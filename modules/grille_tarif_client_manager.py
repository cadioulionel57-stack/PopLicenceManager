from database.database import Database


class GrilleTarifClientManager:
    """
    Gère la grille des tarifs de port FACTURÉS AU CLIENT,
    quand un canal a besoin de plusieurs tarifs différents
    selon le transporteur ET la tranche de poids (cas Fnac :
    le client choisit entre Relais Colis ou Colissimo
    Recommandé R1, chacun avec son propre tarif par poids).

    À ne pas confondre avec grille_transport, qui contient
    le COÛT RÉEL payé au transporteur — cette grille-ci
    contient le PRIX AFFICHÉ AU CLIENT.

    Rien n'est figé : la grille est entièrement modifiable
    depuis l'interface, une fois l'écran de gestion créé.
    """

    def __init__(self):

        self.db = Database()

    def tous(self, canal_id=None):

        if canal_id is not None:

            return self.db.lire(
                """
                SELECT
                    g.*,
                    t.nom AS transporteur,
                    c.nom AS canal
                FROM grille_tarif_client g

                LEFT JOIN transporteurs t
                    ON t.id = g.transporteur_id

                LEFT JOIN canaux_vente c
                    ON c.id = g.canal_id

                WHERE g.actif = 1
                AND g.canal_id = ?

                ORDER BY t.nom, g.offre, g.poids_max_kg
                """,
                (canal_id,)
            )

        return self.db.lire(
            """
            SELECT
                g.*,
                t.nom AS transporteur,
                c.nom AS canal
            FROM grille_tarif_client g

            LEFT JOIN transporteurs t
                ON t.id = g.transporteur_id

            LEFT JOIN canaux_vente c
                ON c.id = g.canal_id

            WHERE g.actif = 1

            ORDER BY c.nom, t.nom, g.offre, g.poids_max_kg
            """
        )

    def ajouter(
        self, canal_id, transporteur_id, offre, poids_max_kg, tarif_ttc
    ):

        curseur = self.db.executer(
            """
            INSERT INTO grille_tarif_client
            (
                canal_id,
                transporteur_id,
                offre,
                poids_max_kg,
                tarif_ttc,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, 1
            )
            """,
            (
                canal_id,
                transporteur_id,
                offre,
                poids_max_kg,
                tarif_ttc,
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        canal_id,
        transporteur_id,
        offre,
        poids_max_kg,
        tarif_ttc,
    ):

        self.db.executer(
            """
            UPDATE grille_tarif_client
            SET
                canal_id = ?,
                transporteur_id = ?,
                offre = ?,
                poids_max_kg = ?,
                tarif_ttc = ?
            WHERE id = ?
            """,
            (
                canal_id,
                transporteur_id,
                offre,
                poids_max_kg,
                tarif_ttc,
                identifiant,
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_tarif_client
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def tarif(self, canal_id, transporteur_id, offre, poids_kg):
        """
        Renvoie le tarif TTC facturé au client pour ce
        canal/transporteur/offre, au poids donné : la plus
        petite tranche de poids qui couvre ce poids.

        Renvoie None si aucune tranche ne couvre ce poids
        (produit trop lourd pour cette offre sur ce canal).
        """

        lignes = self.db.lire(
            """
            SELECT poids_max_kg, tarif_ttc
            FROM grille_tarif_client
            WHERE canal_id = ?
            AND transporteur_id = ?
            AND offre = ?
            AND actif = 1
            ORDER BY poids_max_kg ASC
            """,
            (canal_id, transporteur_id, offre)
        )

        for ligne in lignes:

            if poids_kg <= ligne["poids_max_kg"]:
                return ligne["tarif_ttc"]

        return None
