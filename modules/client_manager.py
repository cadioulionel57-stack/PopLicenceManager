from database.database import Database


class ClientManager:
    """
    Gère les clients — rattachés aux commandes. Pas de
    notion "actif/inactif" ici : un client ne se désactive
    pas comme une référence produit.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM clients
            ORDER BY nom, prenom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM clients
            WHERE id = ?
            """,
            (identifiant,)
        )

    def trouver_par_email(self, email):

        if not email:
            return None

        return self.db.lire_un(
            """
            SELECT *
            FROM clients
            WHERE email = ?
            """,
            (email,)
        )

    def ajouter(
        self,
        nom,
        prenom="",
        societe="",
        email="",
        telephone="",
        adresse="",
        code_postal="",
        ville="",
        pays="France"
    ):

        curseur = self.db.executer(
            """
            INSERT INTO clients
            (
                nom, prenom, societe, email, telephone,
                adresse, code_postal, ville, pays
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                nom, prenom, societe, email, telephone,
                adresse, code_postal, ville, pays
            )
        )

        return curseur.lastrowid

    def obtenir_ou_creer(
        self,
        nom,
        prenom="",
        email="",
        telephone="",
        adresse="",
        code_postal="",
        ville="",
        pays="France"
    ):
        """
        Réutilise le client existant si l'email correspond
        déjà à quelqu'un (évite les doublons lors d'imports
        répétés du même client) — sinon en crée un nouveau.
        """

        existant = self.trouver_par_email(email)

        if existant is not None:
            return existant["id"]

        return self.ajouter(
            nom, prenom, "", email, telephone,
            adresse, code_postal, ville, pays
        )

    def modifier(
        self,
        identifiant,
        nom,
        prenom="",
        societe="",
        email="",
        telephone="",
        adresse="",
        code_postal="",
        ville="",
        pays="France"
    ):

        self.db.executer(
            """
            UPDATE clients
            SET
                nom = ?, prenom = ?, societe = ?, email = ?,
                telephone = ?, adresse = ?, code_postal = ?,
                ville = ?, pays = ?
            WHERE id = ?
            """,
            (
                nom, prenom, societe, email, telephone,
                adresse, code_postal, ville, pays,
                identifiant
            )
        )