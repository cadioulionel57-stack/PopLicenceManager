from database.database import Database


class FournisseurCanalManager:
    """
    Autorisation de revente par fournisseur ET par canal.

    Certains fournisseurs interdisent la revente sur les
    marketplaces, parfois seulement sur certaines d'entre
    elles (Amazon autorisé, Cdiscount interdit). Ce n'est
    donc pas un oui/non sur la fiche fournisseur, mais une
    autorisation par couple fournisseur × canal.

    Règle de lecture : ce qui n'est pas enregistré est
    AUTORISÉ. Un fournisseur pour lequel on n'a rien dit
    reste vendable partout — sinon l'ajout de ce module
    bloquerait d'un coup tous les produits existants.

    Le canal "Site" n'est jamais concerné : la boutique
    reste toujours ouverte, l'interdiction ne porte que sur
    les marketplaces.
    """

    def __init__(self):

        self.db = Database()

        self.creer_table()

    def creer_table(self):
        """
        Crée la table si elle n'existe pas encore.

        Volontairement ici et pas dans schema.py : ce module
        est autonome, il ne dépend d'aucune modification des
        fichiers de base du logiciel.
        """

        self.db.executer(
            """
            CREATE TABLE IF NOT EXISTS fournisseurs_canaux
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fournisseur_id INTEGER NOT NULL,
                canal_id INTEGER NOT NULL,
                autorise INTEGER DEFAULT 1,
                UNIQUE (fournisseur_id, canal_id)
            )
            """
        )

    # ------------------------------------------------------
    # Lecture
    # ------------------------------------------------------

    def canaux_marketplace(self):
        """
        Liste des canaux concernés par une autorisation :
        les marketplaces actives, jamais le canal Site.
        """

        return self.db.lire(
            """
            SELECT id, nom, couleur
            FROM canaux_vente
            WHERE type = 'marketplace'
            AND actif = 1
            ORDER BY nom
            """
        )

    def autorisations(self, fournisseur_id):
        """
        Renvoie un dictionnaire {canal_id: True/False} pour
        ce fournisseur.

        Les canaux jamais enregistrés sont absents du
        dictionnaire — donc autorisés par défaut.
        """

        resultat = {}

        if fournisseur_id is None:
            return resultat

        lignes = self.db.lire(
            """
            SELECT canal_id, autorise
            FROM fournisseurs_canaux
            WHERE fournisseur_id = ?
            """,
            (fournisseur_id,)
        )

        for ligne in lignes:
            resultat[ligne["canal_id"]] = bool(ligne["autorise"])

        return resultat

    def est_autorise(self, fournisseur_id, canal_id):
        """
        Réponse directe pour un couple donné.

        Renvoie True si rien n'a jamais été enregistré.
        """

        if fournisseur_id is None or canal_id is None:
            return True

        ligne = self.db.lire_un(
            """
            SELECT autorise
            FROM fournisseurs_canaux
            WHERE fournisseur_id = ?
            AND canal_id = ?
            """,
            (fournisseur_id, canal_id)
        )

        if ligne is None:
            return True

        return bool(ligne["autorise"])

    def canaux_interdits(self, fournisseur_id):
        """
        Liste des noms de canaux interdits pour ce
        fournisseur — pour l'afficher à l'écran.
        """

        interdits = []

        autorisations = self.autorisations(fournisseur_id)

        for canal in self.canaux_marketplace():

            if autorisations.get(canal["id"], True) is False:
                interdits.append(canal["nom"])

        return interdits

    def tout_interdit(self, fournisseur_id):
        """
        Vrai si AUCUNE marketplace n'est autorisée.

        Sert à basculer automatiquement le type de SKU en
        NMKPS à la création d'un produit.
        """

        canaux = self.canaux_marketplace()

        if not canaux:
            return False

        autorisations = self.autorisations(fournisseur_id)

        for canal in canaux:

            if autorisations.get(canal["id"], True):
                return False

        return True

    # ------------------------------------------------------
    # Écriture
    # ------------------------------------------------------

    def enregistrer(self, fournisseur_id, autorisations):
        """
        Enregistre les autorisations d'un fournisseur.

        autorisations : dictionnaire {canal_id: True/False}

        On écrit TOUTES les lignes, y compris les autorisées,
        pour que l'écran affiche l'état réellement choisi et
        non un défaut implicite.
        """

        if fournisseur_id is None:
            return

        for canal_id, autorise in autorisations.items():

            self.db.executer(
                """
                INSERT INTO fournisseurs_canaux
                (fournisseur_id, canal_id, autorise)
                VALUES (?, ?, ?)
                ON CONFLICT (fournisseur_id, canal_id)
                DO UPDATE SET autorise = excluded.autorise
                """,
                (fournisseur_id, canal_id, 1 if autorise else 0)
            )