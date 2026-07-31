from datetime import date

from database.database import Database


# Les quatre types de produits du logiciel, avec le
# libellé qu'on affiche à l'écran.
LIBELLES_TYPES = {
    "stock": "en Stock",
    "dropshipping": "Direct Fournisseur",
    "precommande": "en Précommande",
    "bundle": "Bundle",
}


def normaliser_date(valeur):
    """
    Ramène une date au format AAAA-MM-JJ, seul format
    comparable de façon fiable.

    L'ancien écran des périodes laissait taper la date à la
    main dans un champ libre : on trouve donc aussi bien
    « 2026-12-01 » que « 01/12/2026 ». Les deux doivent
    fonctionner, sinon une règle reste muette sans qu'on
    sache pourquoi.
    """

    texte = str(valeur or "").strip()

    if not texte:
        return ""

    if "/" in texte:

        morceaux = texte.split("/")

        if len(morceaux) == 3:

            jour, mois, annee = (m.strip() for m in morceaux)

            if len(annee) == 2:
                annee = "20" + annee

            if jour.isdigit() and mois.isdigit() and annee.isdigit():
                return f"{annee}-{int(mois):02d}-{int(jour):02d}"

    return texte[:10]


class RegleTemplateManager:

    def __init__(self):

        self.db = Database()

    ########################################################
    # Lecture
    ########################################################

    def regles(self, actives_seulement=False):
        """
        Toutes les règles, avec les noms lisibles de la
        période, du modèle et de la catégorie visée.
        """

        condition = "WHERE r.actif = 1" if actives_seulement else ""

        return self.db.lire(f"""
            SELECT
                r.*,
                p.nom AS nom_periode,
                p.date_debut,
                p.date_fin,
                m.nom AS nom_modele,
                t.nom AS nom_theme,
                c.nom AS nom_categorie
            FROM regles_template_periode r
            LEFT JOIN periodes_commerciales p ON p.id = r.periode_id
            LEFT JOIN modeles_fiche_produit m ON m.id = r.modele_fiche_id
            LEFT JOIN themes_template t ON t.id = m.theme_id
            LEFT JOIN categories_site c ON c.id = r.categorie_site_id
            {condition}
            ORDER BY p.date_debut, r.priorite DESC
        """)

    def types_du_modele(self, modele_fiche_id):
        """
        Les types de produits que couvre un modèle de fiche.

        C'est la définition du modèle lui-même qui le dit :
        un « Template STOCK Vêtements » ne coche que
        « stock ». On ne redemande donc jamais cette
        information à l'utilisateur.
        """

        lignes = self.db.lire(
            """
            SELECT type_produit
            FROM modeles_fiche_types
            WHERE modele_id = ?
            """,
            (modele_fiche_id,)
        )

        return [l["type_produit"] for l in lignes if l["type_produit"]]

    def obtenir(self, identifiant):

        return self.db.lire_un(
            "SELECT * FROM regles_template_periode WHERE id = ?",
            (identifiant,)
        )

    ########################################################
    # Écriture
    ########################################################

    def ajouter(
        self,
        nom,
        periode_id,
        modele_fiche_id,
        categorie_site_id=None,
        priorite=0,
    ):

        if not periode_id:
            raise ValueError("Choisis une période commerciale.")

        if not modele_fiche_id:
            raise ValueError("Choisis un modèle de fiche.")

        curseur = self.db.executer("""
            INSERT INTO regles_template_periode
                (nom, periode_id, modele_fiche_id,
                 categorie_site_id, priorite, actif)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (
            (nom or "").strip(),
            periode_id,
            modele_fiche_id,
            categorie_site_id,
            priorite or 0,
        ))

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        nom,
        periode_id,
        modele_fiche_id,
        categorie_site_id=None,
        priorite=0,
        actif=True,
    ):

        if not periode_id:
            raise ValueError("Choisis une période commerciale.")

        if not modele_fiche_id:
            raise ValueError("Choisis un modèle de fiche.")

        self.db.executer("""
            UPDATE regles_template_periode
            SET nom = ?, periode_id = ?, modele_fiche_id = ?,
                categorie_site_id = ?, priorite = ?, actif = ?
            WHERE id = ?
        """, (
            (nom or "").strip(),
            periode_id,
            modele_fiche_id,
            categorie_site_id,
            priorite or 0,
            1 if actif else 0,
            identifiant,
        ))

    def supprimer(self, identifiant):

        self.db.executer(
            "DELETE FROM regles_template_periode WHERE id = ?",
            (identifiant,)
        )

    ########################################################
    # Le cœur : quelle règle s'applique
    ########################################################

    def regles_en_cours(self, jour=None):
        """
        Les règles dont la période couvre le jour donné
        (aujourd'hui par défaut).
        """

        if jour is None:
            jour = date.today().isoformat()

        jour = normaliser_date(jour)

        # La comparaison se fait en Python et non en SQL :
        # les dates enregistrées peuvent être au format
        # français, il faut les remettre d'aplomb avant de
        # comparer quoi que ce soit.
        candidates = self.db.lire("""
            SELECT
                r.*,
                p.nom AS nom_periode,
                p.date_debut,
                p.date_fin,
                m.nom AS nom_modele
            FROM regles_template_periode r
            JOIN periodes_commerciales p ON p.id = r.periode_id
            JOIN modeles_fiche_produit m ON m.id = r.modele_fiche_id
            WHERE r.actif = 1
              AND p.actif = 1
              AND m.actif = 1
            ORDER BY r.priorite DESC
        """)

        retenues = []

        for regle in candidates:

            debut = normaliser_date(regle["date_debut"])
            fin = normaliser_date(regle["date_fin"])

            if not debut or not fin:
                continue

            if debut <= jour <= fin:
                retenues.append(regle)

        return retenues

    def template_pour(self, produit_id, jour=None):
        """
        Le modèle de fiche qui s'applique à ce produit à
        cette date.

        Renvoie un dictionnaire :
            modele_fiche_id : le modèle à utiliser
            origine         : "regle" ou "fiche"
            nom_regle       : le nom de la règle, le cas échéant

        Ordre de préférence : une règle visant la catégorie
        du produit passe devant une règle visant tout le
        catalogue ; à défaut de règle, le modèle choisi dans
        la fiche.
        """

        produit = self.db.lire_un("""
            SELECT modele_fiche_id, categorie_site_id,
                   type_produit
            FROM produits WHERE id = ?
        """, (produit_id,))

        defaut = {
            "modele_fiche_id": (
                produit["modele_fiche_id"] if produit else None
            ),
            "origine": "fiche",
            "nom_regle": None,
        }

        if produit is None:
            return defaut

        categorie = produit["categorie_site_id"]
        type_produit = produit["type_produit"]

        meilleure = None
        meilleur_rang = None

        for regle in self.regles_en_cours(jour):

            vise_toute_categorie = regle["categorie_site_id"] is None

            # Une règle qui vise une catégorie précise ne
            # concerne que les produits de cette catégorie.
            if (
                not vise_toute_categorie
                and regle["categorie_site_id"] != categorie
            ):
                continue

            # LE TYPE VIENT DU MODÈLE, PAS DE LA RÈGLE.
            #
            # Un « Template STOCK Vêtements » ne coche que le
            # type « stock » dans sa définition : il ne peut
            # donc pas atterrir sur un produit Direct
            # Fournisseur, même si la règle vise toute la
            # catégorie Vêtements. C'est ce qui permet
            # d'écrire une règle par modèle sans jamais se
            # contredire.
            types = self.types_du_modele(regle["modele_fiche_id"])

            if types and type_produit not in types:
                continue

            # Rang de comparaison : la priorité d'abord, puis
            # la précision — une règle qui vise une catégorie
            # précise passe devant une règle générale.
            precision = 0 if vise_toute_categorie else 1

            rang = (regle["priorite"] or 0, precision)

            if meilleur_rang is None or rang > meilleur_rang:
                meilleure = regle
                meilleur_rang = rang

        if meilleure is None:
            return defaut

        return {
            "modele_fiche_id": meilleure["modele_fiche_id"],
            "origine": "regle",
            "nom_regle": (
                meilleure["nom"] or meilleure["nom_periode"] or ""
            ),
        }

    def apercu(self, jour=None):
        """
        Ce qui s'applique aujourd'hui, en une phrase par
        règle — pour l'afficher à l'écran sans avoir à
        interpréter des dates.
        """

        lignes = []

        for regle in self.regles_en_cours(jour):

            morceaux = []

            if regle["categorie_site_id"]:

                categorie = self.db.lire_un(
                    "SELECT nom FROM categories_site WHERE id = ?",
                    (regle["categorie_site_id"],)
                )

                if categorie:
                    morceaux.append(
                        f"la catégorie « {categorie['nom']} »"
                    )

            types = self.types_du_modele(regle["modele_fiche_id"])

            if types:
                morceaux.append(
                    "les produits "
                    + " ou ".join(
                        LIBELLES_TYPES.get(t, t) for t in types
                    )
                )

            cible = " et ".join(morceaux) or "tous les produits"

            lignes.append(
                f"{cible} → modèle « {regle['nom_modele']} » "
                f"(période {regle['nom_periode']})"
            )

        return lignes