from database.database import Database
from modules.emballage_manager import EmballageManager


class FamilleProduitManager:
    """
    Gère les familles de produits (Textile & Mode,
    Chaussures, Linge de maison, Jeux & Jouets...).

    Chaque famille a un emballage lié (dont le coût est
    calculé automatiquement depuis la grille d'emballage)
    et un taux de retour, utilisés pour calculer le coût
    de revient réel d'un produit, quel que soit le canal
    sur lequel il est vendu.

    Si aucun emballage n'est lié, le coût d'emballage
    manuel (cout_emballage_ht) reste utilisé — pour la
    rétrocompatibilité avec les familles créées avant
    l'existence de la grille d'emballage.

    Rien n'est figé : les familles se créent, se
    modifient ou se désactivent librement depuis
    l'interface.
    """

    def __init__(self):

        self.db = Database()
        self.emballages = EmballageManager()

    def tous(self):

        return self.db.lire(
            """
            SELECT
                f.*,
                e.code AS emballage_code,
                e.nom AS emballage_nom
            FROM familles_produit f

            LEFT JOIN grille_emballage e
                ON e.id = f.emballage_id

            WHERE f.actif = 1

            ORDER BY f.nom
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

    def ajouter(
        self,
        nom,
        cout_emballage_ht=0,
        taux_retour=0,
        emballage_id=None,
    ):

        self.db.executer(
            """
            INSERT INTO familles_produit
            (
                nom,
                cout_emballage_ht,
                emballage_id,
                taux_retour,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, 1
            )
            """,
            (
                nom,
                cout_emballage_ht,
                emballage_id,
                taux_retour
            )
        )

    def modifier(
        self,
        identifiant,
        nom,
        cout_emballage_ht,
        taux_retour,
        emballage_id=None,
    ):

        self.db.executer(
            """
            UPDATE familles_produit
            SET
                nom = ?,
                cout_emballage_ht = ?,
                emballage_id = ?,
                taux_retour = ?
            WHERE id = ?
            """,
            (
                nom,
                cout_emballage_ht,
                emballage_id,
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

    def cout_emballage_effectif(self, famille_id):
        """
        Renvoie le coût d'emballage réellement utilisé :
        celui de l'emballage lié (emballage + calage) si
        renseigné, sinon le coût manuel de la famille.
        """

        famille = self.obtenir(famille_id)

        if famille is None:
            return 0

        if famille["emballage_id"] is not None:
            return self.emballages.cout_total(famille["emballage_id"])

        return famille["cout_emballage_ht"] or 0

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

        cout_emballage = self.cout_emballage_effectif(famille_id)

        base = (prix_achat_ht or 0) + cout_emballage

        return base * (1 + (famille["taux_retour"] or 0))