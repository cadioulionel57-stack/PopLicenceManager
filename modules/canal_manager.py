from database.database import Database


class CanalManager:
    """
    Gère les canaux de vente (WiziShop, Amazon FBM,
    Cdiscount, eBay, Leclerc, Rakuten, Fnac...).

    Rien n'est figé ici : un canal peut être ajouté,
    modifié ou désactivé librement depuis l'interface,
    avec ses propres règles (commission, frais fixe,
    port inclus ou non dans le prix affiché).
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM canaux_vente
            WHERE actif = 1
            ORDER BY ordre, nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM canaux_vente
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        nom,
        type_canal,
        commission_pourcentage=0,
        frais_fixe_ht=0,
        frais_paiement_pourcentage=0,
        frais_paiement_fixe_ht=0,
        taux_tsn_pourcentage=0,
        port_inclus=False,
        tarif_port_client_ttc=None,
        seuil_gratuite_ttc=None,
        contribution_transport_min_ht=0,
        prix_vente_min_ttc=None,
        utilise_grille_fba=False,
        ordre=0
    ):

        curseur = self.db.executer(
            """
            INSERT INTO canaux_vente
            (
                nom,
                type,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                port_inclus,
                tarif_port_client_ttc,
                seuil_gratuite_ttc,
                contribution_transport_min_ht,
                prix_vente_min_ttc,
                utilise_grille_fba,
                ordre,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                nom,
                type_canal,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                1 if port_inclus else 0,
                tarif_port_client_ttc,
                seuil_gratuite_ttc,
                contribution_transport_min_ht,
                prix_vente_min_ttc,
                1 if utilise_grille_fba else 0,
                ordre
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        nom,
        type_canal,
        commission_pourcentage,
        frais_fixe_ht,
        port_inclus,
        ordre,
        frais_paiement_pourcentage=0,
        frais_paiement_fixe_ht=0,
        taux_tsn_pourcentage=0,
        tarif_port_client_ttc=None,
        seuil_gratuite_ttc=None,
        contribution_transport_min_ht=0,
        prix_vente_min_ttc=None,
        utilise_grille_fba=False,
    ):

        self.db.executer(
            """
            UPDATE canaux_vente
            SET
                nom = ?,
                type = ?,
                commission_pourcentage = ?,
                frais_fixe_ht = ?,
                frais_paiement_pourcentage = ?,
                frais_paiement_fixe_ht = ?,
                taux_tsn_pourcentage = ?,
                port_inclus = ?,
                tarif_port_client_ttc = ?,
                seuil_gratuite_ttc = ?,
                contribution_transport_min_ht = ?,
                prix_vente_min_ttc = ?,
                utilise_grille_fba = ?,
                ordre = ?
            WHERE id = ?
            """,
            (
                nom,
                type_canal,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                1 if port_inclus else 0,
                tarif_port_client_ttc,
                seuil_gratuite_ttc,
                contribution_transport_min_ht,
                prix_vente_min_ttc,
                1 if utilise_grille_fba else 0,
                ordre,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE canaux_vente
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    ########################################################
    # Transporteurs autorisés pour ce canal
    #
    # Chaque canal marketplace définit sa propre liste de
    # transporteurs/offres autorisés (ex : Amazon FBM =
    # Colissimo Domicile uniquement ; Cdiscount = Mondial
    # Relay Point Relais + Colissimo Domicile). Le moteur
    # de prix choisit ensuite automatiquement le moins cher
    # de cette liste, selon le poids du produit.
    ########################################################

    def transporteurs_autorises(self, canal_id):

        return self.db.lire(
            """
            SELECT
                ct.id,
                ct.transporteur_id,
                ct.offre,
                t.nom AS transporteur
            FROM canaux_transporteurs ct

            LEFT JOIN transporteurs t
                ON t.id = ct.transporteur_id

            WHERE ct.canal_id = ?
            AND ct.actif = 1

            ORDER BY t.nom, ct.offre
            """,
            (canal_id,)
        )

    def definir_transporteurs_autorises(self, canal_id, liste):
        """
        Remplace la liste des transporteurs autorisés
        pour un canal.

        liste : [(transporteur_id, offre), ...]
        """

        self.db.executer(
            """
            DELETE FROM canaux_transporteurs
            WHERE canal_id = ?
            """,
            (canal_id,)
        )

        for transporteur_id, offre in liste:

            self.db.executer(
                """
                INSERT INTO canaux_transporteurs
                (canal_id, transporteur_id, offre, actif)
                VALUES (?, ?, ?, 1)
                """,
                (canal_id, transporteur_id, offre)
            )

    def transport_le_moins_cher(self, canal_id, poids_kg):
        """
        Renvoie (transporteur, offre, prix_ht) le moins
        cher parmi les transporteurs autorisés pour ce
        canal, pour le poids donné.

        Renvoie None si aucun transporteur autorisé ne
        couvre ce poids (produit trop lourd, ou aucun
        transporteur configuré pour ce canal).
        """

        from modules.grille_transport_manager import (
            GrilleTransportManager
        )

        gtm = GrilleTransportManager()

        autorises = self.transporteurs_autorises(canal_id)

        meilleur = None

        for option in autorises:

            prix = gtm.tarif(
                option["transporteur_id"],
                option["offre"],
                poids_kg
            )

            if prix is None:
                continue

            if meilleur is None or prix < meilleur["prix_ht"]:

                meilleur = {
                    "transporteur": option["transporteur"],
                    "transporteur_id": option["transporteur_id"],
                    "offre": option["offre"],
                    "prix_ht": prix,
                }

        return meilleur

    def transport_eligible_prix(self, canal_id, poids_kg, prix_vente_ttc):
        """
        Cas des canaux avec grille_tarif_client_active=1
        (ex : Fnac) : plusieurs transporteurs autorisés,
        chacun éligible seulement sur une tranche de prix de
        vente (ex : Relais Colis 25€-200€, Chrono 18 +200€),
        avec un tarif client différent par transporteur ET
        par poids.

        Renvoie le transporteur éligible le moins cher pour
        LE CLIENT (par défaut, cf. règle actée), parmi ceux
        dont la tranche de prix couvre prix_vente_ttc et
        dont la tranche de poids couvre poids_kg.

        Renvoie None si aucun transporteur n'est éligible
        (produit hors tranche de prix, ou trop lourd) — le
        produit doit alors être exclu de ce canal.
        """

        from modules.grille_transport_manager import (
            GrilleTransportManager
        )
        from modules.grille_tarif_client_manager import (
            GrilleTarifClientManager
        )

        gtm = GrilleTransportManager()
        gtc = GrilleTarifClientManager()

        autorises = self.db.lire(
            """
            SELECT
                ct.transporteur_id,
                ct.offre,
                ct.prix_min_ttc,
                ct.prix_max_ttc,
                t.nom AS transporteur
            FROM canaux_transporteurs ct

            LEFT JOIN transporteurs t
                ON t.id = ct.transporteur_id

            WHERE ct.canal_id = ?
            AND ct.actif = 1
            """,
            (canal_id,)
        )

        meilleur = None

        for option in autorises:

            prix_min = option["prix_min_ttc"]
            prix_max = option["prix_max_ttc"]

            if prix_min is not None and prix_vente_ttc < prix_min:
                continue

            if prix_max is not None and prix_vente_ttc > prix_max:
                continue

            tarif_client = gtc.tarif(
                canal_id,
                option["transporteur_id"],
                option["offre"],
                poids_kg
            )

            if tarif_client is None:
                continue

            cout_reel_ht = gtm.tarif(
                option["transporteur_id"],
                option["offre"],
                poids_kg
            )

            if cout_reel_ht is None:
                continue

            if meilleur is None or tarif_client < meilleur["tarif_client_ttc"]:

                meilleur = {
                    "transporteur": option["transporteur"],
                    "transporteur_id": option["transporteur_id"],
                    "offre": option["offre"],
                    "tarif_client_ttc": tarif_client,
                    "prix_ht": cout_reel_ht,
                }

        return meilleur