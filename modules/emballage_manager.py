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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
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

    def desactiver(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_emballage
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def cout_total(self, identifiant):
        """
        Coût complet d'un emballage : le contenant plus son
        calage. C'est ce montant qui entre dans le coût de
        revient du produit.
        """

        emballage = self.obtenir(identifiant)

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

        TROIS REGLES.

        Emballage SOUPLE (pochette plastique) : la pochette
        se referme autour du produit. On ne compare que ses
        DEUX dimensions, en ajoutant la MOITIE de l'epaisseur
        du produit a chacune — une pochette souple ne
        consomme pas toute l'epaisseur en se refermant. Sans
        cet assouplissement, un set gants et bonnet de
        22 x 18 x 4 cm etait ecarte de la pochette 24 x 35.

        Emballage RIGIDE, dimension la plus longue : la
        marge de securite n'est PAS exigee. Un article de
        60 cm entre dans un carton de 60 cm ; c'est la
        largeur et la hauteur qui demandent du calage, pas
        la longueur.

        Emballage RIGIDE, deux autres dimensions : la marge
        de securite s'applique normalement (1 cm par defaut,
        pour la fermeture et le calage).

        L'ORIENTATION DU PRODUIT EST LIBRE : les dimensions
        du produit et celles de l'emballage sont triees de
        la plus grande a la plus petite avant d'etre
        comparees — comme lorsqu'on tourne un objet dans la
        main pour le glisser dans un carton.

        Renvoie une liste vide si aucun emballage ne
        convient — dans ce cas, la creation du produit doit
        etre bloquee cote interface, avec une alerte
        invitant a ajouter un nouvel emballage a la grille.
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

        demi_epaisseur = dimensions_produit[2] / 2.0

        for emballage in tous_les_emballages:

            if emballage["longueur_ext_cm"] is None:
                continue
            if emballage["largeur_ext_cm"] is None:
                continue
            if emballage["hauteur_ext_cm"] is None:
                continue
            if emballage["poids_max_g"] is None:
                continue

            souple = emballage["type_emballage"] == "souple"

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

            if souple:

                # Pochette : deux dimensions utiles, et la
                # moitie de l'epaisseur du produit vient
                # s'ajouter aux deux.
                for rang in (0, 1):

                    cote_emballage = dimensions_emballage[rang]
                    cote_produit = dimensions_produit[rang]

                    if cote_emballage < cote_produit + demi_epaisseur:
                        convient = False
                        break

            else:

                # Carton : les trois dimensions comptent.
                for rang in (0, 1, 2):

                    cote_emballage = dimensions_emballage[rang]
                    cote_produit = dimensions_produit[rang]

                    # Pas de marge exigee sur la plus grande
                    # dimension : un article de 60 cm entre
                    # dans un carton de 60 cm.
                    marge = 0 if rang == 0 else marge_cm

                    if cote_emballage < cote_produit + marge:
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