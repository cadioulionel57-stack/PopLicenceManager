from database.database import Database


class CommandeManager:
    """
    Gère les commandes, leurs lignes (produits achetés) et
    les retours associés — la brique qui alimentera plus
    tard l'onglet Ventes pour calculer CA, charges, frais de
    port réels vs facturés au client, et coûts de retour.
    """

    def __init__(self):

        self.db = Database()

    ########################################################
    # Commandes
    ########################################################

    def tous(self):
        """
        Liste toutes les commandes actives, avec le nom du
        client et du canal déjà résolus (évite un aller-
        retour supplémentaire à l'affichage).
        """

        return self.db.lire(
            """
            SELECT
                co.*,
                (c.prenom || ' ' || c.nom) AS nom_client,
                cv.nom AS nom_canal
            FROM commandes co

            LEFT JOIN clients c
                ON c.id = co.client_id

            LEFT JOIN canaux_vente cv
                ON cv.id = co.canal_id

            WHERE co.actif = 1

            ORDER BY co.date_commande DESC
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM commandes
            WHERE id = ?
            """,
            (identifiant,)
        )

    def marquer_paye(self, commande_id, paye, date_paiement=None):
        """
        Coche/décoche une commande comme réellement payée
        (argent reçu). Si cochée : fige une contribution au
        Fonds de Croissance (5% du bénéfice net de CETTE
        vente, au taux en vigueur au moment où elle est
        cochée — ne bouge plus jamais après, même si le taux
        change plus tard). Si décochée : retire cette
        contribution proprement.
        """

        from datetime import date

        date_paiement = date_paiement or date.today().isoformat()

        self.db.executer(
            """
            UPDATE commandes
            SET paye = ?, date_paiement = ?
            WHERE id = ?
            """,
            (1 if paye else 0, date_paiement if paye else None, commande_id)
        )

        if paye:

            from modules.tresorerie_manager import TresorerieManager

            existe = self.db.lire_un(
                """
                SELECT id
                FROM contributions_fonds_croissance
                WHERE commande_id = ?
                """,
                (commande_id,)
            )

            if existe is None:

                taux = TresorerieManager().taux_contribution_croissance()

                gain = self.gain_net_reel(commande_id)
                gain_net = gain["gain_net_ht"] if gain else 0

                montant_contribue = round(gain_net * (taux / 100), 2)

                self.db.executer(
                    """
                    INSERT INTO contributions_fonds_croissance
                    (commande_id, montant_contribue, taux_applique,
                     date_contribution)
                    VALUES (?, ?, ?, ?)
                    """,
                    (commande_id, montant_contribue, taux, date_paiement)
                )

        else:

            self.db.executer(
                """
                DELETE FROM contributions_fonds_croissance
                WHERE commande_id = ?
                """,
                (commande_id,)
            )

    def montant_encaisse_ttc(self, commande_id):
        """
        Argent réellement encaissé pour cette commande : le
        montant TTC payé par le client (produits + port),
        tel qu'il arrive vraiment sur le compte.
        """

        commande = self.obtenir(commande_id)

        if commande is None:
            return 0

        lignes = self.lignes(commande_id)

        montant_produits_ttc = sum(
            (l["prix_unitaire_ttc"] or 0) * (l["quantite"] or 1)
            for l in lignes
        )

        frais_port = commande["frais_port_client_ttc"] or 0

        return round(montant_produits_ttc + frais_port, 2)

    def ca_encaisse_depuis(self, date_iso):
        """
        Total réellement encaissé (TTC) pour toutes les
        commandes cochées "payée" dont la date de paiement
        est le jour même ou après date_iso — sert à ajouter
        au solde du jour saisi à la main. Comparaison
        inclusive : un paiement coché le jour même de la
        saisie du solde compte quand même (on part du
        principe que le solde saisi ne l'inclut pas encore).
        """

        commandes = self.db.lire(
            """
            SELECT id
            FROM commandes
            WHERE actif = 1
            AND paye = 1
            AND date_paiement >= ?
            """,
            (date_iso,)
        )

        return round(
            sum(self.montant_encaisse_ttc(c["id"]) for c in commandes),
            2
        )

    def ajouter(
        self,
        numero,
        canal_id,
        client_id,
        date_commande,
        date_expedition=None,
        transporteur_id=None,
        statut="En cours",
        montant_ht=0,
        montant_ttc=0,
        frais_port_client_ttc=0,
        frais_port_reel_ht=0,
        papier_cadeau_actif=False,
        papier_cadeau_emballage_id=None,
        papier_cadeau_supplement_id=None,
        tracking="",
        commentaire=""
    ):

        curseur = self.db.executer(
            """
            INSERT INTO commandes
            (
                numero, canal_id, client_id, date_commande,
                date_expedition, transporteur_id, statut,
                montant_ht, montant_ttc,
                frais_port_client_ttc, frais_port_reel_ht,
                papier_cadeau_actif, papier_cadeau_emballage_id,
                papier_cadeau_supplement_id,
                tracking, commentaire, actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                numero, canal_id, client_id, date_commande,
                date_expedition, transporteur_id, statut,
                montant_ht, montant_ttc,
                frais_port_client_ttc, frais_port_reel_ht,
                1 if papier_cadeau_actif else 0,
                papier_cadeau_emballage_id,
                papier_cadeau_supplement_id,
                tracking, commentaire
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        numero,
        canal_id,
        client_id,
        date_commande,
        date_expedition=None,
        transporteur_id=None,
        statut="En cours",
        montant_ht=0,
        montant_ttc=0,
        frais_port_client_ttc=0,
        frais_port_reel_ht=0,
        papier_cadeau_actif=False,
        papier_cadeau_emballage_id=None,
        papier_cadeau_supplement_id=None,
        tracking="",
        commentaire=""
    ):

        self.db.executer(
            """
            UPDATE commandes
            SET
                numero = ?, canal_id = ?, client_id = ?,
                date_commande = ?, date_expedition = ?,
                transporteur_id = ?, statut = ?,
                montant_ht = ?, montant_ttc = ?,
                frais_port_client_ttc = ?, frais_port_reel_ht = ?,
                papier_cadeau_actif = ?,
                papier_cadeau_emballage_id = ?,
                papier_cadeau_supplement_id = ?,
                tracking = ?, commentaire = ?
            WHERE id = ?
            """,
            (
                numero, canal_id, client_id, date_commande,
                date_expedition, transporteur_id, statut,
                montant_ht, montant_ttc,
                frais_port_client_ttc, frais_port_reel_ht,
                1 if papier_cadeau_actif else 0,
                papier_cadeau_emballage_id,
                papier_cadeau_supplement_id,
                tracking, commentaire,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE commandes
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    ########################################################
    # Lignes de commande (le panier)
    ########################################################

    def lignes(self, commande_id):

        return self.db.lire(
            """
            SELECT *
            FROM lignes_commandes
            WHERE commande_id = ?
            AND actif = 1
            ORDER BY id
            """,
            (commande_id,)
        )

    def obtenir_ligne(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM lignes_commandes
            WHERE id = ?
            """,
            (identifiant,)
        )

    def definir_lignes(self, commande_id, lignes):
        """
        Remplace toutes les lignes d'une commande — plus
        simple et plus sûr que de gérer ajout/suppression
        ligne par ligne depuis l'écran d'édition, qui
        reconstruit toujours le panier en entier à chaque
        sauvegarde.

        lignes : liste de dictionnaires avec les clés
        produit_id, nom_produit, quantite, prix_unitaire_ht,
        prix_unitaire_ttc, cout_achat_unitaire_ht,
        remise_ht, tva.
        """

        self.db.executer(
            """
            UPDATE lignes_commandes
            SET actif = 0
            WHERE commande_id = ?
            """,
            (commande_id,)
        )

        for ligne in lignes:

            self.db.executer(
                """
                INSERT INTO lignes_commandes
                (
                    commande_id, produit_id, nom_produit,
                    quantite, prix_unitaire_ht,
                    prix_unitaire_ttc, cout_achat_unitaire_ht,
                    remise_ht, tva, actif
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
                )
                """,
                (
                    commande_id,
                    ligne.get("produit_id"),
                    ligne.get("nom_produit"),
                    ligne.get("quantite", 1),
                    ligne.get("prix_unitaire_ht"),
                    ligne.get("prix_unitaire_ttc"),
                    ligne.get("cout_achat_unitaire_ht"),
                    ligne.get("remise_ht", 0),
                    ligne.get("tva", 20),
                )
            )

    ########################################################
    # Retours
    ########################################################

    def retours_commande(self, commande_id):
        """
        Renvoie tous les retours liés aux lignes de cette
        commande (utile pour l'affichage groupé sur la
        fiche commande).
        """

        return self.db.lire(
            """
            SELECT
                r.*,
                lc.nom_produit
            FROM commandes_retours r

            LEFT JOIN lignes_commandes lc
                ON lc.id = r.ligne_commande_id

            WHERE lc.commande_id = ?
            AND r.actif = 1

            ORDER BY r.date_retour DESC
            """,
            (commande_id,)
        )

    def retours_ligne(self, ligne_commande_id):

        return self.db.lire(
            """
            SELECT *
            FROM commandes_retours
            WHERE ligne_commande_id = ?
            AND actif = 1
            ORDER BY date_retour DESC
            """,
            (ligne_commande_id,)
        )

    def ajouter_retour(
        self,
        ligne_commande_id,
        date_retour,
        motif="",
        statut="Demandé",
        montant_rembourse_ttc=0,
        frais_reexpedition_ht=0,
        cout_retour_ht=0,
        notes=""
    ):

        curseur = self.db.executer(
            """
            INSERT INTO commandes_retours
            (
                ligne_commande_id, date_retour, motif, statut,
                montant_rembourse_ttc, frais_reexpedition_ht,
                cout_retour_ht, notes, actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                ligne_commande_id, date_retour, motif, statut,
                montant_rembourse_ttc, frais_reexpedition_ht,
                cout_retour_ht, notes
            )
        )

        return curseur.lastrowid

    def modifier_retour(
        self,
        identifiant,
        date_retour,
        motif,
        statut,
        montant_rembourse_ttc,
        frais_reexpedition_ht,
        cout_retour_ht,
        notes
    ):

        self.db.executer(
            """
            UPDATE commandes_retours
            SET
                date_retour = ?, motif = ?, statut = ?,
                montant_rembourse_ttc = ?,
                frais_reexpedition_ht = ?, cout_retour_ht = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                date_retour, motif, statut,
                montant_rembourse_ttc, frais_reexpedition_ht,
                cout_retour_ht, notes,
                identifiant
            )
        )

    def supprimer_retour(self, identifiant):

        self.db.executer(
            """
            UPDATE commandes_retours
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    ########################################################
    # Vue SAV globale (tableau de bord + suivi transversal)
    ########################################################

    def tous_les_retours(self):
        """
        Liste tous les retours, toutes commandes confondues,
        avec le numéro de commande, le client et le produit
        déjà résolus — pour un suivi SAV transversal, sans
        avoir à ouvrir chaque commande une par une.
        """

        return self.db.lire(
            """
            SELECT
                r.*,
                lc.nom_produit,
                co.numero AS numero_commande,
                co.id AS commande_id,
                (cl.prenom || ' ' || cl.nom) AS nom_client
            FROM commandes_retours r

            LEFT JOIN lignes_commandes lc
                ON lc.id = r.ligne_commande_id

            LEFT JOIN commandes co
                ON co.id = lc.commande_id

            LEFT JOIN clients cl
                ON cl.id = co.client_id

            WHERE r.actif = 1

            ORDER BY r.date_retour DESC
            """
        )

    def total_sav(self):
        """
        Coût SAV total, toutes commandes confondues — somme
        du remboursement, des frais de réexpédition et du
        coût du retour lui-même, sur tous les retours actifs.
        Alimente le KPI du tableau de bord.
        """

        TAUX_TVA = 0.20

        total = 0

        for retour in self.tous_les_retours():

            total += (
                (retour["montant_rembourse_ttc"] or 0) / (1 + TAUX_TVA)
                + (retour["frais_reexpedition_ht"] or 0)
                + (retour["cout_retour_ht"] or 0)
            )

        return round(total, 2)

    ########################################################
    # Chiffre d'affaires (pour le tableau de bord)
    ########################################################

    def papier_cadeau_commande(self, commande_id):
        """
        CA, coût et marge de la prestation emballage cadeau
        pour cette commande, si elle en a une.

        CA = le tarif facturé de l'emballage "principal"
        choisi (toujours le même montant, quel que soit le
        code — c'est un choix esthétique pour toi, pas pour
        le prix).

        Coût = le coût réel de l'emballage principal choisi
        + le coût du supplément éventuel (jamais facturé).
        """

        commande = self.obtenir(commande_id)

        if commande is None or not commande["papier_cadeau_actif"]:

            return {
                "ca_ht": 0,
                "cout_ht": 0,
                "marge_ht": 0,
            }

        from modules.emballage_cadeau_manager import (
            EmballageCadeauManager
        )

        manager = EmballageCadeauManager()

        ca_ht = 0
        cout_ht = 0

        if commande["papier_cadeau_emballage_id"]:

            principal = manager.obtenir(
                commande["papier_cadeau_emballage_id"]
            )

            if principal:
                ca_ht = principal["tarif_facture_ht"] or 0
                cout_ht = principal["cout_ht"] or 0

        if commande["papier_cadeau_supplement_id"]:

            supplement = manager.obtenir(
                commande["papier_cadeau_supplement_id"]
            )

            if supplement:
                cout_ht += supplement["cout_ht"] or 0

        return {
            "ca_ht": round(ca_ht, 2),
            "cout_ht": round(cout_ht, 2),
            "marge_ht": round(ca_ht - cout_ht, 2),
        }

    def chiffre_affaires_ht(self, commande_id):
        """
        CA HT d'une commande = vente de marchandises (hors
        contribution transport cachée, qui n'est pas une
        vraie vente mais de la récupération de coût de
        transport) + frais de port facturés séparément au
        client.
        """

        commande = self.obtenir(commande_id)

        if commande is None:
            return 0

        lignes = self.lignes(commande_id)

        canal = self.db.lire_un(
            """
            SELECT *
            FROM canaux_vente
            WHERE id = ?
            """,
            (commande["canal_id"],)
        )

        TAUX_TVA = 0.20

        montant_produits_ht = sum(
            (l["prix_unitaire_ht"] or 0) * (l["quantite"] or 1)
            for l in lignes
        )

        quantite_totale = sum(l["quantite"] or 1 for l in lignes)

        contribution_transport_ht = 0

        if canal is not None:

            contribution_unitaire = (
                canal["contribution_transport_min_ht"] or 0
            )
            contribution_transport_ht = (
                contribution_unitaire * quantite_totale
            )

        frais_port_client_ht = (
            (commande["frais_port_client_ttc"] or 0) / (1 + TAUX_TVA)
        )

        return round(
            (montant_produits_ht - contribution_transport_ht)
            + frais_port_client_ht,
            2
        )

    def ca_periode(self, date_debut, date_fin):
        """
        CA HT total sur une période (bornes incluses, format
        'YYYY-MM-DD'), toutes commandes actives confondues.
        """

        commandes = self.db.lire(
            """
            SELECT id
            FROM commandes
            WHERE actif = 1
            AND date_commande >= ?
            AND date_commande <= ?
            """,
            (date_debut, date_fin)
        )

        return round(
            sum(
                self.chiffre_affaires_ht(c["id"]) for c in commandes
            ),
            2
        )

    def ca_par_licence(self, mois_iso, limite=10):
        """
        CA HT du mois, par licence de produit vendu — classé
        du plus rentable au moins rentable. Les lignes dont
        le produit n'a pas de licence associée (ou n'existe
        plus) sont regroupées sous "Sans licence".
        """

        import calendar

        annee, mois = (int(x) for x in mois_iso.split("-"))
        dernier_jour = calendar.monthrange(annee, mois)[1]

        date_debut = f"{mois_iso}-01"
        date_fin = f"{mois_iso}-{dernier_jour:02d}"

        lignes = self.db.lire(
            """
            SELECT
                lc.quantite,
                lc.prix_unitaire_ht,
                l.nom AS nom_licence
            FROM lignes_commandes lc

            INNER JOIN commandes co
                ON co.id = lc.commande_id

            LEFT JOIN produits p
                ON p.id = lc.produit_id

            LEFT JOIN licences l
                ON l.id = p.licence_id

            WHERE lc.actif = 1
            AND co.actif = 1
            AND co.date_commande >= ?
            AND co.date_commande <= ?
            """,
            (date_debut, date_fin)
        )

        ca_par_licence = {}

        for l in lignes:

            nom = l["nom_licence"] or "Sans licence"
            ca = (l["prix_unitaire_ht"] or 0) * (l["quantite"] or 1)

            ca_par_licence[nom] = ca_par_licence.get(nom, 0) + ca

        resultat = [
            {"licence": nom, "ca_ht": round(ca, 2)}
            for nom, ca in sorted(
                ca_par_licence.items(), key=lambda x: -x[1]
            )
            if ca > 0
        ]

        return resultat[:limite]

    def benefice_par_canal(self, mois_iso):
        """
        Bénéfice net réel du mois, réparti par canal de
        vente — complète ca_par_canal : un canal peut faire
        beaucoup de CA mais très peu de marge à cause des
        commissions et frais (l'inverse est vrai aussi).
        """

        import calendar

        annee, mois = (int(x) for x in mois_iso.split("-"))
        dernier_jour = calendar.monthrange(annee, mois)[1]

        date_debut = f"{mois_iso}-01"
        date_fin = f"{mois_iso}-{dernier_jour:02d}"

        commandes = self.db.lire(
            """
            SELECT co.id, cv.nom AS nom_canal
            FROM commandes co

            LEFT JOIN canaux_vente cv
                ON cv.id = co.canal_id

            WHERE co.actif = 1
            AND co.date_commande >= ?
            AND co.date_commande <= ?
            """,
            (date_debut, date_fin)
        )

        benefice_par_canal = {}

        for c in commandes:

            nom = c["nom_canal"] or "Canal inconnu"

            gain = self.gain_net_reel(c["id"])
            benefice = gain["gain_net_ht"] if gain else 0

            benefice_par_canal[nom] = (
                benefice_par_canal.get(nom, 0) + benefice
            )

        return [
            {"canal": nom, "benefice_ht": round(benefice, 2)}
            for nom, benefice in sorted(
                benefice_par_canal.items(), key=lambda x: -x[1]
            )
        ]

    def ca_par_canal(self, mois_iso):
        """
        CA HT du mois, réparti par canal de vente — sert au
        camembert de répartition. Ne renvoie que les canaux
        ayant réellement du CA ce mois-là.
        """

        import calendar

        annee, mois = (int(x) for x in mois_iso.split("-"))
        dernier_jour = calendar.monthrange(annee, mois)[1]

        date_debut = f"{mois_iso}-01"
        date_fin = f"{mois_iso}-{dernier_jour:02d}"

        commandes = self.db.lire(
            """
            SELECT co.id, co.canal_id, cv.nom AS nom_canal
            FROM commandes co

            LEFT JOIN canaux_vente cv
                ON cv.id = co.canal_id

            WHERE co.actif = 1
            AND co.date_commande >= ?
            AND co.date_commande <= ?
            """,
            (date_debut, date_fin)
        )

        ca_par_canal = {}

        for c in commandes:

            nom = c["nom_canal"] or "Canal inconnu"
            ca = self.chiffre_affaires_ht(c["id"])

            ca_par_canal[nom] = ca_par_canal.get(nom, 0) + ca

        return [
            {"canal": nom, "ca_ht": round(ca, 2)}
            for nom, ca in sorted(
                ca_par_canal.items(), key=lambda x: -x[1]
            )
            if ca > 0
        ]

    def mois_avec_commandes(self):
        """
        Tous les mois (AAAA-MM) où au moins une commande a
        été passée, triés du plus récent au plus ancien —
        sert à peupler le sélecteur de mois des graphiques.
        """

        lignes = self.db.lire(
            """
            SELECT DISTINCT substr(date_commande, 1, 7) AS mois
            FROM commandes
            WHERE actif = 1
            AND date_commande IS NOT NULL
            ORDER BY mois DESC
            """
        )

        return [l["mois"] for l in lignes if l["mois"]]

    def annees_disponibles(self):
        """
        Toutes les années civiles (AAAA) où au moins une
        commande existe, triées de la plus récente à la plus
        ancienne — sert au sélecteur d'année du graphique
        d'évolution du CA.
        """

        lignes = self.db.lire(
            """
            SELECT DISTINCT substr(date_commande, 1, 4) AS annee
            FROM commandes
            WHERE actif = 1
            AND date_commande IS NOT NULL
            ORDER BY annee DESC
            """
        )

        return [l["annee"] for l in lignes if l["annee"]]

    def ca_par_mois_annee(self, annee):
        """
        CA HT de chacun des 12 mois d'une année civile
        donnée (janvier à décembre) — renvoie aussi les mois
        sans aucune vente, à 0€, pour que le graphique montre
        toujours les 12 mois complets.
        """

        resultat = []

        for mois in range(1, 13):

            mois_iso = f"{annee}-{mois:02d}"

            import calendar

            dernier_jour = calendar.monthrange(int(annee), mois)[1]

            ca = self.ca_periode(
                f"{mois_iso}-01", f"{mois_iso}-{dernier_jour:02d}"
            )

            resultat.append({"mois": mois_iso, "ca_ht": ca})

        return resultat

    def ca_jour(self):

        from datetime import date

        aujourdhui = date.today().isoformat()

        return self.ca_periode(aujourdhui, aujourdhui)

    def ca_mois(self):

        from datetime import date

        aujourdhui = date.today()

        debut_mois = aujourdhui.replace(day=1).isoformat()

        return self.ca_periode(debut_mois, aujourdhui.isoformat())

    def ca_prestations_periode(self, date_debut, date_fin):
        """
        CA HT des prestations de service (emballage cadeau
        pour l'instant) sur une période — volontairement
        séparé du CA marchandises, pour piloter les deux
        indépendamment.
        """

        commandes = self.db.lire(
            """
            SELECT id
            FROM commandes
            WHERE actif = 1
            AND date_commande >= ?
            AND date_commande <= ?
            AND papier_cadeau_actif = 1
            """,
            (date_debut, date_fin)
        )

        total = 0

        for c in commandes:

            papier_cadeau = self.papier_cadeau_commande(c["id"])
            total += papier_cadeau["ca_ht"]

        return round(total, 2)

    def ca_prestations_jour(self):

        from datetime import date

        aujourdhui = date.today().isoformat()

        return self.ca_prestations_periode(aujourdhui, aujourdhui)

    def ca_prestations_mois(self):

        from datetime import date

        aujourdhui = date.today()

        debut_mois = aujourdhui.replace(day=1).isoformat()

        return self.ca_prestations_periode(
            debut_mois, aujourdhui.isoformat()
        )

    def benefice_periode(self, date_debut, date_fin):
        """
        Bénéfice HT total sur une période (bornes incluses,
        format 'YYYY-MM-DD') — somme du gain net réel de
        chaque commande passée sur cette période.
        """

        commandes = self.db.lire(
            """
            SELECT id
            FROM commandes
            WHERE actif = 1
            AND date_commande >= ?
            AND date_commande <= ?
            """,
            (date_debut, date_fin)
        )

        total = 0

        for c in commandes:

            gain = self.gain_net_reel(c["id"])

            if gain:
                total += gain["gain_net_ht"]

        return round(total, 2)

    def benefice_mois(self):

        from datetime import date

        aujourdhui = date.today()

        debut_mois = aujourdhui.replace(day=1).isoformat()

        return self.benefice_periode(debut_mois, aujourdhui.isoformat())

    def benefice_total(self):
        """
        Bénéfice cumulé depuis le tout début (toutes les
        commandes actives, sans limite de date) — recalculé
        en direct à chaque fois, jamais stocké. Sert de base
        au Fonds de Croissance, qui doit refléter la réalité
        à l'instant présent, pas un historique figé.
        """

        return self.benefice_periode("0000-01-01", "9999-12-31")

    ########################################################
    # TVA (collectée / déductible / nette)
    ########################################################

    def tva_commande(self, commande_id):
        """
        TVA collectée et déductible d'une commande, au taux
        standard de 20% :

        Collectée : sur les produits vendus (écart TTC-HT
        réellement facturé au client) + sur les frais de port
        facturés au client.

        Déductible : sur le coût d'achat des produits, la
        commission du canal, les frais de paiement, le
        transport réel payé et les frais fixes du canal.

        Approximation au taux standard 20% — ne distingue pas
        les taux réduits (livres, alimentaire...) si tu en as
        dans ton catalogue, à affiner plus tard si besoin.
        """

        TAUX_TVA = 0.20

        commande = self.obtenir(commande_id)

        if commande is None:
            return None

        lignes = self.lignes(commande_id)

        # TVA collectée sur les produits : différence entre
        # le TTC réellement facturé et son équivalent HT.
        tva_collectee_produits = sum(
            (
                (l["prix_unitaire_ttc"] or 0)
                - (l["prix_unitaire_ht"] or 0)
            ) * (l["quantite"] or 1)
            for l in lignes
        )

        frais_port_client_ttc = commande["frais_port_client_ttc"] or 0
        frais_port_client_ht = frais_port_client_ttc / (1 + TAUX_TVA)

        tva_collectee_port = frais_port_client_ttc - frais_port_client_ht

        tva_collectee = tva_collectee_produits + tva_collectee_port

        # TVA déductible : taux standard appliqué sur chaque
        # charge HT réelle de la commande.
        gain = self.gain_net_reel(commande_id)

        tva_deductible = 0

        if gain:

            tva_deductible = TAUX_TVA * (
                gain["cout_achat_total_ht"]
                + gain["commission_ht"]
                + gain["frais_paiement_ht"]
                + gain["frais_fixe_canal_ht"]
                + gain["frais_port_reel_ht"]
                + gain["papier_cadeau_cout_ht"]
            )

            # TVA collectée sur la prestation emballage cadeau,
            # facturée au client — le taux facturé (2,42€ HT)
            # est déjà HT, donc on applique le taux standard
            # pour obtenir la TVA correspondante.
            tva_collectee += TAUX_TVA * gain["papier_cadeau_ca_ht"]

        return {
            "tva_collectee": round(tva_collectee, 2),
            "tva_deductible": round(tva_deductible, 2),
            "tva_nette": round(tva_collectee - tva_deductible, 2),
        }

    def tva_periode(self, date_debut, date_fin):
        """
        TVA collectée/déductible/nette totale sur une
        période (bornes incluses, format 'YYYY-MM-DD').
        """

        commandes = self.db.lire(
            """
            SELECT id
            FROM commandes
            WHERE actif = 1
            AND date_commande >= ?
            AND date_commande <= ?
            """,
            (date_debut, date_fin)
        )

        collectee = 0
        deductible = 0

        for c in commandes:

            tva = self.tva_commande(c["id"])

            if tva:
                collectee += tva["tva_collectee"]
                deductible += tva["tva_deductible"]

        return {
            "tva_collectee": round(collectee, 2),
            "tva_deductible": round(deductible, 2),
            "tva_nette": round(collectee - deductible, 2),
        }

    def tva_mois(self):

        from datetime import date

        aujourdhui = date.today()

        debut_mois = aujourdhui.replace(day=1).isoformat()

        return self.tva_periode(debut_mois, aujourdhui.isoformat())

    def total_cout_achat_vendu(self):
        """
        Somme du coût d'achat fournisseur de tous les
        produits vendus, toutes commandes actives confondues
        — alimente le KPI "Renouvellement Stock" (ce qui a
        été récupéré sur les ventes pour racheter du stock).

        Recalculé en direct à chaque fois depuis les lignes
        de commande, jamais stocké — comme les Fonds
        Développement/Réserve, pas de risque de double
        comptage à chaque relance du logiciel.
        """

        lignes = self.db.lire(
            """
            SELECT
                lc.quantite,
                lc.cout_achat_unitaire_ht
            FROM lignes_commandes lc

            INNER JOIN commandes co
                ON co.id = lc.commande_id

            WHERE lc.actif = 1
            AND co.actif = 1
            """
        )

        total = sum(
            (l["cout_achat_unitaire_ht"] or 0) * (l["quantite"] or 1)
            for l in lignes
        )

        return round(total, 2)

    def gain_net_reel(self, commande_id):
        """
        Calcule le gain net réel d'une commande, en tenant
        compte de tout ce qui pèse réellement dessus :

        + Montant produits + port payé par le client
        − Coût d'achat des produits
        − Contribution transport cachée dans le prix (canaux
          type Amazon FBM/Cdiscount/eBay/Rakuten qui
          intègrent un montant fixe au produit)
        − Frais de port réel payé par toi (en plus, s'il y
          en a)
        − Commission du canal (taux par défaut du canal,
          approximation si les catégories par produit ne
          sont pas prises en compte ligne par ligne)
        − Coûts de retour (remboursement + réexpédition +
          coût du retour lui-même)

        Renvoie un dictionnaire détaillé, pas juste le total
        — pour que la fiche commande puisse expliquer d'où
        vient le chiffre, pas juste l'afficher.
        """

        commande = self.obtenir(commande_id)

        if commande is None:
            return None

        lignes = self.lignes(commande_id)

        canal = self.db.lire_un(
            """
            SELECT *
            FROM canaux_vente
            WHERE id = ?
            """,
            (commande["canal_id"],)
        )

        TAUX_TVA = 0.20

        montant_produits_ht = sum(
            (l["prix_unitaire_ht"] or 0) * (l["quantite"] or 1)
            for l in lignes
        )

        cout_achat_total_ht = sum(
            (l["cout_achat_unitaire_ht"] or 0) * (l["quantite"] or 1)
            for l in lignes
        )

        quantite_totale = sum(l["quantite"] or 1 for l in lignes)

        contribution_transport_ht = 0

        if canal is not None:

            contribution_unitaire = (
                canal["contribution_transport_min_ht"] or 0
            )
            contribution_transport_ht = (
                contribution_unitaire * quantite_totale
            )

        frais_port_client_ht = (
            (commande["frais_port_client_ttc"] or 0) / (1 + TAUX_TVA)
        )

        frais_port_reel_ht = commande["frais_port_reel_ht"] or 0

        encaisse_ht = montant_produits_ht + frais_port_client_ht

        commission_pourcentage = (
            canal["commission_pourcentage"] or 0
        ) if canal else 0

        commission_ht = encaisse_ht * (commission_pourcentage / 100)

        # Frais fixe par vente du canal (ex : 0,35€ chez
        # eBay), et frais de paiement (% + montant fixe) —
        # oubliés jusqu'ici dans le calcul du gain, on les
        # ajoute pour que le Bénéfice soit exact.
        frais_fixe_canal_ht = (canal["frais_fixe_ht"] or 0) if canal else 0

        frais_paiement_pourcentage = (
            (canal["frais_paiement_pourcentage"] or 0) if canal else 0
        )
        frais_paiement_fixe_ht = (
            (canal["frais_paiement_fixe_ht"] or 0) if canal else 0
        )

        frais_paiement_ht = (
            encaisse_ht * (frais_paiement_pourcentage / 100)
            + frais_paiement_fixe_ht
        )

        retours = self.retours_commande(commande_id)

        cout_retours_ht = 0

        for retour in retours:

            cout_retours_ht += (
                (retour["montant_rembourse_ttc"] or 0) / (1 + TAUX_TVA)
                + (retour["frais_reexpedition_ht"] or 0)
                + (retour["cout_retour_ht"] or 0)
            )

        # Prestation emballage cadeau : sa marge s'ajoute
        # au gain net de la commande (le CA et le coût de la
        # commission/paiement restent calculés séparément,
        # cette prestation n'est pas commissionnée par le
        # canal — elle n'est vendue que sur le site).
        papier_cadeau = self.papier_cadeau_commande(commande_id)

        gain_net_ht = (
            encaisse_ht
            - cout_achat_total_ht
            - contribution_transport_ht
            - frais_port_reel_ht
            - commission_ht
            - frais_fixe_canal_ht
            - frais_paiement_ht
            - cout_retours_ht
            + papier_cadeau["marge_ht"]
        )

        return {
            "encaisse_ht": round(encaisse_ht, 2),
            "montant_produits_ht": round(montant_produits_ht, 2),
            "frais_port_client_ht": round(frais_port_client_ht, 2),
            "cout_achat_total_ht": round(cout_achat_total_ht, 2),
            "contribution_transport_ht": round(contribution_transport_ht, 2),
            "frais_port_reel_ht": round(frais_port_reel_ht, 2),
            "commission_pourcentage": commission_pourcentage,
            "commission_ht": round(commission_ht, 2),
            "frais_fixe_canal_ht": round(frais_fixe_canal_ht, 2),
            "frais_paiement_ht": round(frais_paiement_ht, 2),
            "cout_retours_ht": round(cout_retours_ht, 2),
            "papier_cadeau_ca_ht": papier_cadeau["ca_ht"],
            "papier_cadeau_cout_ht": papier_cadeau["cout_ht"],
            "papier_cadeau_marge_ht": papier_cadeau["marge_ht"],
            "gain_net_ht": round(gain_net_ht, 2),
        }