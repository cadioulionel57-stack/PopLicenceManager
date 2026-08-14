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

        L'ORIENTATION DU PRODUIT EST LIBRE : les trois
        dimensions du produit et celles de l'emballage sont
        triées de la plus grande à la plus petite avant
        d'être comparées. On compare donc la plus grande du
        produit à la plus grande de l'emballage, et ainsi de
        suite — comme lorsqu'on tourne un objet dans la main
        pour le glisser dans un carton.

        Sans ce tri, un bonnet saisi 22 x 2 x 21 (l'ordre
        dans lequel le fournisseur donne ses mesures, qui
        change d'un fournisseur a l'autre et parfois d'un
        produit a l'autre) ne rentrait dans aucune pochette,
        alors qu'il y rentre parfaitement une fois tourne.
        """

        tous_les_emballages = self.tous()

        compatibles = []

        # Produit : de la plus grande dimension a la plus
        # petite. Les valeurs manquantes comptent pour 0.
        dimensions_produit = sorted(
            [
                longueur_cm or 0,
                largeur_cm or 0,
                hauteur_cm or 0,
            ],
            reverse=True
        )

        for emballage in tous_les_emballages:

            if emballage["longueur_ext_cm"] is None:
                continue
            if emballage["largeur_ext_cm"] is None:
                continue
            if emballage["hauteur_ext_cm"] is None:
                continue
            if emballage["poids_max_g"] is None:
                continue

            # Les pochettes souples (P1/P2) enveloppent le
            # produit au plus près : pas besoin de marge de
            # sécurité. Seuls les cartons rigides (C1-C4) en
            # ont réellement besoin (fermeture, calage).
            if emballage["type_emballage"] == "souple":
                marge_reelle = 0
            else:
                marge_reelle = marge_cm

            # Emballage : trie de la meme facon, pour que la
            # comparaison porte sur des grandeurs de meme
            # rang (la plus grande avec la plus grande).
            dimensions_emballage = sorted(
                [
                    emballage["longueur_ext_cm"],
                    emballage["largeur_ext_cm"],
                    emballage["hauteur_ext_cm"],
                ],
                reverse=True
            )

            convient = True

            for cote_emballage, cote_produit in zip(
                dimensions_emballage, dimensions_produit
            ):

                if cote_emballage < cote_produit + marge_reelle:
                    convient = False
                    break

            if not convient:
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