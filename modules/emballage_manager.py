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

        DEUX RÈGLES SELON LE TYPE D'EMBALLAGE.

        Emballage RIGIDE (carton, sac kraft) : chacune de
        ses trois dimensions extérieures doit être
        supérieure ou égale à la dimension correspondante du
        produit, plus la marge de sécurité (1 cm par défaut,
        pour la fermeture et le calage).

        Emballage SOUPLE (pochette plastique) : la pochette
        n'a pas de troisième dimension réelle, elle se
        referme autour du produit. On ne compare donc que
        ses DEUX dimensions, en ajoutant l'épaisseur du
        produit à chacune — car la pochette consomme de la
        largeur en se refermant sur un article épais.

        Sans cette distinction, un t-shirt, un pantalon ou
        un manteau plié de plus d'un centimètre d'épaisseur
        était systématiquement écarté des pochettes, et le
        logiciel imposait un carton. Le coût d'emballage
        était alors surévalué de plus de 50 centimes par
        produit, ce qui faussait tous les prix de vente.

        L'ORIENTATION DU PRODUIT EST LIBRE : les dimensions
        du produit et celles de l'emballage sont triées de
        la plus grande à la plus petite avant d'être
        comparées — comme lorsqu'on tourne un objet dans la
        main pour le glisser dans un carton.

        Renvoie une liste vide si aucun emballage ne
        convient — dans ce cas, la création du produit doit
        être bloquée côté interface, avec une alerte
        invitant à ajouter un nouvel emballage à la grille.
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

        epaisseur_produit = dimensions_produit[2]

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

                # Pochette : deux dimensions utiles, et
                # l'epaisseur du produit vient s'ajouter aux
                # deux car la pochette se referme autour.
                for rang in (0, 1):

                    cote_emballage = dimensions_emballage[rang]
                    cote_produit = dimensions_produit[rang]

                    if cote_emballage < cote_produit + epaisseur_produit:
                        convient = False
                        break

            else:

                # Carton : les trois dimensions comptent, et
                # il faut la marge de fermeture et de calage.
                for cote_emballage, cote_produit in zip(
                    dimensions_emballage, dimensions_produit
                ):

                    if cote_emballage < cote_produit + marge_cm:
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