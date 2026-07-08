from database.database import Database
from modules.famille_produit_manager import FamilleProduitManager
from modules.categorie_manager import CategorieManager
from modules.canal_manager import CanalManager
from modules.parametre_manager import ParametreManager
from modules.grille_fba_manager import GrilleFbaManager


class MoteurPrix:
    """
    Calcule le prix de vente d'un produit sur un canal
    donné, à partir de ses coûts directs réels (méthode
    "coût variable" / marge de contribution — les charges
    de structure comme les abonnements logiciels globaux
    ou l'assurance d'entreprise ne sont volontairement pas
    incluses ici).

    Formule :

    Coût direct total = Coût produit (achat+emballage+retour)
                       + Frais fixes du canal
                       + Transport (si inclus dans le prix)
                       + Frais de paiement fixes

    PV HT = Coût direct total ÷ (
        1 − Marge visée
          − Commission (canal ou catégorie, avec paliers)
          − Taux de frais de paiement (%)
          − Taux TSN effectif (TSN × commission)
    )

    PV TTC = PV HT × (1 + taux de TVA)
    """

    TAUX_TVA = 0.20

    # Clé de paramètre pour le seuil transport, et valeur
    # de repli si jamais rien n'a encore été réglé.
    CLE_SEUIL_TRANSPORT = "seuil_transport_max_pourcentage"
    SEUIL_TRANSPORT_DEFAUT = 25

    def __init__(self):

        self.db = Database()
        self.familles = FamilleProduitManager()
        self.categories = CategorieManager()
        self.canaux = CanalManager()
        self.parametres = ParametreManager()
        self.grille_fba = GrilleFbaManager()

    def calculer(self, produit, canal_id, categorie_id=None):
        """
        Calcule le détail complet du prix de vente d'un
        produit sur un canal donné.

        produit : dict-like avec au moins prix_fournisseur_ht,
        famille_produit_id, marge_visee_pourcentage, poids

        categorie_id : catégorie du produit sur CE canal
        (vient de produits_categories_canaux), utilisée pour
        la commission si elle en a une propre.

        Renvoie un dictionnaire détaillé, ou un dictionnaire
        avec "erreur" si le calcul est impossible (ex :
        aucun transporteur ne couvre le poids du produit).
        """

        canal = self.canaux.obtenir(canal_id)

        if canal is None:
            return {"erreur": "Canal introuvable"}

        prix_achat_ht = produit["prix_fournisseur_ht"] or 0
        famille_id = produit["famille_produit_id"]
        marge = (produit["marge_visee_pourcentage"] or 0) / 100
        poids = produit["poids"] or 0

        # 1. Coût produit (identique quel que soit le canal)
        cout_produit = self.familles.cout_produit(
            famille_id, prix_achat_ht
        )

        # 2. Frais fixes du canal
        cout_fixe = cout_produit + (canal["frais_fixe_ht"] or 0)

        # 3. Transport, uniquement si inclus dans le prix.
        #    Deux façons de le calculer selon le canal :
        #    - grille FBA (format de colis + poids), si le
        #      canal est marqué "utilise_grille_fba"
        #    - grille transporteurs classique (Boxtal) sinon,
        #      qui choisit automatiquement le moins cher
        #      parmi les transporteurs autorisés
        transport = None

        if canal["port_inclus"]:

            if canal["utilise_grille_fba"]:

                nom_categorie = None

                if categorie_id is not None:

                    categorie = self.categories.obtenir(categorie_id)

                    if categorie is not None:
                        nom_categorie = categorie["nom"]

                # Les dimensions d'expédition (carton plié)
                # priment si renseignées ; sinon on utilise
                # les dimensions du produit tel quel (objets
                # rigides, non pliables).
                longueur_colis = (
                    produit.get("longueur_expedition")
                    or produit.get("longueur")
                )
                largeur_colis = (
                    produit.get("largeur_expedition")
                    or produit.get("largeur")
                )
                hauteur_colis = (
                    produit.get("hauteur_expedition")
                    or produit.get("hauteur")
                )

                resultat_fba = self.grille_fba.tarif(
                    longueur_colis,
                    largeur_colis,
                    hauteur_colis,
                    poids * 1000,
                    categorie_speciale=nom_categorie
                )

                if resultat_fba is None:

                    return {
                        "erreur": (
                            "Aucun format de colis FBA ne "
                            "correspond aux dimensions ou au "
                            "poids de ce produit."
                        )
                    }

                transport = {
                    "transporteur": "Amazon (FBA)",
                    "offre": resultat_fba["format_colis"],
                    "prix_ht": resultat_fba["prix_ht"],
                }

            else:

                transport = self.canaux.transport_le_moins_cher(
                    canal_id, poids
                )

                if transport is None:

                    return {
                        "erreur": (
                            "Aucun transporteur autorisé pour ce "
                            "canal ne couvre ce poids ("
                            f"{poids} kg)"
                        )
                    }

            cout_fixe += transport["prix_ht"]

        # 4. Frais de paiement fixes (ex : 0,35€ PayPal)
        cout_fixe += canal["frais_paiement_fixe_ht"] or 0

        # 5. Commission — calcul itératif si paliers de prix
        #    (la commission peut dépendre du prix de vente,
        #    qui dépend lui-même de la commission). Comme
        #    les frais de paiement, elle est facturée sur
        #    le prix TTC (confirmé : "la commission Amazon
        #    est calculée sur le prix de vente TTC"), donc
        #    on la regonfle avant de l'utiliser dans une
        #    formule qui résout le prix HT.
        commission_pourcentage = self._resoudre_commission(
            categorie_id, canal, cout_fixe, marge
        )

        commission_ttc = commission_pourcentage / 100
        commission = commission_ttc * (1 + self.TAUX_TVA)

        # 6. TSN, calculée sur le montant de la commission
        #    (elle hérite donc aussi de la conversion TTC
        #    ci-dessus, via "commission" déjà regonflée)
        taux_tsn = (canal["taux_tsn_pourcentage"] or 0) / 100
        taux_tsn_effectif = taux_tsn * commission

        # 7. Frais de paiement en pourcentage.
        #    Ils sont facturés sur le prix TTC (le
        #    prestataire de paiement encaisse le montant
        #    payé par le client, TVA comprise), donc on
        #    doit "regonfler" le taux avant de l'inclure
        #    dans une formule qui résout le prix HT.
        taux_paiement_ttc = (canal["frais_paiement_pourcentage"] or 0) / 100
        taux_paiement = taux_paiement_ttc * (1 + self.TAUX_TVA)

        # 8. Dénominateur
        denominateur = (
            1 - marge - commission - taux_paiement - taux_tsn_effectif
        )

        if denominateur <= 0:

            return {
                "erreur": (
                    "Impossible de calculer un prix : la somme "
                    "de la marge, de la commission et des frais "
                    "dépasse 100%. Réduis la marge visée ou "
                    "vérifie la commission de ce canal."
                )
            }

        prix_vente_ht = cout_fixe / denominateur
        prix_vente_ttc = prix_vente_ht * (1 + self.TAUX_TVA)

        # Décision automatique : le transport ne doit pas
        # peser plus que le seuil défini dans le prix de
        # vente final — pas besoin d'étude de marché pour
        # écarter automatiquement les cas déséquilibrés.
        decision = "✅ Recommandé"
        ratio_transport = None

        seuil_transport_max = self.parametres.obtenir_nombre(
            self.CLE_SEUIL_TRANSPORT,
            self.SEUIL_TRANSPORT_DEFAUT
        )

        if transport is not None and prix_vente_ht > 0:

            ratio_transport = round(
                (transport["prix_ht"] / prix_vente_ht) * 100, 1
            )

            if ratio_transport > seuil_transport_max:

                decision = (
                    f"❌ Transport trop élevé "
                    f"({ratio_transport}% > "
                    f"{seuil_transport_max}%)"
                )

        return {
            "erreur": None,
            "cout_produit": round(cout_produit, 2),
            "cout_fixe_total": round(cout_fixe, 2),
            "transport": transport,
            "ratio_transport_pourcentage": ratio_transport,
            "decision": decision,
            "commission_pourcentage": round(commission_pourcentage, 2),
            "taux_tsn_effectif": round(taux_tsn_effectif * 100, 3),
            "taux_paiement_pourcentage": round(taux_paiement_ttc * 100, 2),
            "marge_pourcentage": round(marge * 100, 2),
            "prix_vente_ht": round(prix_vente_ht, 2),
            "prix_vente_ttc": round(prix_vente_ttc, 2),
        }

    def _resoudre_commission(self, categorie_id, canal, cout_fixe, marge):
        """
        Détermine la commission applicable, avec jusqu'à 3
        passes si la catégorie utilise des paliers de prix
        (la commission dépend du prix, qui dépend de la
        commission).
        """

        if categorie_id is None:

            return canal["commission_pourcentage"] or 0

        # Première estimation, sans connaître le prix
        commission_pourcentage = self.categories.commission_effective(
            categorie_id
        )

        if commission_pourcentage is None:
            commission_pourcentage = canal["commission_pourcentage"] or 0

        for _ in range(3):

            commission_ttc = commission_pourcentage / 100
            commission = commission_ttc * (1 + self.TAUX_TVA)

            taux_tsn = (canal["taux_tsn_pourcentage"] or 0) / 100
            taux_paiement = (
                (canal["frais_paiement_pourcentage"] or 0) / 100
                * (1 + self.TAUX_TVA)
            )

            denominateur = (
                1 - marge - commission
                - taux_paiement - (taux_tsn * commission)
            )

            if denominateur <= 0:
                break

            prix_estime_ht = cout_fixe / denominateur

            # Les seuils de palier (ex : "jusqu'à 15€") sont
            # exprimés en prix TTC, comme affichés au client.
            prix_estime_ttc = prix_estime_ht * (1 + self.TAUX_TVA)

            nouvelle_commission = self.categories.commission_effective(
                categorie_id, prix_vente=prix_estime_ttc
            )

            if nouvelle_commission is None:
                nouvelle_commission = canal["commission_pourcentage"] or 0

            if abs(nouvelle_commission - commission_pourcentage) < 0.01:
                commission_pourcentage = nouvelle_commission
                break

            commission_pourcentage = nouvelle_commission

        return commission_pourcentage

    def seuil_rentable(self, produit, canal_id, categorie_id=None):
        """
        Renvoie le prix de vente minimum (marge = 0%) pour
        ce produit sur ce canal — utile pour comparer au
        prix de marché constaté et savoir si le canal est
        viable.
        """

        produit_marge_zero = dict(produit)
        produit_marge_zero["marge_visee_pourcentage"] = 0

        return self.calculer(produit_marge_zero, canal_id, categorie_id)

    def evaluer_tous_canaux(self, produit, categories_par_canal=None):
        """
        Calcule le prix et le seuil de rentabilité du
        produit sur TOUS les canaux de vente actifs
        compatibles avec son type (règle stock/marketplace
        déjà appliquée en amont, dans l'onglet Publication).

        categories_par_canal : {canal_id: categorie_id}

        Renvoie une liste de résultats, un par canal.
        """

        categories_par_canal = categories_par_canal or {}

        resultats = []

        for canal in self.canaux.tous():

            categorie_id = categories_par_canal.get(canal["id"])

            prix = self.calculer(produit, canal["id"], categorie_id)
            seuil = self.seuil_rentable(produit, canal["id"], categorie_id)

            resultats.append({
                "canal_id": canal["id"],
                "canal_nom": canal["nom"],
                "canal_type": canal["type"],
                "prix": prix,
                "seuil_rentable": seuil,
            })

        return resultats