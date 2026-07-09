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

        # 1. Coût produit. L'emballage n'est compté que si
        #    c'est TOI qui expédies (FBM, Site...) — pas en
        #    FBA, où c'est Amazon qui gère l'emballage dans
        #    ses propres entrepôts. L'emballage choisi sur
        #    la fiche produit elle-même prime toujours sur
        #    celui de la famille (plus précis, adapté aux
        #    dimensions/poids réels de ce produit).
        emballage_id_produit = (
            produit["emballage_id"]
            if "emballage_id" in produit.keys()
            else None
        )

        cout_produit = self.familles.cout_produit(
            famille_id,
            prix_achat_ht,
            inclure_emballage=not canal["utilise_grille_fba"],
            emballage_id_produit=emballage_id_produit,
        )

        # 2. Frais fixes du canal + contribution transport
        #    minimale (si définie pour ce canal) — ajoutée
        #    systématiquement, sans condition, en plus de
        #    l'écart transport calculé plus bas.
        cout_fixe = (
            cout_produit
            + (canal["frais_fixe_ht"] or 0)
            + (canal["contribution_transport_min_ht"] or 0)
        )

        # 3. Transport, uniquement si inclus dans le prix.
        #    Deux façons de le calculer selon le canal :
        #    - grille FBA (format de colis + poids), si le
        #      canal est marqué "utilise_grille_fba"
        #    - grille transporteurs classique (Boxtal) sinon,
        #      qui choisit automatiquement le moins cher
        #      parmi les transporteurs autorisés
        transport = None

        if canal["grille_tarif_client_active"]:

            # Cas Fnac : plusieurs transporteurs possibles,
            # chacun éligible sur une tranche de prix de
            # vente différente, avec un tarif client propre
            # par poids. Comme le prix dépend du transport
            # choisi, et le transport dépend du prix, on
            # itère jusqu'à 3 fois (même principe que la
            # résolution de commission par paliers).
            resolution = None
            cout_fixe_avec_transport = cout_fixe

            for _ in range(3):

                commission_estimee = self._resoudre_commission(
                    categorie_id, canal, cout_fixe_avec_transport, marge
                )

                commission_est = (
                    (commission_estimee / 100) * (1 + self.TAUX_TVA)
                )

                taux_tsn_est = (
                    (canal["taux_tsn_pourcentage"] or 0) / 100
                )
                taux_paiement_est = (
                    (canal["frais_paiement_pourcentage"] or 0) / 100
                    * (1 + self.TAUX_TVA)
                )

                denominateur_est = (
                    1 - marge - commission_est
                    - taux_paiement_est
                    - (taux_tsn_est * commission_est)
                )

                if denominateur_est <= 0:
                    resolution = None
                    break

                prix_estime_ht = (
                    cout_fixe_avec_transport / denominateur_est
                )
                prix_estime_ttc = prix_estime_ht * (1 + self.TAUX_TVA)

                nouvelle_resolution = self.canaux.transport_eligible_prix(
                    canal_id, poids, prix_estime_ttc
                )

                if nouvelle_resolution is None:
                    resolution = None
                    break

                tarif_client_ht_test = (
                    nouvelle_resolution["tarif_client_ttc"]
                    / (1 + self.TAUX_TVA)
                )
                ecart_test = (
                    nouvelle_resolution["prix_ht"] - tarif_client_ht_test
                )
                nouveau_cout_fixe = cout_fixe + ecart_test

                meme_transporteur = (
                    resolution is not None
                    and resolution["offre"] == nouvelle_resolution["offre"]
                    and resolution["transporteur_id"]
                    == nouvelle_resolution["transporteur_id"]
                )

                resolution = nouvelle_resolution
                cout_fixe_avec_transport = nouveau_cout_fixe

                if meme_transporteur:
                    break

            if resolution is None:

                return {
                    "erreur": (
                        "Aucun transporteur éligible pour ce "
                        "produit sur ce canal : prix de vente "
                        "hors des tranches définies (trop bas ou "
                        "trop élevé), ou poids au-delà de ce que "
                        "couvre la grille."
                    )
                }

            tarif_client_ht = (
                resolution["tarif_client_ttc"] / (1 + self.TAUX_TVA)
            )
            ecart = resolution["prix_ht"] - tarif_client_ht

            cout_fixe += ecart

            transport = {
                "transporteur": resolution["transporteur"],
                "offre": resolution["offre"],
                "prix_ht": resolution["prix_ht"],
                "tarif_facture_client_ttc": resolution["tarif_client_ttc"],
                "ecart_absorbe_ht": round(ecart, 2),
            }

        elif canal["port_inclus"]:

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

        elif canal["tarif_port_client_ttc"]:

            # Cas FBM : le client paie un frais de port
            # séparé, mais fixé par toi — pas forcément égal
            # au vrai coût transporteur. Seul l'écart entre
            # les deux s'ajoute au coût du produit.
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

            tarif_client_ht = (
                canal["tarif_port_client_ttc"] / (1 + self.TAUX_TVA)
            )

            ecart = transport["prix_ht"] - tarif_client_ht

            cout_fixe += ecart

            transport = {
                "transporteur": transport["transporteur"],
                "offre": transport["offre"],
                "prix_ht": transport["prix_ht"],
                "tarif_facture_client_ttc": canal["tarif_port_client_ttc"],
                "ecart_absorbe_ht": round(ecart, 2),
            }

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

            # Si seul un écart est absorbé (cas FBM), c'est
            # cet écart qui pèse réellement sur ton prix —
            # pas le coût total du transport, dont une
            # partie est payée par le client.
            valeur_pesant_sur_le_prix = transport.get(
                "ecart_absorbe_ht", transport["prix_ht"]
            )

            ratio_transport = round(
                (valeur_pesant_sur_le_prix / prix_vente_ht) * 100, 1
            )

            if ratio_transport > seuil_transport_max:

                decision = (
                    f"❌ Transport trop élevé "
                    f"({ratio_transport}% > "
                    f"{seuil_transport_max}%)"
                )

        # Alerte prix de vente minimum recommandé pour ce
        # canal (zone grise structurelle : port + commission
        # trop lourds face à un prix trop bas). Purement
        # indicatif — ne bloque pas l'enregistrement, mais
        # prime sur le message précédent si les deux se
        # déclenchent, car c'est le signal le plus direct
        # pour décider d'un autre canal (ex : FBA).
        prix_min = canal["prix_vente_min_ttc"]

        if prix_min is not None and prix_vente_ttc < prix_min:

            decision = (
                f"❌ Prix sous le seuil recommandé pour ce "
                f"canal ({prix_vente_ttc:.2f}€ < {prix_min:.2f}€)"
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