from database.database import Database


class AttributManager:

    def __init__(self):

        self.db = Database()

    ########################################################
    # Critères
    ########################################################

    def attributs(self, actifs_seulement=False):
        """
        Liste des critères, avec le nombre de valeurs de
        chacun — pour l'afficher sans requête supplémentaire.
        """

        condition = "WHERE a.actif = 1" if actifs_seulement else ""

        return self.db.lire(f"""
            SELECT a.*,
                   (
                       SELECT COUNT(*)
                       FROM valeurs_attributs v
                       WHERE v.attribut_id = a.id
                         AND v.actif = 1
                   ) AS nombre_valeurs
            FROM attributs a
            {condition}
            ORDER BY a.nom
        """)

    def obtenir_attribut(self, identifiant):

        return self.db.lire_un(
            "SELECT * FROM attributs WHERE id = ?", (identifiant,)
        )

    def ajouter_attribut(self, nom, type_attribut="liste"):
        """
        Crée un critère. Renvoie son identifiant, ou celui du
        critère existant si le nom est déjà pris — on ne crée
        jamais deux « Couleur ».
        """

        nom = (nom or "").strip()

        if not nom:
            raise ValueError("Le nom du critère est obligatoire.")

        existant = self.db.lire_un(
            "SELECT id, actif FROM attributs WHERE nom = ?", (nom,)
        )

        if existant is not None:

            if not existant["actif"]:
                self.db.executer(
                    "UPDATE attributs SET actif = 1 WHERE id = ?",
                    (existant["id"],)
                )

            return existant["id"]

        curseur = self.db.executer(
            "INSERT INTO attributs (nom, type, actif) VALUES (?, ?, 1)",
            (nom, type_attribut)
        )

        return curseur.lastrowid

    def modifier_attribut(self, identifiant, nom, actif=True):

        nom = (nom or "").strip()

        if not nom:
            raise ValueError("Le nom du critère est obligatoire.")

        double = self.db.lire_un(
            "SELECT id FROM attributs WHERE nom = ? AND id != ?",
            (nom, identifiant)
        )

        if double is not None:
            raise ValueError(f"Un critère « {nom} » existe déjà.")

        self.db.executer(
            "UPDATE attributs SET nom = ?, actif = ? WHERE id = ?",
            (nom, 1 if actif else 0, identifiant)
        )

    def attribut_utilise(self, identifiant):
        """
        Nombre de variations produit qui s'appuient sur ce
        critère. Sert à empêcher une suppression qui casserait
        des références existantes.
        """

        ligne = self.db.lire_un("""
            SELECT COUNT(*) AS total
            FROM variations_valeurs
            WHERE attribut_id = ?
        """, (identifiant,))

        return ligne["total"] if ligne else 0

    def supprimer_attribut(self, identifiant):
        """
        Supprime un critère et ses valeurs. Refuse si des
        variations l'utilisent : on ne casse jamais une
        référence déjà vendue.
        """

        if self.attribut_utilise(identifiant) > 0:
            raise ValueError(
                "Ce critère est utilisé par des variations de "
                "produits. Désactive-le plutôt que de le "
                "supprimer."
            )

        self.db.executer(
            "DELETE FROM valeurs_attributs WHERE attribut_id = ?",
            (identifiant,)
        )
        self.db.executer(
            "DELETE FROM attributs WHERE id = ?", (identifiant,)
        )

    ########################################################
    # Valeurs
    ########################################################

    def valeurs(self, attribut_id, actives_seulement=False):

        condition = "AND actif = 1" if actives_seulement else ""

        return self.db.lire(f"""
            SELECT * FROM valeurs_attributs
            WHERE attribut_id = ? {condition}
            ORDER BY ordre, valeur
        """, (attribut_id,))

    def ajouter_valeur(self, attribut_id, valeur):

        valeur = (valeur or "").strip()

        if not valeur:
            raise ValueError("La valeur est obligatoire.")

        existante = self.db.lire_un("""
            SELECT id, actif FROM valeurs_attributs
            WHERE attribut_id = ? AND valeur = ?
        """, (attribut_id, valeur))

        if existante is not None:

            if not existante["actif"]:
                self.db.executer(
                    "UPDATE valeurs_attributs SET actif = 1 WHERE id = ?",
                    (existante["id"],)
                )

            return existante["id"]

        # La nouvelle valeur se range en dernier.
        dernier = self.db.lire_un("""
            SELECT MAX(ordre) AS rang FROM valeurs_attributs
            WHERE attribut_id = ?
        """, (attribut_id,))

        rang = (dernier["rang"] or 0) + 1

        curseur = self.db.executer("""
            INSERT INTO valeurs_attributs
                (attribut_id, valeur, ordre, actif)
            VALUES (?, ?, ?, 1)
        """, (attribut_id, valeur, rang))

        return curseur.lastrowid

    def modifier_valeur(self, identifiant, valeur, actif=True):

        valeur = (valeur or "").strip()

        if not valeur:
            raise ValueError("La valeur est obligatoire.")

        ligne = self.db.lire_un(
            "SELECT attribut_id FROM valeurs_attributs WHERE id = ?",
            (identifiant,)
        )

        if ligne is None:
            return

        double = self.db.lire_un("""
            SELECT id FROM valeurs_attributs
            WHERE attribut_id = ? AND valeur = ? AND id != ?
        """, (ligne["attribut_id"], valeur, identifiant))

        if double is not None:
            raise ValueError(f"La valeur « {valeur} » existe déjà.")

        self.db.executer("""
            UPDATE valeurs_attributs SET valeur = ?, actif = ?
            WHERE id = ?
        """, (valeur, 1 if actif else 0, identifiant))

    def valeur_utilisee(self, identifiant):

        ligne = self.db.lire_un("""
            SELECT COUNT(*) AS total
            FROM variations_valeurs
            WHERE valeur_id = ?
        """, (identifiant,))

        return ligne["total"] if ligne else 0

    def supprimer_valeur(self, identifiant):

        if self.valeur_utilisee(identifiant) > 0:
            raise ValueError(
                "Cette valeur est utilisée par des variations "
                "de produits. Désactive-la plutôt que de la "
                "supprimer."
            )

        self.db.executer(
            "DELETE FROM valeurs_attributs WHERE id = ?", (identifiant,)
        )

    def deplacer_valeur(self, identifiant, sens):
        """
        Monte (sens = -1) ou descend (sens = +1) une valeur
        dans la liste, en échangeant son rang avec celui de
        sa voisine.
        """

        courante = self.db.lire_un(
            "SELECT * FROM valeurs_attributs WHERE id = ?", (identifiant,)
        )

        if courante is None:
            return

        liste = self.valeurs(courante["attribut_id"])

        positions = [v["id"] for v in liste]

        if identifiant not in positions:
            return

        index = positions.index(identifiant)
        cible = index + sens

        if cible < 0 or cible >= len(liste):
            return

        voisine = liste[cible]

        # Les rangs peuvent être identiques ou nuls sur
        # d'anciennes données : on réécrit toute la liste
        # dans le nouvel ordre plutôt que d'échanger deux
        # valeurs, ce qui serait sans effet.
        nouvel_ordre = list(positions)
        nouvel_ordre[index], nouvel_ordre[cible] = (
            nouvel_ordre[cible], nouvel_ordre[index]
        )

        for rang, valeur_id in enumerate(nouvel_ordre, start=1):
            self.db.executer(
                "UPDATE valeurs_attributs SET ordre = ? WHERE id = ?",
                (rang, valeur_id)
            )