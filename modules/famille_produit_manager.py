from database.database import Database


class FamilleProduitManager:
    """
    Gère les familles de produits (Textile & Mode,
    Chaussures, Linge de maison, Jeux & Jouets...).

    Chaque famille a un coût d'emballage moyen et un
    taux de retour, utilisés pour calculer le coût de
    revient réel d'un produit, quel que soit le canal
    sur lequel il est vendu.

    Rien n'est figé : les familles se créent, se
    modifient ou se désactivent librement depuis
    l'interface.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM familles_produit
            WHERE actif = 1
            ORDER BY nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM familles_produit
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(self, nom, cout_emballage_ht=0, taux_retour=0):

        self.db.executer(
            """
            INSERT INTO familles_produit
            (
                nom,
                cout_emballage_ht,
                taux_retour,
                actif
            )
            VALUES
            (
                ?, ?, ?, 1
            )
            """,
            (
                nom,
                cout_emballage_ht,
                taux_retour
            )
        )

    def modifier(
        self,
        identifiant,
        nom,
        cout_emballage_ht,
        taux_retour
    ):

        self.db.executer(
            """
            UPDATE familles_produit
            SET
                nom = ?,
                cout_emballage_ht = ?,
                taux_retour = ?
            WHERE id = ?
            """,
            (
                nom,
                cout_emballage_ht,
                taux_retour,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE familles_produit
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def cout_produit(self, famille_id, prix_achat_ht):
        """
        Calcule le coût de revient "produit" (indépendant
        du canal de vente) :

        (Prix d'achat HT + Coût emballage) × (1 + Taux de retour)
        """

        if famille_id is None:
            return prix_achat_ht or 0

        famille = self.obtenir(famille_id)

        if famille is None:
            return prix_achat_ht or 0

        base = (prix_achat_ht or 0) + (famille["cout_emballage_ht"] or 0)

        return base * (1 + (famille["taux_retour"] or 0))