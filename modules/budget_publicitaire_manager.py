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

    def total_depense_mois(self, mois_iso):
        """
        Dépense publicitaire totale, toutes lignes
        confondues, pour un mois précis.
        """

        total = self.db.lire_un(
            """
            SELECT SUM(montant_reel_ht) AS total
            FROM depenses_publicitaires
            WHERE mois = ?
            AND actif = 1
            """,
            (mois_iso,)
        )

        return round(total["total"] or 0, 2)

    def mois_avec_depenses(self):
        """
        Tous les mois (AAAA-MM) où au moins une dépense
        publicitaire a été saisie, triés chronologiquement —
        sert de base pour comparer avec le CA du même mois.
        """

        lignes = self.db.lire(
            """
            SELECT DISTINCT mois
            FROM depenses_publicitaires
            WHERE actif = 1
            ORDER BY mois
            """
        )

        return [l["mois"] for l in lignes]

    def evolution_ca_vs_pub(self):
        """
        Pour chaque mois où de la pub a été dépensée : le
        montant dépensé, le CA du même mois, et le ROAS
        (Return On Ad Spend = CA ÷ dépense pub — un ROAS de
        4 veut dire que chaque euro de pub a rapporté 4€ de
        CA).
        """

        from modules.commande_manager import CommandeManager

        commande_manager = CommandeManager()

        resultat = []

        for mois in self.mois_avec_depenses():

            depense = self.total_depense_mois(mois)

            import calendar

            annee, num_mois = (int(x) for x in mois.split("-"))
            dernier_jour = calendar.monthrange(annee, num_mois)[1]

            date_debut = f"{mois}-01"
            date_fin = f"{mois}-{dernier_jour:02d}"

            ca = commande_manager.ca_periode(date_debut, date_fin)

            roas = round(ca / depense, 2) if depense > 0 else None

            resultat.append({
                "mois": mois,
                "depense_pub_ht": depense,
                "ca_ht": ca,
                "roas": roas,
            })

        return resultat

    def niveau_alerte(self, pourcentage):
        """
        'normal' en dessous de 80%, 'attention' entre 80 et
        100%, 'depasse' au-delà de 100%.
        """

        if pourcentage >= 100:
            return "depasse"

        if pourcentage >= 80:
            return "attention"

        return "normal"

    def total_restant_global(self):
        """
        Somme du restant sur toutes les lignes actives —
        pour savoir en un chiffre combien de budget pub il
        te reste au total, sans avoir à additionner chaque
        ligne toi-même.
        """

        return round(
            sum(item["restant_ht"] for item in self.synthese()), 2
        )

    def synthese(self):
        """
        Pour chaque ligne : enveloppe totale, dépensé à ce
        jour, restant, pourcentage consommé, niveau d'alerte,
        et le CA généré par ses canaux liés actifs (avec le
        ROAS correspondant).
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

            ca_canaux = self.ca_canaux_ligne(ligne["id"])
            roas_canaux = (
                round(ca_canaux / depense, 2) if depense > 0 else None
            )

            resultat.append({
                "ligne": dict(ligne),
                "depense_ht": depense,
                "restant_ht": round(restant, 2),
                "pourcentage_consomme": pourcentage,
                "niveau_alerte": self.niveau_alerte(pourcentage),
                "ca_canaux_ht": ca_canaux,
                "roas_canaux": roas_canaux,
            })

        return resultat

    ########################################################
    # Canaux liés à une ligne de budget
    ########################################################

    def canaux_lies(self, ligne_id):
        """
        Tous les canaux liés à cette ligne de budget, avec
        leur statut actif/inactif — un canal peut être lié
        sans être compté tout de suite (ex : Amazon FBA lié
        à "Amazon Ads" mais pas encore utilisé).
        """

        return self.db.lire(
            """
            SELECT
                bpc.id AS lien_id,
                bpc.canal_id,
                bpc.actif,
                cv.nom AS nom_canal
            FROM budget_publicitaire_canaux bpc

            INNER JOIN canaux_vente cv
                ON cv.id = bpc.canal_id

            WHERE bpc.ligne_id = ?

            ORDER BY cv.nom
            """,
            (ligne_id,)
        )

    def ajouter_canal_ligne(self, ligne_id, canal_id):

        existe = self.db.lire_un(
            """
            SELECT id
            FROM budget_publicitaire_canaux
            WHERE ligne_id = ?
            AND canal_id = ?
            """,
            (ligne_id, canal_id)
        )

        if existe is not None:
            return existe["id"]

        curseur = self.db.executer(
            """
            INSERT INTO budget_publicitaire_canaux
            (ligne_id, canal_id, actif)
            VALUES (?, ?, 1)
            """,
            (ligne_id, canal_id)
        )

        return curseur.lastrowid

    def basculer_actif_canal(self, lien_id, actif):

        self.db.executer(
            """
            UPDATE budget_publicitaire_canaux
            SET actif = ?
            WHERE id = ?
            """,
            (1 if actif else 0, lien_id)
        )

    def retirer_canal_ligne(self, lien_id):

        self.db.executer(
            """
            DELETE FROM budget_publicitaire_canaux
            WHERE id = ?
            """,
            (lien_id,)
        )

    def ca_canaux_ligne(self, ligne_id, date_debut=None, date_fin=None):
        """
        CA généré par les canaux actifs liés à cette ligne,
        sur la période de la ligne (ou une période précise
        si fournie) — sert à calculer le vrai ROAS par canal,
        pas juste le ROAS global tous canaux confondus.
        """

        ligne = self.obtenir_ligne(ligne_id)

        if ligne is None:
            return 0

        date_debut = date_debut or f"{ligne['date_debut']}-01"

        if date_fin is None:

            if ligne["date_fin"]:
                import calendar
                annee, mois = (int(x) for x in ligne["date_fin"].split("-"))
                dernier_jour = calendar.monthrange(annee, mois)[1]
                date_fin = f"{ligne['date_fin']}-{dernier_jour:02d}"
            else:
                from datetime import date
                date_fin = date.today().isoformat()

        canaux_actifs = [
            c["canal_id"] for c in self.canaux_lies(ligne_id)
            if c["actif"]
        ]

        if not canaux_actifs:
            return 0

        from modules.commande_manager import CommandeManager

        commande_manager = CommandeManager()

        placeholders = ",".join("?" * len(canaux_actifs))

        commandes = self.db.lire(
            f"""
            SELECT id
            FROM commandes
            WHERE actif = 1
            AND canal_id IN ({placeholders})
            AND date_commande >= ?
            AND date_commande <= ?
            """,
            (*canaux_actifs, date_debut, date_fin)
        )

        total = sum(
            commande_manager.chiffre_affaires_ht(c["id"])
            for c in commandes
        )

        return round(total, 2)

    ########################################################
    # Périodes commerciales (Noël, Rentrée...)
    ########################################################

    def periodes(self):

        return self.db.lire(
            """
            SELECT *
            FROM periodes_commerciales
            WHERE actif = 1
            ORDER BY date_debut DESC
            """
        )

    def obtenir_periode(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM periodes_commerciales
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter_periode(
        self, nom, date_debut, date_fin, budget_supplementaire_ht=0
    ):

        curseur = self.db.executer(
            """
            INSERT INTO periodes_commerciales
            (nom, date_debut, date_fin, budget_supplementaire_ht, actif)
            VALUES (?, ?, ?, ?, 1)
            """,
            (nom, date_debut, date_fin, budget_supplementaire_ht)
        )

        return curseur.lastrowid

    def modifier_periode(
        self, identifiant, nom, date_debut, date_fin,
        budget_supplementaire_ht=0
    ):

        self.db.executer(
            """
            UPDATE periodes_commerciales
            SET nom = ?, date_debut = ?, date_fin = ?,
                budget_supplementaire_ht = ?
            WHERE id = ?
            """,
            (nom, date_debut, date_fin, budget_supplementaire_ht,
             identifiant)
        )

    def supprimer_periode(self, identifiant):

        self.db.executer(
            """
            UPDATE periodes_commerciales
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def depense_pub_periode(self, periode):
        """
        Dépense publicitaire déjà saisie mois par mois qui
        tombe dans les dates de la période, tous canaux
        confondus + le budget supplémentaire alloué
        spécifiquement à cette période.

        Un mois est considéré "dans la période" dès qu'il en
        chevauche une partie (ex : Noël du 15 nov au 5 jan
        inclut novembre, décembre et janvier en entier —
        approximation au mois, cohérente avec le fait que la
        dépense elle-même n'est saisie qu'au mois près).
        """

        annee_debut, mois_debut = (
            int(x) for x in periode["date_debut"][:7].split("-")
        )
        annee_fin, mois_fin = (
            int(x) for x in periode["date_fin"][:7].split("-")
        )

        mois_periode = []
        annee, mois = annee_debut, mois_debut

        while (annee, mois) <= (annee_fin, mois_fin):

            mois_periode.append(f"{annee}-{mois:02d}")

            mois += 1
            if mois > 12:
                mois = 1
                annee += 1

        total_depense_pub = 0

        for mois_iso in mois_periode:
            total_depense_pub += self.total_depense_mois(mois_iso)

        supplement = periode["budget_supplementaire_ht"] or 0

        return round(total_depense_pub + supplement, 2)

    def ca_periode_commerciale(self, periode):

        from modules.commande_manager import CommandeManager

        return CommandeManager().ca_periode(
            periode["date_debut"], periode["date_fin"]
        )

    def synthese_periodes(self):
        """
        Pour chaque période : dépense pub (saisie + supplé-
        ment), CA généré sur les mêmes dates, et le ROI
        (retour sur investissement de cette période précise).
        """

        resultat = []

        for periode in self.periodes():

            depense = self.depense_pub_periode(periode)
            ca = self.ca_periode_commerciale(periode)

            roas = round(ca / depense, 2) if depense > 0 else None

            resultat.append({
                "periode": dict(periode),
                "depense_pub_ht": depense,
                "ca_ht": ca,
                "roas": roas,
            })

        return resultat