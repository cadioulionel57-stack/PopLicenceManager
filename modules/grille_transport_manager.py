from database.database import Database


class GrilleTransportManager:
    """
    Gère la grille tarifaire des transporteurs (Mondial
    Relay, Colissimo, Chronopost...), basée sur les tarifs
    Boxtal : un prix HT par tranche de poids, pour chaque
    offre d'un transporteur.

    Rien n'est figé : la grille est entièrement modifiable
    depuis l'interface, transporteur par transporteur.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT
                g.id,
                g.transporteur_id,
                g.offre,
                g.poids_max_kg,
                g.prix_ht,
                g.actif,
                t.nom AS transporteur
            FROM grille_transport g

            LEFT JOIN transporteurs t
                ON t.id = g.transporteur_id

            WHERE g.actif = 1

            ORDER BY t.nom, g.offre, g.poids_max_kg
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM grille_transport
            WHERE id = ?
            """,
            (identifiant,)
        )

    def offres_disponibles(self):
        """
        Renvoie la liste des couples (transporteur, offre)
        existants, pour peupler les menus déroulants
        ailleurs dans le logiciel (ex : choix du
        transporteur sur un canal de vente).
        """

        return self.db.lire(
            """
            SELECT DISTINCT
                g.transporteur_id,
                t.nom AS transporteur,
                g.offre
            FROM grille_transport g

            LEFT JOIN transporteurs t
                ON t.id = g.transporteur_id

            WHERE g.actif = 1

            ORDER BY t.nom, g.offre
            """
        )

    def ajouter(self, transporteur_id, offre, poids_max_kg, prix_ht):

        self.db.executer(
            """
            INSERT INTO grille_transport
            (
                transporteur_id,
                offre,
                poids_max_kg,
                prix_ht,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, 1
            )
            """,
            (
                transporteur_id,
                offre,
                poids_max_kg,
                prix_ht
            )
        )

    def modifier(
        self,
        identifiant,
        transporteur_id,
        offre,
        poids_max_kg,
        prix_ht
    ):

        self.db.executer(
            """
            UPDATE grille_transport
            SET
                transporteur_id = ?,
                offre = ?,
                poids_max_kg = ?,
                prix_ht = ?
            WHERE id = ?
            """,
            (
                transporteur_id,
                offre,
                poids_max_kg,
                prix_ht,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_transport
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def tarif(self, transporteur_id, offre, poids_kg):
        """
        Renvoie le prix HT du transport pour un poids
        donné : la plus petite tranche de poids qui
        couvre ce poids.

        Renvoie None si aucune tranche ne couvre ce poids
        (produit trop lourd pour cette offre).
        """

        lignes = self.db.lire(
            """
            SELECT poids_max_kg, prix_ht
            FROM grille_transport
            WHERE transporteur_id = ?
            AND offre = ?
            AND actif = 1
            ORDER BY poids_max_kg ASC
            """,
            (transporteur_id, offre)
        )

        for ligne in lignes:

            if poids_kg <= ligne["poids_max_kg"]:
                return ligne["prix_ht"]

        return None