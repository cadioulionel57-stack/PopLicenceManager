from database.database import Database


class BudgetPublicitaireManager:
    """
    Gère les enveloppes de budget publicitaire (Google
    Shopping, Google Search, Amazon Ads, Agence SEA...) et
    les dépenses réelles saisies librement mois par mois —
    aucune répartition automatique imposée, tu décides
    toi-même combien tu dépenses chaque mois, le logiciel se
    contente de comparer le cumul à l'enveloppe totale.
    """

    def __init__(self):

        self.db = Database()

    ########################################################
    # Lignes de budget (les enveloppes)
    ########################################################

    def lignes(self):

        return self.db.lire(
            """
            SELECT *
            FROM budget_publicitaire_lignes
            WHERE actif = 1
            ORDER BY nom
            """
        )

    def obtenir_ligne(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM budget_publicitaire_lignes
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter_ligne(self, nom, enveloppe_totale_ht, date_debut, date_fin):

        curseur = self.db.executer(
            """
            INSERT INTO budget_publicitaire_lignes
            (nom, enveloppe_totale_ht, date_debut, date_fin, actif)
            VALUES (?, ?, ?, ?, 1)
            """,
            (nom, enveloppe_totale_ht, date_debut, date_fin)
        )

        return curseur.lastrowid

    def modifier_ligne(
        self, identifiant, nom, enveloppe_totale_ht, date_debut, date_fin
    ):

        self.db.executer(
            """
            UPDATE budget_publicitaire_lignes
            SET nom = ?, enveloppe_totale_ht = ?,
                date_debut = ?, date_fin = ?
            WHERE id = ?
            """,
            (nom, enveloppe_totale_ht, date_debut, date_fin, identifiant)
        )

    def supprimer_ligne(self, identifiant):

        self.db.executer(
            """
            UPDATE budget_publicitaire_lignes
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    ########################################################
    # Dépenses réelles, mois par mois
    ########################################################

    def depenses_ligne(self, ligne_id):

        return self.db.lire(
            """
            SELECT *
            FROM depenses_publicitaires
            WHERE ligne_id = ?
            AND actif = 1
            ORDER BY mois
            """,
            (ligne_id,)
        )

    def definir_depense_mois(self, ligne_id, mois_iso, montant_ht):
        """
        Enregistre (ou met à jour) la dépense réelle d'une
        ligne pour un mois donné.
        """

        existe = self.db.lire_un(
            """
            SELECT id
            FROM depenses_publicitaires
            WHERE ligne_id = ?
            AND mois = ?
            """,
            (ligne_id, mois_iso)
        )

        if existe is not None:

            self.db.executer(
                """
                UPDATE depenses_publicitaires
                SET montant_reel_ht = ?
                WHERE id = ?
                """,
                (montant_ht, existe["id"])
            )

        else:

            self.db.executer(
                """
                INSERT INTO depenses_publicitaires
                (ligne_id, mois, montant_reel_ht, actif)
                VALUES (?, ?, ?, 1)
                """,
                (ligne_id, mois_iso, montant_ht)
            )

    def total_depense(self, ligne_id):

        lignes = self.depenses_ligne(ligne_id)

        return round(
            sum(l["montant_reel_ht"] or 0 for l in lignes), 2
        )

    def synthese(self):
        """
        Pour chaque ligne : enveloppe totale, dépensé à ce
        jour, restant, et pourcentage consommé.
        """

        resultat = []

        for ligne in self.lignes():

            depense = self.total_depense(ligne["id"])
            enveloppe = ligne["enveloppe_totale_ht"] or 0
            restant = enveloppe - depense

            pourcentage = (
                round((depense / enveloppe) * 100, 1)
                if enveloppe > 0 else 0
            )

            resultat.append({
                "ligne": dict(ligne),
                "depense_ht": depense,
                "restant_ht": round(restant, 2),
                "pourcentage_consomme": pourcentage,
            })

        return resultat