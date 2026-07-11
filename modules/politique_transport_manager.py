from modules.canal_manager import CanalManager


class PolitiqueTransportManager:
    """
    Génère un résumé en langage clair de la politique de
    frais de port mise en place sur chaque canal de vente —
    pense comme un pense-bête, pas comme un écran de
    configuration (pour modifier les réglages, ça reste
    Canaux de vente).
    """

    def __init__(self):

        self.canaux = CanalManager()

    def description_canal(self, canal_id):
        """
        Renvoie une liste de lignes (texte) décrivant la
        politique de transport de ce canal.
        """

        canal = self.canaux.obtenir(canal_id)

        if canal is None:
            return ["Canal introuvable."]

        lignes = []

        ##################################################
        # Mécanisme principal
        ##################################################

        if canal["utilise_grille_fba"]:

            lignes.append(
                "📦 Transport géré par la grille FBA "
                "d'Amazon : tarif fixé par Amazon selon le "
                "gabarit du colis, payé par le client à "
                "l'achat."
            )

        elif canal["grille_tarif_client_active"]:

            lignes.append(
                "🔀 Plusieurs transporteurs possibles — le "
                "logiciel choisit automatiquement celui "
                "éligible selon le prix de vente du produit :"
            )

            transporteurs = self.canaux.transporteurs_autorises(
                canal_id
            )

            for transporteur in transporteurs:

                prix_min = transporteur["prix_min_ttc"]
                prix_max = transporteur["prix_max_ttc"]

                if prix_min is None and prix_max is None:
                    tranche = "toutes tranches de prix"
                elif prix_min is None:
                    tranche = f"jusqu'à {prix_max:.0f}€"
                elif prix_max is None:
                    tranche = f"à partir de {prix_min:.0f}€"
                else:
                    tranche = f"de {prix_min:.0f}€ à {prix_max:.0f}€"

                lignes.append(
                    f"   • {transporteur['transporteur']} "
                    f"({transporteur['offre']}) — {tranche} "
                    f"(tarif client variable selon le poids)"
                )

        elif canal["port_inclus"]:

            lignes.append(
                "🎁 Frais de port intégralement inclus dans "
                "le prix (coût réel du transporteur le moins "
                "cher, variable selon le poids). Le client "
                "voit \"livraison gratuite\"."
            )

        elif canal["tarif_port_client_ttc"]:

            lignes.append(
                f"💳 Port facturé séparément au client : "
                f"{canal['tarif_port_client_ttc']:.2f}€ TTC "
                f"fixe (écart avec le coût réel absorbé dans "
                f"le prix)."
            )

        ##################################################
        # Contribution fixe (si utilisée en plus)
        ##################################################

        if canal["contribution_transport_min_ht"]:

            lignes.append(
                f"➕ Contribution transport fixe intégrée à "
                f"chaque produit, quel que soit son poids : "
                f"{canal['contribution_transport_min_ht']:.2f}€ HT."
            )

        if (
            canal["tarif_port_client_ttc"] == 0
            and canal["contribution_transport_min_ht"]
        ):

            lignes.append(
                "🆓 Port affiché gratuit au client (coût "
                "absorbé via la contribution ci-dessus)."
            )

        ##################################################
        # Seuil de gratuité informatif
        ##################################################

        if canal["seuil_gratuite_ttc"]:

            lignes.append(
                f"🎯 Livraison gratuite dès "
                f"{canal['seuil_gratuite_ttc']:.2f}€ de "
                f"commande."
            )

        ##################################################
        # Prix de vente minimum recommandé
        ##################################################

        if canal["prix_vente_min_ttc"]:

            lignes.append(
                f"⚠ Prix de vente minimum recommandé sur ce "
                f"canal : {canal['prix_vente_min_ttc']:.2f}€ "
                f"TTC (alerte rouge sur la fiche produit si "
                f"le prix calculé est en dessous)."
            )

        ##################################################
        # Frais de gestion par palier de prix
        ##################################################

        paliers = self.canaux.paliers_frais_gestion(canal_id)

        if paliers:

            lignes.append(
                "📊 Frais de gestion par palier de prix de "
                "vente :"
            )

            for palier in paliers:

                if palier["seuil_prix_max"] is None:
                    seuil = "au-delà"
                else:
                    seuil = f"jusqu'à {palier['seuil_prix_max']:.0f}€"

                lignes.append(
                    f"   • {seuil} : "
                    f"{palier['frais_gestion_ht']:.2f}€ HT"
                )

        ##################################################
        # Rien de configuré
        ##################################################

        if not lignes:

            lignes.append(
                "Aucune règle de transport spécifique "
                "configurée pour ce canal — le coût de "
                "transport n'est pas pris en compte dans le "
                "calcul de marge sur ce canal."
            )

        return lignes

    def tous(self):
        """
        Renvoie {canal: {nom, commission, lignes}} pour
        tous les canaux actifs, prêt à afficher.
        """

        resultat = []

        for canal in self.canaux.tous():

            resultat.append({
                "id": canal["id"],
                "nom": canal["nom"],
                "commission": canal["commission_pourcentage"],
                "lignes": self.description_canal(canal["id"]),
            })

        return resultat