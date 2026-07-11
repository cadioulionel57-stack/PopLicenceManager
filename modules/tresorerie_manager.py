from datetime import date

from database.database import Database


class TresorerieManager:
    """
    Gère la trésorerie : solde du jour, charges récurrentes
    (loyer, abonnements, prêt, crédit TVA...) et leurs
    paiements mensuels, et le Fonds de Croissance (la seule
    des 3 "enveloppes" à réellement accumuler dans le temps
    — Développement et Réserve restent de simples
    pourcentages du solde actuel, recalculés à la volée).
    """

    def __init__(self):

        self.db = Database()

    ########################################################
    # Solde journalier
    ########################################################

    def definir_solde_jour(self, date_iso, solde_ttc):
        """
        Enregistre (ou met à jour) le solde bancaire pour
        une date donnée.
        """

        existe = self.db.lire_un(
            """
            SELECT id
            FROM soldes_journaliers
            WHERE date = ?
            """,
            (date_iso,)
        )

        if existe is not None:

            self.db.executer(
                """
                UPDATE soldes_journaliers
                SET solde_ttc = ?
                WHERE date = ?
                """,
                (solde_ttc, date_iso)
            )

        else:

            self.db.executer(
                """
                INSERT INTO soldes_journaliers
                (date, solde_ttc, actif)
                VALUES (?, ?, 1)
                """,
                (date_iso, solde_ttc)
            )

    def solde_actuel(self):
        """
        Dernier solde saisi (le plus récent), ou None si
        rien n'a encore été renseigné.
        """

        ligne = self.db.lire_un(
            """
            SELECT solde_ttc
            FROM soldes_journaliers
            WHERE actif = 1
            ORDER BY date DESC
            LIMIT 1
            """
        )

        return ligne["solde_ttc"] if ligne else None

    def solde_jour(self, date_iso):

        ligne = self.db.lire_un(
            """
            SELECT solde_ttc
            FROM soldes_journaliers
            WHERE date = ?
            """,
            (date_iso,)
        )

        return ligne["solde_ttc"] if ligne else None

    def historique_soldes(self, limite=30):

        return self.db.lire(
            """
            SELECT *
            FROM soldes_journaliers
            WHERE actif = 1
            ORDER BY date DESC
            LIMIT ?
            """,
            (limite,)
        )

    ########################################################
    # Charges récurrentes
    ########################################################

    def charges(self):

        return self.db.lire(
            """
            SELECT *
            FROM charges_recurrentes
            WHERE actif = 1
            ORDER BY categorie, nom
            """
        )

    def obtenir_charge(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM charges_recurrentes
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter_charge(
        self, nom, categorie, montant_mensuel,
        mois_debut, nombre_occurrences=None, frequence="mensuelle",
        tva_applicable=True,
    ):

        curseur = self.db.executer(
            """
            INSERT INTO charges_recurrentes
            (nom, categorie, frequence, tva_applicable,
             montant_mensuel, mois_debut, nombre_occurrences, actif)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (nom, categorie, frequence, 1 if tva_applicable else 0,
             montant_mensuel, mois_debut, nombre_occurrences)
        )

        return curseur.lastrowid

    def modifier_charge(
        self, identifiant, nom, categorie, montant_mensuel,
        mois_debut, nombre_occurrences=None, frequence="mensuelle",
        tva_applicable=True,
    ):

        self.db.executer(
            """
            UPDATE charges_recurrentes
            SET nom = ?, categorie = ?, frequence = ?,
                tva_applicable = ?, montant_mensuel = ?,
                mois_debut = ?, nombre_occurrences = ?
            WHERE id = ?
            """,
            (nom, categorie, frequence, 1 if tva_applicable else 0,
             montant_mensuel, mois_debut, nombre_occurrences, identifiant)
        )

    def supprimer_charge(self, identifiant):

        self.db.executer(
            """
            UPDATE charges_recurrentes
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def charge_active_ce_mois(self, charge, mois_iso):
        """
        Une charge mensuelle est due chaque mois. Une charge
        annuelle n'est due qu'une fois par an, le même mois
        que sa première échéance (ex : assurance payée
        chaque mois de mars).

        Une charge à durée déterminée (prêt, crédit TVA...)
        n'est due que pendant sa fenêtre d'échéances — au-
        delà, elle ne doit plus apparaître comme charge du
        mois.
        """

        if not charge["mois_debut"]:
            return True

        debut_annee, debut_mois = (
            int(x) for x in charge["mois_debut"].split("-")
        )
        cette_annee, ce_mois = (
            int(x) for x in mois_iso.split("-")
        )

        if charge["frequence"] == "annuelle":

            if ce_mois != debut_mois:
                return False

            if charge["nombre_occurrences"] is None:
                return cette_annee >= debut_annee

            index_annee = cette_annee - debut_annee

            return 0 <= index_annee < charge["nombre_occurrences"]

        if charge["nombre_occurrences"] is None:
            return True

        index_mois = (
            (cette_annee - debut_annee) * 12
            + (ce_mois - debut_mois)
        )

        return 0 <= index_mois < charge["nombre_occurrences"]

    def charges_du_mois(self, mois_iso=None):
        """
        Renvoie chaque charge active ce mois précis, avec
        son statut de paiement pour ce mois.
        """

        mois_iso = mois_iso or date.today().strftime("%Y-%m")

        resultat = []

        for charge in self.charges():

            if not self.charge_active_ce_mois(charge, mois_iso):
                continue

            paiement = self.db.lire_un(
                """
                SELECT *
                FROM paiements_charges
                WHERE charge_id = ?
                AND mois = ?
                """,
                (charge["id"], mois_iso)
            )

            resultat.append({
                "charge": dict(charge),
                "paye": bool(paiement["paye"]) if paiement else False,
                "paiement_id": paiement["id"] if paiement else None,
            })

        return resultat

    def marquer_paye(self, charge_id, mois_iso, paye=True):

        existe = self.db.lire_un(
            """
            SELECT id
            FROM paiements_charges
            WHERE charge_id = ?
            AND mois = ?
            """,
            (charge_id, mois_iso)
        )

        date_paiement = date.today().isoformat() if paye else None

        if existe is not None:

            self.db.executer(
                """
                UPDATE paiements_charges
                SET paye = ?, date_paiement = ?
                WHERE id = ?
                """,
                (1 if paye else 0, date_paiement, existe["id"])
            )

        else:

            self.db.executer(
                """
                INSERT INTO paiements_charges
                (charge_id, mois, paye, date_paiement)
                VALUES (?, ?, ?, ?)
                """,
                (charge_id, mois_iso, 1 if paye else 0, date_paiement)
            )

    def total_charges_mois(self, mois_iso=None):

        lignes = self.charges_du_mois(mois_iso)

        total = sum(l["charge"]["montant_mensuel"] or 0 for l in lignes)
        paye = sum(
            l["charge"]["montant_mensuel"] or 0
            for l in lignes if l["paye"]
        )
        restant = total - paye

        return {
            "total": round(total, 2),
            "paye": round(paye, 2),
            "restant": round(restant, 2),
        }

    def tva_deductible_charges(self, mois_iso=None):
        """
        TVA déductible sur les charges du mois réellement
        payées, au taux standard 20% — uniquement pour
        celles marquées "TVA applicable" (le remboursement
        de prêt ou le crédit relais TVA n'en génèrent pas).

        Le montant renseigné pour une charge est considéré
        HT.
        """

        TAUX_TVA = 0.20

        lignes = self.charges_du_mois(mois_iso)

        base_ht = sum(
            l["charge"]["montant_mensuel"] or 0
            for l in lignes
            if l["paye"] and l["charge"]["tva_applicable"]
        )

        return round(base_ht * TAUX_TVA, 2)

    ########################################################
    # Les 3 fonds
    ########################################################

    def fonds_developpement(self):
        """30% du solde actuel, recalculé en direct."""

        solde = self.solde_actuel() or 0

        return round(solde * 0.30, 2)

    def reserve_tresorerie(self):
        """40% du solde actuel, recalculé en direct."""

        solde = self.solde_actuel() or 0

        return round(solde * 0.40, 2)

    ########################################################
    # Renouvellement Stock
    ########################################################

    def _obtenir_renouvellement_stock(self):

        ligne = self.db.lire_un(
            """
            SELECT * FROM renouvellement_stock LIMIT 1
            """
        )

        if ligne is None:

            self.db.executer(
                """
                INSERT INTO renouvellement_stock (ajustement_manuel)
                VALUES (0)
                """
            )

            ligne = self.db.lire_un(
                """
                SELECT * FROM renouvellement_stock LIMIT 1
                """
            )

        return ligne

    def ajustement_manuel_stock(self):

        return self._obtenir_renouvellement_stock()["ajustement_manuel"] or 0

    def definir_ajustement_manuel_stock(self, montant):
        """
        Fixe l'ajustement manuel libre (positif pour ajouter
        une somme au Renouvellement Stock, négatif pour en
        retirer).
        """

        ligne = self._obtenir_renouvellement_stock()

        self.db.executer(
            """
            UPDATE renouvellement_stock
            SET ajustement_manuel = ?
            WHERE id = ?
            """,
            (montant, ligne["id"])
        )

    def renouvellement_stock_total(self):
        """
        Coût d'achat cumulé de tout ce qui a été vendu
        (calculé en direct depuis les commandes) + ajustement
        manuel libre.
        """

        from modules.commande_manager import CommandeManager

        cout_ventes = CommandeManager().total_cout_achat_vendu()
        ajustement = self.ajustement_manuel_stock()

        return round(cout_ventes + ajustement, 2)

    def _obtenir_fonds_croissance(self):

        ligne = self.db.lire_un(
            """
            SELECT *
            FROM fonds_croissance
            LIMIT 1
            """
        )

        if ligne is None:

            self.db.executer(
                """
                INSERT INTO fonds_croissance
                (montant_actuel, dernier_mois_alimente)
                VALUES (0, NULL)
                """
            )

            ligne = self.db.lire_un(
                """
                SELECT * FROM fonds_croissance LIMIT 1
                """
            )

        return ligne

    def fonds_deja_initialise(self):

        return bool(self._obtenir_fonds_croissance()["initialise"])

    def initialiser_fonds_croissance(self, montant_depart):
        """
        Amorce la cagnotte à 30% du solde de départ — à
        n'appliquer qu'une seule fois, à la toute première
        saisie de solde. Si la cotisation mensuelle de 5% a
        déjà eu lieu avant cette initialisation, elle est
        conservée et le montant de départ vient s'AJOUTER,
        pas écraser ce qui existe déjà.
        """

        fonds = self._obtenir_fonds_croissance()

        montant_base = round(montant_depart * 0.30, 2)

        nouveau_montant = (fonds["montant_actuel"] or 0) + montant_base

        self.db.executer(
            """
            UPDATE fonds_croissance
            SET montant_actuel = ?, initialise = 1
            WHERE id = ?
            """,
            (nouveau_montant, fonds["id"])
        )

    def fonds_croissance_actuel(self):

        return self._obtenir_fonds_croissance()["montant_actuel"] or 0

    def alimenter_fonds_croissance_mensuel(self, benefice_du_mois, mois_iso=None):
        """
        Verse 5% du bénéfice du mois dans la cagnotte — une
        seule fois par mois (vérifie qu'elle n'a pas déjà
        été alimentée ce mois-ci, pour ne jamais verser deux
        fois si le logiciel est relancé plusieurs fois dans
        le même mois).
        """

        mois_iso = mois_iso or date.today().strftime("%Y-%m")

        fonds = self._obtenir_fonds_croissance()

        if fonds["dernier_mois_alimente"] == mois_iso:
            return False

        apport = round(benefice_du_mois * 0.05, 2)

        nouveau_montant = (fonds["montant_actuel"] or 0) + apport

        self.db.executer(
            """
            UPDATE fonds_croissance
            SET montant_actuel = ?, dernier_mois_alimente = ?
            WHERE id = ?
            """,
            (nouveau_montant, mois_iso, fonds["id"])
        )

        return True

    ########################################################
    # Trésorerie prévisionnelle
    ########################################################

    def tresorerie_previsionnelle(self, mois_iso=None):
        """
        Solde actuel moins les charges du mois pas encore
        payées.
        """

        solde = self.solde_actuel() or 0

        charges = self.total_charges_mois(mois_iso)

        return round(solde - charges["restant"], 2)