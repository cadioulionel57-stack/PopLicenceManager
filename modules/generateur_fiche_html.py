import re
import sqlite3
from pathlib import Path

from modules.modele_fiche_manager import ModeleFicheManager
from modules.parametre_manager import ParametreManager
from modules.bloc_livraison_manager import BlocLivraisonManager
from modules.bloc_emballage_cadeau_manager import BlocEmballageCadeauManager
from modules import grilles_tailles


class GenerateurFicheHtml:
    """
    Génère le HTML complet d'une fiche produit à partir du
    modèle actif et des informations du produit.
    """

    CHAMPS_CONDITIONNELS = [
        "composition_matiere",
        "instructions_entretien",
        "coupe_type",
        "type_manche",

        "matiere",
        "couleur",
        "age_minimum",
        "pays_fabrication",

        "age_conseille",
        "nombre_joueurs",
        "duree_partie",
        "contenu_boite",
        "nombre_pieces",
        "taille_literie",
        "contenance",
        "type_alimentation",
        "format_cartes",
        "nombre_cartes",
        "date_sortie_precommande",
        "remise_precommande",
        "contenu_bundle",
        "date_fin_vente_flash",
    ]

    CHAMPS_BOOLEENS_CONDITIONNELS = [
        "compatible_lave_vaisselle",
    ]

    @staticmethod
    def _poids_lisible(poids):
        """
        0.24 -> "240 g" ; 1.5 -> "1,5 kg".
        """

        try:
            valeur = float(poids)
        except (TypeError, ValueError):
            return ""

        if valeur <= 0:
            return ""

        if valeur < 1:
            return f"{int(round(valeur * 1000))} g"

        texte = f"{valeur:.1f}".replace(".", ",")
        texte = texte.rstrip("0").rstrip(",")

        return f"{texte} kg"

    @staticmethod
    def _tableau_tailles(produit):
        """
        Tableau des tailles reduit aux seules tailles vendues
        sur cette fiche. Vide si le produit n'a aucune
        variation de taille reconnue.
        """

        try:
            identifiant = produit["id"]
        except (KeyError, IndexError, TypeError):
            return ""

        if not identifiant:
            return ""

        chemin = (
            Path(__file__).parent.parent
            / "database" / "poplicence.db"
        )

        try:
            connexion = sqlite3.connect(str(chemin))

            lignes = connexion.execute(
                "SELECT libelle FROM produits_variations "
                "WHERE produit_id = ? AND actif = 1 "
                "ORDER BY ordre, id",
                (identifiant,)
            ).fetchall()

            connexion.close()

        except sqlite3.Error:
            return ""

        libelles = [ligne[0] for ligne in lignes if ligne[0]]

        if not libelles:
            return ""

        coupe = GenerateurFicheHtml._valeur_champ(produit, "coupe_type")

        return grilles_tailles.tableau_html(libelles, coupe)

    @staticmethod
    def _paragraphes(texte):
        """
        Met en forme le texte ecrit sur le produit : chaque
        paragraphe recoit sa propre balise et son espacement.

        Une ligne vide separe deux paragraphes. Un titre
        s'ecrit entre deux doubles diese : ## Mon titre ##.
        Une ligne qui commence par un tiret devient un point
        de liste. Les deux sont reconnus meme au milieu d'une
        ligne, donc un texte colle d'un seul tenant sort aussi
        bien mis en page qu'un texte aere.
        """

        if not texte:
            return ""

        style_titre = (
            "margin:26px 0 10px 0;"
            "font-size:18px;"
            "color:#0f172a !important;"
            "font-weight:900;"
        )

        style_para = (
            "margin:0 0 16px 0;"
            "font-size:15px;"
            "line-height:1.9;"
            "color:#475569 !important;"
        )

        style_liste = (
            "margin:0 0 16px 0;"
            "padding-left:18px;"
            "font-size:15px;"
            "line-height:2;"
            "color:#475569 !important;"
        )

        sortie = []

        def _ajouter_texte(morceau):
            """
            Decoupe un morceau de texte en paragraphes et en
            listes, puis les ajoute a la sortie.

            Une ligne qui commence par un tiret devient un
            point de liste. Le tiret est reconnu meme au
            milieu d'une ligne, donc une liste collee d'un
            seul tenant ressort quand meme en liste.
            """

            for bloc in re.split(r"\n\s*\n", morceau):

                if not bloc.strip():
                    continue

                # Un bloc qui contient des tirets en debut de
                # ligne, ou " - " au fil du texte, est une liste.
                puces = [
                    point.strip()
                    for point in re.split(r"(?:^|\s)-\s+", bloc)
                    if point.strip()
                ]

                # Deux tirets au minimum : un tiret isole au
                # fil d'une phrase ne doit pas faire une liste.
                est_liste = (
                    len(re.findall(r"(?:^|\s)-\s+", bloc)) >= 2
                )

                if est_liste:

                    # Ce qui precede le premier tiret reste du
                    # texte normal.
                    avant = re.split(r"(?:^|\s)-\s+", bloc)[0].strip()

                    if avant:
                        sortie.append(
                            "<p style=\"" + style_para + "\">"
                            + avant
                            + "</p>"
                        )
                        puces = puces[1:]

                    if puces:
                        sortie.append(
                            "<ul style=\"" + style_liste + "\">"
                            + "".join(
                                "<li>" + point.replace("\n", " ") + "</li>"
                                for point in puces
                            )
                            + "</ul>"
                        )

                    continue

                lignes = [
                    ligne.strip()
                    for ligne in bloc.split("\n")
                    if ligne.strip()
                ]

                if not lignes:
                    continue

                sortie.append(
                    "<p style=\"" + style_para + "\">"
                    + "<br>".join(lignes)
                    + "</p>"
                )

        # Les titres encadres : ## Mon titre ##
        parties = re.split(r"##\s*(.+?)\s*##", str(texte))

        for rang, partie in enumerate(parties):

            if not partie or not partie.strip():
                continue

            # Les rangs impairs sont les titres captures.
            if rang % 2 == 1:
                sortie.append(
                    "<h3 style=\"" + style_titre + "\">"
                    + partie.strip()
                    + "</h3>"
                )
            else:
                _ajouter_texte(partie)

        return "\n        ".join(sortie)

    @staticmethod
    def _lien_licence(licence_nom):
        """
        Fabrique l'adresse de la page marque du site a partir
        du nom de la licence : "Stranger Things" devient
        "/m/stranger-things/".
        """

        if not licence_nom:
            return ""

        import unicodedata

        normalise = unicodedata.normalize("NFKD", str(licence_nom))
        sans_accents = normalise.encode("ascii", "ignore").decode()

        slug = re.sub(r"[^a-z0-9]+", "-", sans_accents.lower())
        slug = slug.strip("-")

        if not slug:
            return ""

        return f"/m/{slug}/"

    @staticmethod
    def _dimensions_lisibles(longueur, largeur, hauteur):
        """
        Renvoie "30 x 15,5 x 10 cm".
        """

        mesures = []

        for valeur in (hauteur, longueur, largeur):

            try:
                nombre = float(valeur)
            except (TypeError, ValueError):
                continue

            if nombre <= 0:
                continue

            texte = f"{nombre:.1f}".replace(".", ",")
            texte = texte.rstrip("0").rstrip(",")

            mesures.append(texte)

        if len(mesures) < 2:
            return ""

        return " x ".join(mesures) + " cm"

    @staticmethod
    def reglages_globaux():
        """
        Réglages communs à toutes les catégories.
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
        Traite les blocs {{#nom_tag}}...{{/nom_tag}} :
        si condition_vraie, garde le contenu sans les balises ;
        sinon retire tout le bloc.

        ATTENTION : un meme bloc peut en contenir un autre du
        MEME nom. On compte donc la profondeur, comme pour des
        parentheses, sinon des balises orphelines s'affichent
        en clair sur la fiche.
        """

        ouverture = "{{#" + nom_tag + "}}"
        fermeture = "{{/" + nom_tag + "}}"

        while True:

            debut = html.find(ouverture)

            if debut == -1:
                return html

            profondeur = 0
            position = debut
            fin = -1

            while position < len(html):

                suivante_o = html.find(ouverture, position)
                suivante_f = html.find(fermeture, position)

                if suivante_f == -1:
                    break

                if suivante_o != -1 and suivante_o < suivante_f:
                    profondeur += 1
                    position = suivante_o + len(ouverture)
                    continue

                profondeur -= 1

                if profondeur == 0:
                    fin = suivante_f
                    break

                position = suivante_f + len(fermeture)

            if fin == -1:
                html = html.replace(ouverture, "", 1)
                continue

            interieur = html[debut + len(ouverture): fin]

            remplacement = interieur if condition_vraie else ""

            html = (
                html[:debut]
                + remplacement
                + html[fin + len(fermeture):]
            )

        return html

    @staticmethod
    def _valeur_champ(produit, champ):
        """
        Lit produit[champ] de façon sûre, que produit soit un
        dict classique ou un sqlite3.Row.
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
        """

        gestionnaire = ModeleFicheManager()

        modele = None
        periode = None

        try:

            from modules.regle_template_manager import (
                RegleTemplateManager
            )

            gestionnaire_regles = RegleTemplateManager()

            decision = gestionnaire_regles.template_pour(produit["id"])

            if decision["origine"] == "regle":

                impose = gestionnaire.obtenir(
                    decision["modele_fiche_id"]
                )

                if impose is not None and impose["actif"]:

                    modele = impose

                    for regle in gestionnaire_regles.regles_en_cours():

                        if regle["modele_fiche_id"] == impose["id"]:
                            periode = regle
                            break

        except Exception:
            modele = None
            periode = None

        if modele is None and produit["modele_fiche_id"] is not None:

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

        type_du_produit = GenerateurFicheHtml._valeur_champ(
            produit, "type_produit"
        )

        expedie_par_nous = type_du_produit in ("stock", "bundle")

        conditions_par_type = {
            "si_stock": expedie_par_nous,
            "si_dropshipping": type_du_produit == "dropshipping",
            "si_precommande": type_du_produit == "precommande",
            "si_bundle": type_du_produit == "bundle",
        }

        for nom_bloc, condition in conditions_par_type.items():
            html = GenerateurFicheHtml._traiter_bloc_conditionnel(
                html, nom_bloc, condition
            )

        emballage_cadeau_possible = (
            bool(produit["eligible_papier_cadeau"])
            and expedie_par_nous
        )

        html = GenerateurFicheHtml._traiter_bloc_conditionnel(
            html, "si_emballage_cadeau", emballage_cadeau_possible
        )

        valeurs_champs_conditionnels = {}

        for champ in GenerateurFicheHtml.CHAMPS_CONDITIONNELS:

            valeur = GenerateurFicheHtml._valeur_champ(produit, champ)
            valeurs_champs_conditionnels[champ] = valeur

            html = GenerateurFicheHtml._traiter_bloc_conditionnel(
                html, f"si_{champ}", bool(str(valeur).strip())
            )

        for champ in GenerateurFicheHtml.CHAMPS_BOOLEENS_CONDITIONNELS:

            valeur_brute = GenerateurFicheHtml._valeur_champ(produit, champ)

            html = GenerateurFicheHtml._traiter_bloc_conditionnel(
                html, f"si_{champ}", bool(valeur_brute)
            )

        nom_produit = produit["nom"] or ""

        avec_licence = f" sous licence {licence_nom}" if licence_nom else ""

        poids_lisible = GenerateurFicheHtml._poids_lisible(
            GenerateurFicheHtml._valeur_champ(produit, "poids")
        )

        dimensions = GenerateurFicheHtml._dimensions_lisibles(
            GenerateurFicheHtml._valeur_champ(produit, "longueur"),
            GenerateurFicheHtml._valeur_champ(produit, "largeur"),
            GenerateurFicheHtml._valeur_champ(produit, "hauteur"),
        )

        lien_licence = GenerateurFicheHtml._lien_licence(licence_nom)

        image_univers = GenerateurFicheHtml._valeur_champ(
            produit, "image_ambiance"
        )

        # Texte alternatif de la banniere.
        alt_univers = nom_produit

        if licence_nom and licence_nom.lower() not in nom_produit.lower():
            alt_univers = f"{nom_produit}, univers {licence_nom}"

        # Le texte propre au produit, ecrit a la main dans
        # le champ "Description longue" du logiciel.
        description_specifique = GenerateurFicheHtml._paragraphes(
            GenerateurFicheHtml._valeur_champ(produit, "description_longue")
        )

        # Le tableau des tailles, reduit aux tailles vendues.
        tableau_tailles = GenerateurFicheHtml._tableau_tailles(produit)

        for nom_bloc, valeur in (
            ("si_poids", poids_lisible),
            ("si_dimensions", dimensions),
            ("si_licence", lien_licence),
            ("si_image_univers", image_univers),
            ("si_description_specifique", description_specifique),
            ("si_tableau_tailles", tableau_tailles),
        ):
            html = GenerateurFicheHtml._traiter_bloc_conditionnel(
                html, nom_bloc, bool(valeur)
            )

        reglages = GenerateurFicheHtml.reglages_globaux()

        bloc_emballage_cadeau = ""

        if emballage_cadeau_possible:

            bloc_emballage_cadeau = (
                BlocEmballageCadeauManager().obtenir().replace(
                    "{{prix_emballage_cadeau}}",
                    f"{reglages['prix_emballage_cadeau']:.2f}"
                )
            )

        from modules.regle_template_manager import normaliser_date

        def _fr(valeur):

            iso = normaliser_date(valeur)

            if len(iso) != 10:
                return ""

            return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"

        html = GenerateurFicheHtml._traiter_bloc_conditionnel(
            html, "si_periode", periode is not None
        )

        bloc_livraison = BlocLivraisonManager().obtenir()

        for cle in (
            "tarif_livraison_df",
            "seuil_livraison_gratuite_df",
            "seuil_livraison_gratuite_stock",
            "tarif_mondial_relay",
            "seuil_mondial_relay",
            "tarif_colissimo",
            "seuil_colissimo",
            "tarif_chrono_relais",
            "seuil_chrono_relais",
        ):
            decimales = 0 if cle.startswith("seuil") else 2

            bloc_livraison = bloc_livraison.replace(
                "{{" + cle + "}}",
                f"{reglages[cle]:.{decimales}f}"
            )

        variables = {
            "bloc_livraison": bloc_livraison,
            "periode_nom": (
                periode["nom_periode"] if periode else ""
            ),
            "periode_debut": (
                _fr(periode["date_debut"]) if periode else ""
            ),
            "periode_fin": (
                _fr(periode["date_fin"]) if periode else ""
            ),
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

        variables["poids_lisible"] = poids_lisible
        variables["dimensions"] = dimensions
        variables["lien_licence"] = lien_licence
        variables["licence"] = licence_nom or ""
        variables["alt_univers"] = alt_univers
        variables["description_specifique"] = description_specifique
        variables["tableau_tailles"] = tableau_tailles

        variables.update(valeurs_champs_conditionnels)

        for cle, valeur in variables.items():
            html = html.replace("{{" + cle + "}}", str(valeur))

        return html