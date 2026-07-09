from database.database import Database


class EmballageManager:
    """
    Gère la grille d'emballages (pochettes, cartons...)
    utilisée pour calculer automatiquement le coût
    d'emballage d'un produit, selon la famille à laquelle
    il appartient.

    Rien n'est figé : la grille est entièrement modifiable
    depuis l'interface.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM grille_emballage
            WHERE actif = 1
            ORDER BY longueur_ext_cm * largeur_ext_cm * hauteur_ext_cm
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM grille_emballage
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        code,
        nom,
        longueur_ext_cm,
        largeur_ext_cm,
        hauteur_ext_cm,
        poids_g,
        cout_ht,
        calage_ht,
    ):

        curseur = self.db.executer(
            """
            INSERT INTO grille_emballage
            (
                code,
                nom,
                longueur_ext_cm,
                largeur_ext_cm,
                hauteur_ext_cm,
                poids_g,
                cout_ht,
                calage_ht,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                code,
                nom,
                longueur_ext_cm,
                largeur_ext_cm,
                hauteur_ext_cm,
                poids_g,
                cout_ht,
                calage_ht,
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        code,
        nom,
        longueur_ext_cm,
        largeur_ext_cm,
        hauteur_ext_cm,
        poids_g,
        cout_ht,
        calage_ht,
    ):

        self.db.executer(
            """
            UPDATE grille_emballage
            SET
                code = ?,
                nom = ?,
                longueur_ext_cm = ?,
                largeur_ext_cm = ?,
                hauteur_ext_cm = ?,
                poids_g = ?,
                cout_ht = ?,
                calage_ht = ?
            WHERE id = ?
            """,
            (
                code,
                nom,
                longueur_ext_cm,
                largeur_ext_cm,
                hauteur_ext_cm,
                poids_g,
                cout_ht,
                calage_ht,
                identifiant,
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_emballage
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def cout_total(self, emballage_id):
        """
        Renvoie le coût total (emballage + calage) pour un
        emballage donné.
        """

        emballage = self.obtenir(emballage_id)

        if emballage is None:
            return 0

        return (emballage["cout_ht"] or 0) + (emballage["calage_ht"] or 0)

    def compatibles(
        self,
        longueur_cm,
        largeur_cm,
        hauteur_cm,
        poids_g,
        marge_cm=1,
    ):
        """
        Renvoie la liste des emballages de la grille
        compatibles avec les dimensions et le poids d'un
        produit donné, triés du plus petit au plus grand
        (par volume extérieur croissant).

        Un emballage est compatible si :
        - chacune de ses dimensions extérieures est
          supérieure ou égale à la dimension du produit
          correspondante + la marge de sécurité (1cm par
          défaut, pour permettre calage/fermeture) ;
        - son poids max supporté est supérieur ou égal au
          poids du produit.

        Renvoie une liste vide si aucun emballage ne
        convient — dans ce cas, la création du produit doit
        être bloquée côté interface, avec une alerte
        invitant à ajouter un nouvel emballage à la grille.

        Rien n'est présupposé sur l'orientation du produit
        dans l'emballage (pas de rotation testée) : la
        comparaison se fait dimension par dimension, dans
        l'ordre où elles sont saisies (longueur avec
        longueur, largeur avec largeur, hauteur avec
        hauteur).
        """

        tous_les_emballages = self.tous()

        compatibles = []

        for emballage in tous_les_emballages:

            if emballage["longueur_ext_cm"] is None:
                continue
            if emballage["largeur_ext_cm"] is None:
                continue
            if emballage["hauteur_ext_cm"] is None:
                continue
            if emballage["poids_max_g"] is None:
                continue

            if emballage["longueur_ext_cm"] < longueur_cm + marge_cm:
                continue
            if emballage["largeur_ext_cm"] < largeur_cm + marge_cm:
                continue
            if emballage["hauteur_ext_cm"] < hauteur_cm + marge_cm:
                continue
            if emballage["poids_max_g"] < poids_g:
                continue

            compatibles.append(emballage)

        compatibles.sort(
            key=lambda e: (
                e["longueur_ext_cm"]
                * e["largeur_ext_cm"]
                * e["hauteur_ext_cm"]
            )
        )

        return compatibles