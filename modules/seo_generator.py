import json
import re
import unicodedata


class SeoGenerator:
    """
    Génère automatiquement le contenu SEO d'une fiche
    produit (titre, descriptions, meta description,
    mots-clés, URL, données structurées Schema.org) à
    partir des informations déjà saisies sur le produit.

    Objectif : que le contenu généré soit exploitable tel
    quel à l'export vers WiziShop/Base.com, sans retouche
    systématique — la Description longue reste toutefois
    pensée comme un bon brouillon à enrichir toi-même sur
    les produits les plus importants, pour éviter le
    contenu trop générique d'une fiche à l'autre.

    Toutes les méthodes sont statiques : ce module ne touche
    jamais à la base de données lui-même, il reçoit les
    informations déjà résolues (noms de licence/marque/
    catégorie/famille, pas juste leurs identifiants) et
    renvoie du texte.
    """

    NOM_SITE = "PopLicence"

    LONGUEUR_MAX_TITRE = 60
    LONGUEUR_MAX_DESCRIPTION_COURTE = 160
    LONGUEUR_MAX_META_DESCRIPTION = 155

    @staticmethod
    def _tronquer(texte, longueur_max):
        """
        Coupe proprement sur le dernier espace avant la
        limite, pour ne jamais couper un mot en plein
        milieu.
        """

        if texte is None:
            return ""

        if len(texte) <= longueur_max:
            return texte

        tronque = texte[:longueur_max]

        dernier_espace = tronque.rfind(" ")

        if dernier_espace > 0:
            tronque = tronque[:dernier_espace]

        return tronque.rstrip(" ,.-") + "…"

    @staticmethod
    def _slugifier(texte):
        """
        Convertit un texte en URL propre : minuscules, sans
        accents, espaces remplacés par des tirets, aucun
        caractère spécial.
        """

        if not texte:
            return ""

        normalise = unicodedata.normalize("NFKD", texte)
        sans_accents = normalise.encode("ascii", "ignore").decode("ascii")

        minuscule = sans_accents.lower()

        avec_tirets = re.sub(r"[^a-z0-9]+", "-", minuscule)

        return avec_tirets.strip("-")

    @staticmethod
    def _caracteristique_principale(matiere, couleur):
        """
        Combine matière et couleur en une phrase courte
        naturelle, en gérant les cas où l'une des deux
        manque.
        """

        if matiere and couleur:
            return f"{matiere}, coloris {couleur}"

        if matiere:
            return matiere

        if couleur:
            return f"coloris {couleur}"

        return ""

    @classmethod
    def generer(
        cls,
        nom_produit,
        licence_nom=None,
        marque_nom=None,
        categorie_nom=None,
        famille_nom=None,
        matiere=None,
        couleur=None,
        age_minimum=None,
        pays_fabrication=None,
        ean=None,
        sku=None,
        prix_ttc=None,
    ):
        """
        Génère les 7 champs SEO à partir des informations
        produit disponibles. Renvoie un dictionnaire avec
        les clés : titre_seo, description_courte,
        description_longue, meta_description, mots_cles,
        url_slug, schema_org_json.

        Chaque champ gère l'absence d'informations
        optionnelles (licence, marque, matière...) sans
        jamais produire de texte bancal du type "None" ou
        une virgule seule.
        """

        nom_produit = (nom_produit or "").strip()

        caracteristique = cls._caracteristique_principale(
            matiere, couleur
        )

        ##################################################
        # Titre SEO
        ##################################################

        elements_titre = [nom_produit]

        licence_deja_dans_nom = (
            licence_nom
            and licence_nom.lower() in nom_produit.lower()
        )

        if licence_nom and not licence_deja_dans_nom:
            elements_titre.append(licence_nom)

        titre_seo = " ".join(elements_titre)

        if marque_nom:
            titre_avec_marque = f"{titre_seo} - {marque_nom}"

            if len(titre_avec_marque) <= cls.LONGUEUR_MAX_TITRE:
                titre_seo = titre_avec_marque

        titre_seo = cls._tronquer(titre_seo, cls.LONGUEUR_MAX_TITRE)

        ##################################################
        # Description courte
        ##################################################

        licence_deja_mentionnee = (
            licence_nom
            and licence_nom.lower() in nom_produit.lower()
        )

        phrase_licence = (
            f", licence {licence_nom}"
            if licence_nom and not licence_deja_mentionnee
            else ""
        )

        phrase_caracteristique = (
            f" {caracteristique}." if caracteristique else ""
        )

        description_courte = (
            f"{nom_produit}{phrase_licence}."
            f"{phrase_caracteristique} "
            f"Produit officiel, livraison rapide."
        )

        description_courte = cls._tronquer(
            description_courte.strip(),
            cls.LONGUEUR_MAX_DESCRIPTION_COURTE
        )

        ##################################################
        # Description longue
        ##################################################

        paragraphes = []

        phrase_ouverture = f"Craquez pour {nom_produit}"

        if licence_nom and not licence_deja_mentionnee:
            phrase_ouverture += f", directement inspiré de l'univers {licence_nom}"

        phrase_ouverture += "."

        paragraphes.append(phrase_ouverture)

        if categorie_nom:

            phrase_categorie = "Idéal pour les passionnés de "

            phrase_categorie += categorie_nom.lower()

            phrase_categorie += (
                f", {licence_nom}"
                if licence_nom and not licence_deja_mentionnee
                else ""
            ) + "."

            paragraphes.append(phrase_categorie)

        if caracteristique:
            paragraphes.append(
                f"Caractéristiques : {caracteristique}."
            )

        if age_minimum:
            paragraphes.append(
                f"Convient à partir de {age_minimum} ans."
            )

        if pays_fabrication:
            paragraphes.append(
                f"Fabriqué en {pays_fabrication}."
            )

        paragraphes.append(
            f"{marque_nom + ' chez ' if marque_nom else ''}"
            f"{cls.NOM_SITE}, retrouvez cet article et bien "
            "d'autres produits sous licence officielle. "
            "Commande expédiée rapidement et soigneusement "
            "emballée."
        )

        description_longue = " ".join(paragraphes)

        ##################################################
        # Meta description
        ##################################################

        phrase_prix = f" dès {prix_ttc:.2f}€" if prix_ttc else ""

        meta_description = (
            f"Achetez {nom_produit}"
            f"{' ' + licence_nom if licence_nom and not licence_deja_mentionnee else ''}"
            f"{phrase_prix} chez {cls.NOM_SITE}."
            f"{' ' + caracteristique + '.' if caracteristique else ''} "
            f"Produit officiel, livraison rapide et sécurisée."
        )

        meta_description = cls._tronquer(
            meta_description.strip(),
            cls.LONGUEUR_MAX_META_DESCRIPTION
        )

        ##################################################
        # Mots-clés
        #
        # Objectif : couvrir les différentes façons dont un
        # client formule sa recherche (utile pour le moteur
        # de recherche interne WiziShop et les marketplaces
        # — Google, lui, n'utilise plus ce champ depuis
        # 2009, la vraie valeur SEO Google se joue dans le
        # titre/description). Jamais de marque/fabricant,
        # matière ou couleur en mot-clé : personne ne
        # recherche un produit par ces critères.
        ##################################################

        type_generique = nom_produit

        if licence_nom:

            type_generique = re.sub(
                re.escape(licence_nom), "", nom_produit,
                flags=re.IGNORECASE
            )
            type_generique = re.sub(r"\s+", " ", type_generique).strip()

        premier_mot_type = (
            type_generique.split()[0] if type_generique else ""
        )

        candidats = [nom_produit]

        if licence_nom:

            candidats.append(licence_nom)

            if not licence_deja_mentionnee:
                candidats.append(f"{nom_produit} {licence_nom}")

            if type_generique and type_generique != nom_produit:
                candidats.append(f"{type_generique} {licence_nom}")

            if premier_mot_type:
                candidats.append(f"{premier_mot_type} {licence_nom}")

        if type_generique:
            candidats.append(type_generique)

        if categorie_nom:

            candidats.append(categorie_nom)

            if licence_nom:
                candidats.append(f"{categorie_nom} {licence_nom}")

        mots_cles_dedupliques = []
        vus = set()

        for expression in candidats:

            expression_propre = expression.strip().lower()

            if not expression_propre or expression_propre in vus:
                continue

            vus.add(expression_propre)
            mots_cles_dedupliques.append(expression.strip())

        mots_cles = ", ".join(mots_cles_dedupliques)

        ##################################################
        # URL / slug
        ##################################################

        base_slug = nom_produit

        if licence_nom and licence_nom.lower() not in nom_produit.lower():
            base_slug = f"{base_slug} {licence_nom}"

        url_slug = cls._slugifier(base_slug)

        ##################################################
        # Schema.org (JSON-LD, type Product)
        ##################################################

        schema = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": nom_produit,
        }

        if marque_nom:
            schema["brand"] = {
                "@type": "Brand",
                "name": marque_nom,
            }

        if categorie_nom:
            schema["category"] = categorie_nom

        if ean:
            schema["gtin13"] = ean

        if sku:
            schema["sku"] = sku

        if description_courte:
            schema["description"] = description_courte

        if prix_ttc:
            schema["offers"] = {
                "@type": "Offer",
                "priceCurrency": "EUR",
                "price": round(prix_ttc, 2),
                "availability": "https://schema.org/InStock",
            }

        schema_org_json = json.dumps(
            schema, ensure_ascii=False, indent=2
        )

        return {
            "titre_seo": titre_seo,
            "description_courte": description_courte,
            "description_longue": description_longue,
            "meta_description": meta_description,
            "mots_cles": mots_cles,
            "url_slug": url_slug,
            "schema_org_json": schema_org_json,
        }