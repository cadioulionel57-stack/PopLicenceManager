import csv

from database.database import Database


class CommandeExportManager:
    """
    Génère l'export CSV d'archive des commandes.

    Une ligne de fichier = un produit vendu. L'en-tête de la
    commande (numéro, date, client, frais de port, totaux)
    est répété sur chaque ligne, ce qui permet de filtrer et
    de faire des tableaux croisés directement dans Excel.

    Le fichier est écrit en UTF-8 avec BOM, séparateur
    point-virgule et virgule décimale : il s'ouvre
    directement dans Excel français, sans assistant d'import
    et sans accents cassés.
    """

    ENTETES = [
        "Numero commande",
        "Date commande",
        "Canal",
        "Client",
        "Statut",
        "Paye",
        "Date paiement",
        "Produit",
        "Quantite",
        "Prix unitaire HT",
        "Prix unitaire TTC",
        "Remise HT",
        "TVA %",
        "Cout achat unitaire HT",
        "Frais port client TTC",
        "Frais port reel HT",
        "Montant commande HT",
        "Montant commande TTC",
        "Transporteur",
        "Tracking",
    ]

    def __init__(self):

        self.db = Database()

    ########################################################
    # Point d'entrée appelé par l'écran Commandes
    ########################################################

    def exporter(self, identifiants, chemin):
        """
        Écrit dans `chemin` les commandes dont l'id figure
        dans `identifiants`. Retourne le nombre de lignes
        de produits écrites.
        """

        if not identifiants:
            raise ValueError(
                "Aucune commande sélectionnée pour l'export."
            )

        lignes = self._lire(identifiants)

        with open(
            chemin,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as fichier:

            redacteur = csv.writer(fichier, delimiter=";")

            redacteur.writerow(self.ENTETES)

            for ligne in lignes:

                redacteur.writerow(self._formater(ligne))

        return len(lignes)

    ########################################################
    # Lecture
    ########################################################

    def _lire(self, identifiants):
        """
        Une ligne par produit vendu. LEFT JOIN sur les
        lignes : une commande sans produit reste visible
        dans l'export au lieu de disparaître silencieusement.
        """

        trous = ",".join("?" for _ in identifiants)

        return self.db.lire(
            f"""
            SELECT
                co.numero,
                co.date_commande,
                co.statut,
                co.paye,
                co.date_paiement,
                co.frais_port_client_ttc,
                co.frais_port_reel_ht,
                co.montant_ht,
                co.montant_ttc,
                co.tracking,

                cv.nom AS nom_canal,

                TRIM(
                    COALESCE(c.prenom, '') || ' ' ||
                    COALESCE(c.nom, '')
                ) AS nom_client,

                t.nom AS nom_transporteur,

                lc.nom_produit,
                lc.quantite,
                lc.prix_unitaire_ht,
                lc.prix_unitaire_ttc,
                lc.remise_ht,
                lc.tva,
                lc.cout_achat_unitaire_ht

            FROM commandes co

            LEFT JOIN clients c
                ON c.id = co.client_id

            LEFT JOIN canaux_vente cv
                ON cv.id = co.canal_id

            LEFT JOIN transporteurs t
                ON t.id = co.transporteur_id

            LEFT JOIN lignes_commandes lc
                ON lc.commande_id = co.id
               AND lc.actif = 1

            WHERE co.id IN ({trous})

            ORDER BY co.date_commande, co.numero, lc.id
            """,
            tuple(identifiants)
        )

    ########################################################
    # Mise en forme
    ########################################################

    def _formater(self, ligne):

        return [
            ligne["numero"] or "",
            self._date(ligne["date_commande"]),
            ligne["nom_canal"] or "",
            ligne["nom_client"] or "",
            ligne["statut"] or "",
            "Oui" if ligne["paye"] else "Non",
            self._date(ligne["date_paiement"]),
            ligne["nom_produit"] or "",
            ligne["quantite"] if ligne["quantite"] is not None else "",
            self._nombre(ligne["prix_unitaire_ht"]),
            self._nombre(ligne["prix_unitaire_ttc"]),
            self._nombre(ligne["remise_ht"]),
            self._nombre(ligne["tva"]),
            self._nombre(ligne["cout_achat_unitaire_ht"]),
            self._nombre(ligne["frais_port_client_ttc"]),
            self._nombre(ligne["frais_port_reel_ht"]),
            self._nombre(ligne["montant_ht"]),
            self._nombre(ligne["montant_ttc"]),
            ligne["nom_transporteur"] or "",
            ligne["tracking"] or "",
        ]

    def _nombre(self, valeur):
        """
        Virgule décimale : sans ça, Excel français lit
        12.50 comme du texte et aucun total ne se calcule.
        """

        if valeur is None:
            return ""

        return f"{float(valeur):.2f}".replace(".", ",")

    def _date(self, valeur):
        """
        Les dates sont stockées en AAAA-MM-JJ. Excel
        français attend JJ/MM/AAAA pour les reconnaître
        comme des dates et non comme du texte.
        """

        if not valeur:
            return ""

        texte = str(valeur)[:10]

        morceaux = texte.split("-")

        if len(morceaux) != 3:
            return texte

        annee, mois, jour = morceaux

        return f"{jour}/{mois}/{annee}"