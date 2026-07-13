import re

from modules.modele_fiche_manager import ModeleFicheManager
from modules.parametre_manager import ParametreManager
from modules.bloc_emballage_cadeau_manager import BlocEmballageCadeauManager


class GenerateurFicheHtml:
    """
    Génère le HTML complet d'une fiche produit à partir du
    modèle actif (catégorie site + type de produit) et des
    informations du produit — remplace les variables
    {{...}} du modèle par les vraies valeurs.
    """

    # Champs "optionnels" du produit : si l'un de ces champs
    # n'est pas renseigné sur la fiche produit, le bloc
    # {{#si_<champ>}}...{{/si_<champ>}} correspondant dans le
    # template est retiré entièrement de la fiche publiée
    # (au lieu d'afficher une section vide ou une variable
    # brute {{...}} non remplacée). Ajouter un nom ici suffit
    # à activer ce comportement pour un nouveau champ, sans
    # toucher au reste du moteur.
    CHAMPS_CONDITIONNELS = [
        "age_conseille",
        "nombre_joueurs",
        "duree_partie",
        "contenu_boite",
        "nombre_pieces",
        "taille_literie",
        "contenance",
        "type_alimentation",
    ]

    # Champs "oui/non" (case à cocher, stockés en 0/1) : la
    # section {{#si_<champ>}}...{{/si_<champ>}} ne s'affiche
    # que si la case est cochée (valeur = 1). Contrairement à
    # CHAMPS_CONDITIONNELS ci-dessus, il n'y a pas de variable
    # {{<champ>}} à substituer à l'intérieur — juste un bloc à
    # montrer ou masquer.
    CHAMPS_BOOLEENS_CONDITIONNELS = [
        "compatible_lave_vaisselle",
    ]

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
    def _traiter_bloc_conditionnel(html, nom_tag, condition_vraie):
        """
        Traite un bloc générique {{#nom_tag}}...{{/nom_tag}} :
        si condition_vraie, garde le contenu (sans les
        balises) ; sinon, retire tout le bloc — pour ne
        montrer une section que lorsqu'elle est réellement
        renseignée/éligible sur le produit.

        Généralisé à partir de l'ancienne fonction qui ne
        gérait que "si_emballage_cadeau" en dur : n'importe
        quel nom_tag fonctionne désormais avec le même
        mécanisme.
        """

        motif = re.compile(
            r"\{\{#" + re.escape(nom_tag) + r"\}\}(.*?)\{\{/" + re.escape(nom_tag) + r"\}\}",
            re.DOTALL
        )

        if condition_vraie:
            return motif.sub(r"\1", html)

        return motif.sub("", html)

    @staticmethod
    def _valeur_champ(produit, champ):
        """
        Lit produit[champ] de façon sûre, que produit soit un
        dict classique ou un sqlite3.Row (qui n'a pas de
        .get()) — renvoie "" si le champ n'existe pas encore
        en base (ex: avant une migration du schéma) ou si sa
        valeur est None.
        """

        try:
            valeur = produit[champ]
        except (KeyError, IndexError):
            return ""

        return valeur if valeur is not None else ""

    @staticmethod
    def generer(produit, licence_nom=None):
        """
        Renvoie le HTML final, ou None si aucun modèle n'est
        disponible pour ce produit.

        Le produit garde en mémoire le modèle choisi
        directement sur sa fiche (produit["modele_fiche_id"]).
        S'il est toujours actif, il est utilisé tel quel.
        S'il a depuis été désactivé (un autre modèle du même
        thème est devenu actif — bascule saisonnière type
        Noël), le produit suit automatiquement le nouveau
        modèle actif du même thème, sans rien à changer sur
        sa fiche.
        """

        gestionnaire = ModeleFicheManager()

        modele = None

        if produit["modele_fiche_id"] is not None:

            choisi = gestionnaire.obtenir(produit["modele_fiche_id"])

            if choisi is not None:

                if choisi["actif"]:
                    modele = choisi
                else:
                    modele = gestionnaire.obtenir_actif(
                        choisi["theme_id"], produit["type_produit"]
                    )

        if modele is None:
            return None

        html = modele["html_template"]

        # La section "Emballage cadeau" ne doit apparaître
        # que si le produit y est réellement éligible (pas
        # les vélos, trottinettes, objets volumineux...).
        html = GenerateurFicheHtml._traiter_bloc_conditionnel(
            html, "si_emballage_cadeau", bool(produit["eligible_papier_cadeau"])
        )

        # Champs optionnels génériques (âge conseillé, nombre
        # de joueurs, durée de partie, contenu de la boîte,
        # nombre de pièces, contenance...) : la section
        # correspondante ne s'affiche que si le champ est
        # réellement renseigné sur la fiche produit.
        valeurs_champs_conditionnels = {}

        for champ in GenerateurFicheHtml.CHAMPS_CONDITIONNELS:

            valeur = GenerateurFicheHtml._valeur_champ(produit, champ)
            valeurs_champs_conditionnels[champ] = valeur

            html = GenerateurFicheHtml._traiter_bloc_conditionnel(
                html, f"si_{champ}", bool(str(valeur).strip())
            )

        # Champs "oui/non" (case à cocher) : la section ne
        # s'affiche que si la case est cochée (1), pas selon
        # qu'une valeur texte soit renseignée.
        for champ in GenerateurFicheHtml.CHAMPS_BOOLEENS_CONDITIONNELS:

            valeur_brute = GenerateurFicheHtml._valeur_champ(produit, champ)

            html = GenerateurFicheHtml._traiter_bloc_conditionnel(
                html, f"si_{champ}", bool(valeur_brute)
            )

        nom_produit = produit["nom"] or ""

        avec_licence = f" sous licence {licence_nom}" if licence_nom else ""

        reglages = GenerateurFicheHtml.reglages_globaux()

        # Bloc réutilisable "éligible emballage cadeau" —
        # vide si le produit n'y est pas éligible, sinon le
        # badge (avec son propre prix substitué).
        bloc_emballage_cadeau = ""

        if produit["eligible_papier_cadeau"]:

            bloc_emballage_cadeau = (
                BlocEmballageCadeauManager().obtenir().replace(
                    "{{prix_emballage_cadeau}}",
                    f"{reglages['prix_emballage_cadeau']:.2f}"
                )
            )

        variables = {
            "nom_produit": nom_produit,
            "avec_licence": avec_licence,
            "image_fond_univers": produit["image_ambiance"] or "",
            "bloc_emballage_cadeau": bloc_emballage_cadeau,
            "composition_matiere": produit["composition_matiere"] or "",
            "instructions_entretien": produit["instructions_entretien"] or "",
            "coupe_type": produit["coupe_type"] or "",
            "type_manche": produit["type_manche"] or "",
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

        # Ajoute les valeurs des champs conditionnels
        # (age_conseille, nombre_joueurs, duree_partie,
        # contenu_boite, nombre_pieces...) au dictionnaire de
        # remplacement, pour que {{age_conseille}} etc. dans
        # le texte du bloc conditionnel soit bien remplacé et
        # ne s'affiche jamais en texte brut non substitué.
        variables.update(valeurs_champs_conditionnels)

        for cle, valeur in variables.items():
            html = html.replace("{{" + cle + "}}", str(valeur))

        return html