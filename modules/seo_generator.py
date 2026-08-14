import json
import re
import unicodedata


class SeoGenerator:
    """
    Génère automatiquement le contenu SEO d'une fiche
    produit (titre, descriptions, meta description,
    mots-clés, URL, données structurées Schema.org) à
    partir des informations déjà saisies sur le produit.

    La description courte est une ACCROCHE COMMERCIALE :
    aucune mention de livraison ni de délai, qui seraient
    fausses sur un Direct Fournisseur et intenables sur une
    précommande.

    Toutes les méthodes sont statiques : ce module ne touche
    jamais à la base de données lui-même.
    """

    NOM_SITE = "Pop Licence"

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
        accents, espaces remplacés par des tirets.
        """

        if not texte:
            return ""

        normalise = unicodedata.normalize("NFKD", texte)
        sans_accents = normalise.encode("ascii", "ignore").decode("ascii")

        minuscule = sans_accents.lower()

        avec_tirets = re.sub(r"[^a-z0-9]+", "-", minuscule)

        return avec_tirets.strip("-")

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

        texte = f"{valeur:.1f}".replace(".", ",").rstrip("0").rstrip(",")

        return f"{texte} kg"

    @staticmethod
    def _format_lisible(longueur, largeur, hauteur):
        """
        Renvoie "30 x 15,5 x 10 cm", en ignorant les mesures
        manquantes.
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
    def _caracteristique_principale(matiere, couleur):
        """
        Combine matière et couleur en une phrase courte
        naturelle.
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
        poids=None,
        longueur=None,
        largeur=None,
        hauteur=None,
        accroche=None,
    ):
        """
        Génère les 7 champs SEO à partir des informations
        produit disponibles.
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

        # Le FABRICANT n'a rien a faire dans le titre : il
        # n'apporte rien au referencement et brouille le
        # message. C'est le nom de la boutique qui prend sa
        # place, comme sur les 239 pages categories.

        suffixe = f" | {cls.NOM_SITE}"

        if len(titre_seo) + len(suffixe) <= cls.LONGUEUR_MAX_TITRE:
            titre_seo += suffixe

        titre_seo = cls._tronquer(titre_seo, cls.LONGUEUR_MAX_TITRE)

        ##################################################
        # Description courte — l'accroche commerciale
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

        faits = []

        if poids:
            faits.append(cls._poids_lisible(poids))

        format_lisible = cls._format_lisible(longueur, largeur, hauteur)

        if format_lisible:
            faits.append(f"format {format_lisible}")

        # La matière et le coloris ne sont PAS repris ici :
        # ils figurent déjà dans la fiche technique et dans
        # la meta description.

        morceaux = [
            f"{nom_produit} sous licence officielle"
            if licence_nom and licence_deja_mentionnee
            else f"{nom_produit}{phrase_licence}"
        ]

        if faits:
            morceaux.append(" : " + ", ".join(faits))

        if accroche:
            morceaux.append(
                (", " if faits else " : ") + accroche.strip(" .")
            )

        description_courte = "".join(morceaux) + "."

        description_courte = cls._tronquer(
            description_courte.strip(),
            cls.LONGUEUR_MAX_DESCRIPTION_COURTE
        )

        ##################################################
        # Description longue
        ##################################################

        # LES DIMENSIONS ET LE POIDS NE SONT PLUS ECRITS ICI :
        # le modele de fiche produit les affiche deja dans sa
        # propre ligne technique. Les repeter fabriquait un
        # doublon visible sur la fiche WiziShop.

        paragraphes = []

        # AUCUN VERBE NI ARTICLE DEVANT LE NOM DU PRODUIT.
        # Le logiciel ne peut pas connaitre le genre ni le
        # nombre d'un nom : "chaussures" est feminin pluriel,
        # "chaussons" masculin pluriel, et une meme categorie
        # melange les deux. Le nom est donc pose en apposition,
        # ce qui reste correct dans tous les cas -- et le place
        # en premiere position, ce qui sert le referencement.

        phrase_ouverture = nom_produit

        if licence_nom and not licence_deja_mentionnee:
            phrase_ouverture += (
                f", un produit officiel sous licence {licence_nom}"
            )
        else:
            # La licence figure deja dans le nom : la repeter
            # trois fois dans le meme paragraphe serait du
            # bourrage de mots-cles.
            phrase_ouverture += ", un produit officiel sous licence"

        phrase_ouverture += "."

        paragraphes.append(phrase_ouverture)

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

        if categorie_nom:
            paragraphes.append(
                f"Une belle idée cadeau pour les amateurs de "
                f"{categorie_nom.lower()}."
            )

        elif licence_nom and not licence_deja_mentionnee:
            paragraphes.append(
                f"Une belle idée cadeau pour les fans de "
                f"{licence_nom}."
            )

        description_longue = " ".join(paragraphes)

        ##################################################
        # Meta description
        #
        # Aucune mention de délai ni de livraison : elle part
        # telle quelle sur tous les types de produit, Direct
        # Fournisseur et précommande compris.
        ##################################################

        meta_description = (
            f"{nom_produit}"
            f"{' ' + licence_nom if licence_nom and not licence_deja_mentionnee else ''}"
            f" sous licence officielle."
            f"{' ' + caracteristique[0].upper() + caracteristique[1:] + '.' if caracteristique else ''}"
            f" À retrouver chez {cls.NOM_SITE}, produits dérivés officiels."
        )

        meta_description = cls._tronquer(
            meta_description.strip(),
            cls.LONGUEUR_MAX_META_DESCRIPTION
        )

        ##################################################
        # Mots-clés
        ##################################################

        # ON NE DECOUPE PLUS LE NOM MOT A MOT : cela produisait
        # des mots-cles sans valeur du type "pat", "paw", "pvc".
        # On garde des expressions entieres.

        candidats = [nom_produit]

        for valeur in (
            licence_nom, categorie_nom, famille_nom, couleur, matiere
        ):

            if valeur:
                candidats.append(valeur)

        mots_cles_dedupliques = []
        vus = set()

        for mot in candidats:

            mot_propre = mot.strip().lower()

            if len(mot_propre) < 3:
                continue

            if mot_propre in vus:
                continue

            vus.add(mot_propre)
            mots_cles_dedupliques.append(mot_propre)

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

        # LA MARQUE AFFICHEE EST LA LICENCE, pas le fabricant :
        # c'est la convention de toute la boutique.
        if licence_nom or marque_nom:
            schema["brand"] = {
                "@type": "Brand",
                "name": licence_nom or marque_nom,
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
                "price": f"{float(prix_ttc):.2f}",
                "priceCurrency": "EUR",
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