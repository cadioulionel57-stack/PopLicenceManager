from modules.modele_fiche_manager import ModeleFicheManager
from modules.parametre_manager import ParametreManager


class GenerateurFicheHtml:
    """
    Génère le HTML complet d'une fiche produit à partir du
    modèle actif (catégorie site + type de produit) et des
    informations du produit — remplace les variables
    {{...}} du modèle par les vraies valeurs.
    """

    @staticmethod
    def reglages_globaux():
        """
        Réglages communs à toutes les catégories (pas
        propres à une seule) — modifiables sans toucher aux
        modèles eux-mêmes.
        """

        parametres = ParametreManager()

        return {
            "prix_emballage_cadeau": parametres.obtenir_nombre(
                "prix_emballage_cadeau", 2.90
            ),
            "seuil_livraison_gratuite_stock": parametres.obtenir_nombre(
                "seuil_livraison_gratuite_stock", 49
            ),
            "tarif_livraison_df": parametres.obtenir_nombre(
                "tarif_livraison_df", 7.90
            ),
            "seuil_livraison_gratuite_df": parametres.obtenir_nombre(
                "seuil_livraison_gratuite_df", 79
            ),
            "tarif_mondial_relay": parametres.obtenir_nombre(
                "tarif_mondial_relay", 4.50
            ),
            "seuil_mondial_relay": parametres.obtenir_nombre(
                "seuil_mondial_relay", 49
            ),
            "tarif_colissimo": parametres.obtenir_nombre(
                "tarif_colissimo", 5.90
            ),
            "seuil_colissimo": parametres.obtenir_nombre(
                "seuil_colissimo", 89
            ),
            "tarif_chrono_relais": parametres.obtenir_nombre(
                "tarif_chrono_relais", 8.90
            ),
            "seuil_chrono_relais": parametres.obtenir_nombre(
                "seuil_chrono_relais", 149
            ),
        }

    @staticmethod
    def generer(produit, licence_nom=None):
        """
        Renvoie le HTML final, ou None si aucun modèle actif
        n'existe pour cette catégorie+type de produit.
        """

        if produit["categorie_site_id"] is None:
            return None

        modele = ModeleFicheManager().obtenir_actif(
            produit["categorie_site_id"], produit["type_produit"]
        )

        if modele is None:
            return None

        html = modele["html_template"]

        nom_produit = produit["nom"] or ""

        avec_licence = f" sous licence {licence_nom}" if licence_nom else ""

        reglages = GenerateurFicheHtml.reglages_globaux()

        variables = {
            "nom_produit": nom_produit,
            "avec_licence": avec_licence,
            "image_fond_univers": produit["image_ambiance"] or "",
            "prix_emballage_cadeau": f"{reglages['prix_emballage_cadeau']:.2f}",
            "seuil_livraison_gratuite_stock": f"{reglages['seuil_livraison_gratuite_stock']:.0f}",
            "tarif_livraison_df": f"{reglages['tarif_livraison_df']:.2f}",
            "seuil_livraison_gratuite_df": f"{reglages['seuil_livraison_gratuite_df']:.0f}",
            "tarif_mondial_relay": f"{reglages['tarif_mondial_relay']:.2f}",
            "seuil_mondial_relay": f"{reglages['seuil_mondial_relay']:.0f}",
            "tarif_colissimo": f"{reglages['tarif_colissimo']:.2f}",
            "seuil_colissimo": f"{reglages['seuil_colissimo']:.0f}",
            "tarif_chrono_relais": f"{reglages['tarif_chrono_relais']:.2f}",
            "seuil_chrono_relais": f"{reglages['seuil_chrono_relais']:.0f}",
        }

        for cle, valeur in variables.items():
            html = html.replace("{{" + cle + "}}", str(valeur))

        return html