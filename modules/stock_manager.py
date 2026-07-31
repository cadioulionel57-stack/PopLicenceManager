from datetime import date

from database.database import Database


class StockManager:
    """
    Moteur du stock : entrées, sorties, quantités et
    valorisation.

    Principe : la table `mouvements_stock` est la seule
    vérité. Chaque entrée et chaque sortie y laisse une
    ligne, et la quantité d'un produit n'est jamais saisie —
    elle est toujours le résultat de ses mouvements. C'est
    ce qui permet de justifier n'importe quel chiffre et de
    retrouver d'où vient un écart.

    La colonne `produits.quantite_stock` est une TOUTE AUTRE
    CHOSE : c'est la quantité que l'on décide de mettre en
    vente sur les canaux, celle qui part dans les exports
    WiziShop et Base. Elle appartient à l'utilisateur.

    Exemple : 10 exemplaires en rayon dont 2 abîmés, on n'en
    met que 8 en vente.

    Le moteur ne l'écrase donc JAMAIS. La seule chose qui la
    fait bouger automatiquement, c'est une commande de vente :
    ce qui est vendu n'est plus à vendre. Une réception
    d'achat, un mouvement manuel ou un inventaire ne la
    touchent pas — c'est à l'utilisateur de décider s'il met
    la marchandise en vente, et en quelle quantité.

    Périmètre : produits de type "stock" et "bundle"
    uniquement. Le dropshipping et les précommandes ne
    passent pas par le stock.

    Les bundles n'ont pas de stock à eux : ils sont montés à
    partir des produits à l'unité. Vendre un bundle sort ses
    composants, et sa quantité disponible se calcule au lieu
    d'être stockée. Un bundle n'est jamais valorisé — sa
    valeur est déjà comptée dans ses composants.
    """

    TYPES_GERES = ("stock", "bundle")

    ENTREE = "ENTREE"
    SORTIE = "SORTIE"

    def __init__(self):

        self.db = Database()

    ########################################################
    # Écriture d'un mouvement
    ########################################################

    def enregistrer_mouvement(
        self,
        produit_id,
        type_mouvement,
        quantite,
        origine="",
        reference="",
        prix_unitaire_ht=None,
        commentaire="",
        date_mouvement=None,
        variation_id=None,
    ):
        """
        Écrit une ligne de mouvement et rafraîchit la copie
        de travail. `quantite` est toujours un nombre
        positif : c'est `type_mouvement` qui donne le sens.

        `variation_id` désigne une taille ou une couleur
        précise. Laissé vide, le mouvement porte sur le
        produit entier — c'est le cas de tous les produits
        sans déclinaison.
        """

        if quantite is None or quantite <= 0:
            raise ValueError(
                "La quantité d'un mouvement doit être "
                "supérieure à zéro."
            )

        if date_mouvement is None:
            date_mouvement = date.today().isoformat()

        self.db.executer(
            """
            INSERT INTO mouvements_stock
                (produit_id, variation_id, date, type, quantite,
                 origine, reference, prix_unitaire_ht,
                 commentaire)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                produit_id,
                variation_id,
                date_mouvement,
                type_mouvement,
                quantite,
                origine,
                reference,
                prix_unitaire_ht,
                commentaire,
            )
        )

        # Une vente retire aussi ce qui vient d'être vendu de
        # la quantité mise en vente sur les canaux. Rien
        # d'autre n'y touche.
        if origine == "commande" and type_mouvement == self.SORTIE:
            self._ajuster_mise_en_vente(
                produit_id, -quantite, variation_id
            )

    def _ajuster_mise_en_vente(
        self, produit_id, delta, variation_id=None
    ):
        """
        Ajuste la quantité mise en vente (celle des exports
        WiziShop et Base), sans jamais descendre sous zéro.

        Ce champ reste la décision de l'utilisateur : on ne
        fait que lui retirer ce qui vient d'être vendu, ou
        lui rendre ce qui a été annulé.
        """

        # Quand la vente porte sur une taille précise,
        # c'est sa propre quantité qu'on ajuste, pas celle
        # du produit parent.
        if variation_id:

            self.db.executer(
                """
                UPDATE produits_variations
                SET quantite_stock = MAX(
                    0, COALESCE(quantite_stock, 0) + ?
                )
                WHERE id = ?
                """,
                (delta, variation_id)
            )
            return

        self.db.executer(
            """
            UPDATE produits
            SET quantite_stock = MAX(
                0, COALESCE(quantite_stock, 0) + ?
            )
            WHERE id = ?
            """,
            (delta, produit_id)
        )

    def _deja_enregistre(self, origine, reference):
        """
        Empêche de compter deux fois la même réception ou la
        même commande si on relance l'opération.
        """

        ligne = self.db.lire_un(
            """
            SELECT COUNT(*) AS nombre
            FROM mouvements_stock
            WHERE origine = ?
              AND reference = ?
            """,
            (origine, str(reference))
        )

        return bool(ligne and ligne["nombre"])

    ########################################################
    # Entrées : réception d'un achat fournisseur
    ########################################################

    def entrer_reception_achat(self, achat_id):
        """
        Fait entrer en stock les lignes d'un achat
        fournisseur. À appeler au moment où l'achat est
        réceptionné, pas quand il est commandé.

        Retourne le nombre de lignes entrées.
        """

        if self._deja_enregistre("achat", achat_id):
            return 0

        achat = self.db.lire_un(
            """
            SELECT numero, date_reception
            FROM achats_fournisseurs
            WHERE id = ?
            """,
            (achat_id,)
        )

        if achat is None:
            raise ValueError("Achat fournisseur introuvable.")

        date_entree = (
            achat["date_reception"]
            or date.today().isoformat()
        )

        lignes = self.db.lire(
            """
            SELECT
                l.produit_id,
                l.variation_id,
                l.quantite,
                l.prix_unitaire_ht,
                p.type_produit
            FROM achats_fournisseurs_lignes l
            LEFT JOIN produits p
                ON p.id = l.produit_id
            WHERE l.achat_id = ?
              AND l.actif = 1
            """,
            (achat_id,)
        )

        entrees = 0

        for ligne in lignes:

            if ligne["type_produit"] not in self.TYPES_GERES:
                continue

            if not ligne["quantite"]:
                continue

            self.enregistrer_mouvement(
                produit_id=ligne["produit_id"],
                type_mouvement=self.ENTREE,
                quantite=ligne["quantite"],
                origine="achat",
                reference=achat_id,
                prix_unitaire_ht=ligne["prix_unitaire_ht"],
                commentaire=f"Réception achat {achat['numero'] or achat_id}",
                date_mouvement=date_entree,
                variation_id=ligne["variation_id"],
            )

            entrees += 1

        return entrees

    ########################################################
    # Sorties : commande client
    ########################################################

    def sortir_commande(self, commande_id):
        """
        Sort du stock les produits d'une commande client. Un
        bundle sort ses composants, jamais lui-même.

        Retourne le nombre de mouvements écrits.
        """

        if self._deja_enregistre("commande", commande_id):
            return 0

        commande = self.db.lire_un(
            """
            SELECT numero, date_commande
            FROM commandes
            WHERE id = ?
            """,
            (commande_id,)
        )

        if commande is None:
            raise ValueError("Commande introuvable.")

        date_sortie = (
            commande["date_commande"]
            or date.today().isoformat()
        )

        lignes = self.db.lire(
            """
            SELECT
                l.produit_id,
                l.variation_id,
                l.quantite,
                p.type_produit
            FROM lignes_commandes l
            LEFT JOIN produits p
                ON p.id = l.produit_id
            WHERE l.commande_id = ?
              AND l.actif = 1
            """,
            (commande_id,)
        )

        sorties = 0

        for ligne in lignes:

            if ligne["type_produit"] not in self.TYPES_GERES:
                continue

            quantite_vendue = ligne["quantite"] or 0

            if quantite_vendue <= 0:
                continue

            for produit_id, variation_id, quantite in self._decomposer(
                ligne["produit_id"],
                ligne["type_produit"],
                quantite_vendue,
                ligne["variation_id"],
            ):

                self.enregistrer_mouvement(
                    produit_id=produit_id,
                    type_mouvement=self.SORTIE,
                    quantite=quantite,
                    origine="commande",
                    reference=commande_id,
                    commentaire=(
                        f"Commande {commande['numero'] or commande_id}"
                    ),
                    date_mouvement=date_sortie,
                    variation_id=variation_id,
                )

                sorties += 1

        return sorties

    def _decomposer(
        self, produit_id, type_produit, quantite_vendue,
        variation_id=None,
    ):
        """
        Traduit une ligne vendue en mouvements réels. Un
        produit à l'unité sort tel quel ; un bundle sort ses
        composants, multipliés par la quantité vendue.

        Renvoie des triplets (produit, variation, quantité).
        Un bundle n'a pas de taille : ses composants sortent
        sans variation.
        """

        if type_produit != "bundle":
            return [(produit_id, variation_id, quantite_vendue)]

        return [
            (
                composant["produit_id"],
                None,
                composant["quantite"] * quantite_vendue,
            )
            for composant in self.composants(produit_id)
        ]

    def annuler_sortie_commande(self, commande_id):
        """
        Annule les sorties d'une commande (commande
        supprimée ou annulée) en supprimant ses mouvements.
        """

        mouvements = self.db.lire(
            """
            SELECT produit_id, variation_id, quantite
            FROM mouvements_stock
            WHERE origine = 'commande'
              AND reference = ?
              AND type = 'SORTIE'
            """,
            (str(commande_id),)
        )

        self.db.executer(
            """
            DELETE FROM mouvements_stock
            WHERE origine = 'commande'
              AND reference = ?
            """,
            (str(commande_id),)
        )

        # La marchandise redevient disponible à la vente.
        for mouvement in mouvements:
            self._ajuster_mise_en_vente(
                mouvement["produit_id"],
                mouvement["quantite"],
                mouvement["variation_id"],
            )

        return len(mouvements)

    def annuler_entree_achat(self, achat_id):
        """
        Annule l'entree en stock d'un achat (achat
        supprime, ou repasse a un statut non recu).
        """

        produits = self.db.lire(
            """
            SELECT DISTINCT produit_id
            FROM mouvements_stock
            WHERE origine = 'achat'
              AND reference = ?
            """,
            (str(achat_id),)
        )

        self.db.executer(
            """
            DELETE FROM mouvements_stock
            WHERE origine = 'achat'
              AND reference = ?
            """,
            (str(achat_id),)
        )

        # La quantité mise en vente n'est pas touchée : c'est
        # l'utilisateur qui décide ce qu'il propose.

        return len(produits)

    ########################################################
    # Création d'un produit : stock de départ
    ########################################################

    def initialiser_produit(self, produit_id):
        """
        À la création d'une fiche produit de type "stock",
        reprend la quantité et le prix d'achat saisis dans la
        fiche pour créer l'entrée de départ.

        Sans ça, un produit tout neuf apparaîtrait à zéro
        dans l'écran Stock alors que sa fiche annonce une
        quantité.

        Ne fait rien si le produit a déjà une entrée de
        départ, ou si sa fiche ne porte aucune quantité.
        """

        if self._deja_enregistre("creation", produit_id):
            return 0

        produit = self.db.lire_un(
            """
            SELECT
                type_produit,
                quantite_stock,
                prix_achat_gestion,
                prix_fournisseur_ht
            FROM produits
            WHERE id = ?
            """,
            (produit_id,)
        )

        if produit is None:
            return 0

        if produit["type_produit"] != "stock":
            return 0

        quantite = produit["quantite_stock"] or 0

        if quantite <= 0:
            return 0

        prix = (
            produit["prix_achat_gestion"]
            or produit["prix_fournisseur_ht"]
            or None
        )

        self.enregistrer_mouvement(
            produit_id=produit_id,
            type_mouvement=self.ENTREE,
            quantite=quantite,
            origine="creation",
            reference=produit_id,
            prix_unitaire_ht=prix,
            commentaire="Stock de départ saisi à la création de la fiche",
        )

        return quantite

    def initialiser_variation(self, variation_id):
        """
        Fait entrer en stock la quantité saisie sur une
        taille dans l'onglet Variations.

        Sans ça, une référence créée avec 5 exemplaires
        apparaîtrait à zéro dans l'écran Stock.

        Ne fait rien si cette taille a déjà une entrée de
        départ, ou si aucune quantité n'a été saisie.
        """

        deja = self.db.lire_un(
            """
            SELECT COUNT(*) AS total
            FROM mouvements_stock
            WHERE variation_id = ? AND origine = 'creation'
            """,
            (variation_id,)
        )

        if deja and deja["total"]:
            return 0

        variation = self.db.lire_un(
            """
            SELECT v.produit_id, v.libelle, v.quantite_stock,
                   v.prix_achat_ht,
                   p.prix_achat_gestion, p.prix_fournisseur_ht
            FROM produits_variations v
            LEFT JOIN produits p ON p.id = v.produit_id
            WHERE v.id = ?
            """,
            (variation_id,)
        )

        if variation is None:
            return 0

        quantite = variation["quantite_stock"] or 0

        if quantite <= 0:
            return 0

        prix = (
            variation["prix_achat_ht"]
            or variation["prix_achat_gestion"]
            or variation["prix_fournisseur_ht"]
            or None
        )

        self.enregistrer_mouvement(
            produit_id=variation["produit_id"],
            type_mouvement=self.ENTREE,
            quantite=quantite,
            origine="creation",
            reference=variation["produit_id"],
            prix_unitaire_ht=prix,
            commentaire=(
                f"Stock de départ — {variation['libelle'] or ''}"
            ),
            variation_id=variation_id,
        )

        return quantite

    ########################################################
    # Mouvement saisi à la main depuis l'écran Stock
    ########################################################

    def mouvement_manuel(
        self,
        produit_id,
        sens,
        quantite,
        date_mouvement,
        motif,
        prix_unitaire_ht=None,
    ):
        """
        Entrée ou sortie saisie à la main : casse, perte,
        retour fournisseur, cadeau, régularisation...

        `sens` vaut "ENTREE" ou "SORTIE". Le motif est
        obligatoire : c'est lui qui justifie le mouvement
        dans l'historique.

        La quantité mise en vente n'est pas touchée — seule
        une commande de vente la fait bouger.
        """

        if sens not in (self.ENTREE, self.SORTIE):
            raise ValueError("Le sens doit être ENTREE ou SORTIE.")

        if not (motif or "").strip():
            raise ValueError(
                "Un mouvement manuel doit toujours porter un "
                "motif."
            )

        self.enregistrer_mouvement(
            produit_id=produit_id,
            type_mouvement=sens,
            quantite=quantite,
            origine="manuel",
            reference="",
            prix_unitaire_ht=(
                prix_unitaire_ht
                if sens == self.ENTREE else None
            ),
            commentaire=motif.strip(),
            date_mouvement=date_mouvement,
        )

    ########################################################
    # Correction manuelle (inventaire)
    ########################################################

    def corriger(self, produit_id, quantite_reelle, commentaire=""):
        """
        Aligne le stock sur un comptage physique. Écrit
        l'écart comme un mouvement, pour qu'il reste
        visible dans l'historique.
        """

        ecart = quantite_reelle - self.quantite(produit_id)

        if ecart == 0:
            return 0

        # Le sens est porté par le type du mouvement, jamais
        # par le signe de la quantité : un comptage à la
        # baisse écrit une vraie sortie. C'est `origine` qui
        # dit qu'il s'agit d'un inventaire et non d'une
        # vente.
        self.enregistrer_mouvement(
            produit_id=produit_id,
            type_mouvement=(
                self.ENTREE if ecart > 0 else self.SORTIE
            ),
            quantite=abs(ecart),
            origine="inventaire",
            reference="",
            prix_unitaire_ht=(
                self.prix_moyen(produit_id) if ecart > 0 else None
            ),
            commentaire=commentaire or "Correction d'inventaire",
        )

        return ecart

    ########################################################
    # Bundles
    ########################################################

    def composants(self, bundle_id):

        return self.db.lire(
            """
            SELECT
                c.produit_id,
                c.quantite,
                p.nom,
                p.sku
            FROM bundles_composants c
            LEFT JOIN produits p
                ON p.id = c.produit_id
            WHERE c.bundle_id = ?
              AND c.actif = 1
            """,
            (bundle_id,)
        )

    def definir_composants(self, bundle_id, composants):
        """
        Remplace la composition d'un bundle.
        `composants` : liste de (produit_id, quantite).
        """

        self.db.executer(
            "DELETE FROM bundles_composants WHERE bundle_id = ?",
            (bundle_id,)
        )

        for produit_id, quantite in composants:

            if not produit_id or not quantite or quantite <= 0:
                continue

            self.db.executer(
                """
                INSERT INTO bundles_composants
                    (bundle_id, produit_id, quantite, actif)
                VALUES (?, ?, ?, 1)
                """,
                (bundle_id, produit_id, quantite)
            )

    def quantite_bundle(self, bundle_id):
        """
        Combien de bundles on peut monter avec le stock
        actuel. C'est toujours le composant le plus rare qui
        commande.
        """

        composants = self.composants(bundle_id)

        if not composants:
            return 0

        possibles = []

        for composant in composants:

            besoin = composant["quantite"] or 0

            if besoin <= 0:
                continue

            possibles.append(
                self.quantite(composant["produit_id"]) // besoin
            )

        if not possibles:
            return 0

        return max(0, min(possibles))

    ########################################################
    # Lecture : quantités et valeur
    ########################################################

    def quantite(self, produit_id, variation_id=None):
        """
        Quantité réelle, recalculée depuis les mouvements.

        Sans variation précisée, on additionne tout ce qui
        concerne le produit — ses tailles comprises. C'est
        donc le stock du t-shirt, toutes tailles confondues.
        """

        if variation_id:

            ligne = self.db.lire_un(
                """
                SELECT COALESCE(SUM(
                    CASE
                        WHEN type = 'SORTIE' THEN -quantite
                        ELSE quantite
                    END
                ), 0) AS total
                FROM mouvements_stock
                WHERE variation_id = ?
                """,
                (variation_id,)
            )

            return int(ligne["total"] if ligne else 0)

        ligne = self.db.lire_un(
            """
            SELECT COALESCE(SUM(
                CASE
                    WHEN type = 'SORTIE' THEN -quantite
                    ELSE quantite
                END
            ), 0) AS total
            FROM mouvements_stock
            WHERE produit_id = ?
            """,
            (produit_id,)
        )

        return int(ligne["total"] if ligne else 0)

    def prix_moyen(self, produit_id, variation_id=None):
        """
        Prix d'achat moyen pondéré.

        On rejoue les mouvements dans l'ordre : chaque
        entrée fait bouger la moyenne au prorata des
        quantités, les sorties la laissent inchangée.
        """

        if variation_id:

            mouvements = self.db.lire(
                """
                SELECT type, quantite, prix_unitaire_ht
                FROM mouvements_stock
                WHERE variation_id = ?
                ORDER BY date, id
                """,
                (variation_id,)
            )

        else:

            mouvements = self.db.lire(
                """
                SELECT type, quantite, prix_unitaire_ht
                FROM mouvements_stock
                WHERE produit_id = ?
                ORDER BY date, id
                """,
                (produit_id,)
            )

        quantite = 0
        moyenne = 0.0

        for mouvement in mouvements:

            nombre = mouvement["quantite"] or 0

            if mouvement["type"] == "SORTIE":
                quantite = max(0, quantite - nombre)
                continue

            prix = mouvement["prix_unitaire_ht"]

            if prix is None:
                quantite += nombre
                continue

            total = quantite * moyenne + nombre * float(prix)
            quantite += nombre

            if quantite > 0:
                moyenne = total / quantite

        return round(moyenne, 4)

    def valeur(self, produit_id, variation_id=None):

        return round(
            self.quantite(produit_id, variation_id)
            * self.prix_moyen(produit_id, variation_id),
            2
        )

    def valeur_totale(self):
        """
        Valeur de tout le stock. Les bundles sont exclus :
        leur valeur est déjà dans leurs composants, les
        compter reviendrait à compter deux fois.
        """

        produits = self.db.lire(
            """
            SELECT id
            FROM produits
            WHERE type_produit = 'stock'
              AND actif = 1
            """
        )

        return round(
            sum(self.valeur(produit["id"]) for produit in produits),
            2
        )

    ########################################################
    # Lecture : tableau de l'écran Stock
    ########################################################

    def etat_stock(self):
        """
        Une ligne par produit géré. Les bundles ont une
        quantité calculée et aucune valeur.
        """

        produits = self.db.lire(
            """
            SELECT id, sku, ean, nom, type_produit
            FROM produits
            WHERE type_produit IN ('stock', 'bundle')
              AND actif = 1
            ORDER BY type_produit, nom
            """
        )

        etat = []

        for produit in produits:

            est_bundle = produit["type_produit"] == "bundle"

            if est_bundle:

                etat.append({
                    "produit_id": produit["id"],
                    "variation_id": None,
                    "sku": produit["sku"] or "",
                    "ean": produit["ean"] or "",
                    "nom": produit["nom"] or "",
                    "type": "Bundle",
                    "quantite": self.quantite_bundle(produit["id"]),
                    "prix_moyen": None,
                    "valeur": None,
                })

                continue

            # Un produit à variations n'a pas de stock à lui :
            # ce sont ses tailles qui en ont un. On affiche
            # donc une ligne par référence vendable, sinon on
            # ne saurait jamais s'il reste des XL.
            variations = self.db.lire(
                """
                SELECT id, sku, ean, libelle
                FROM produits_variations
                WHERE produit_id = ? AND actif = 1
                ORDER BY ordre, id
                """,
                (produit["id"],)
            )

            if variations:

                for variation in variations:

                    etat.append({
                        "produit_id": produit["id"],
                        "variation_id": variation["id"],
                        "sku": variation["sku"] or "",
                        "ean": variation["ean"] or "",
                        "nom": (
                            f"{produit['nom'] or ''} "
                            f"— {variation['libelle'] or ''}"
                        ),
                        "type": "Variation",
                        "quantite": self.quantite(
                            produit["id"], variation["id"]
                        ),
                        "prix_moyen": self.prix_moyen(
                            produit["id"], variation["id"]
                        ),
                        "valeur": self.valeur(
                            produit["id"], variation["id"]
                        ),
                    })

                continue

            etat.append({
                "produit_id": produit["id"],
                "variation_id": None,
                "sku": produit["sku"] or "",
                "ean": produit["ean"] or "",
                "nom": produit["nom"] or "",
                "type": "Stock",
                "quantite": self.quantite(produit["id"]),
                "prix_moyen": self.prix_moyen(produit["id"]),
                "valeur": self.valeur(produit["id"]),
            })

        return etat

    def mouvements(self, produit_id=None, limite=None, variation_id=None):
        """
        Historique des entrées et sorties, du plus récent au
        plus ancien.
        """

        conditions = ""
        parametres = []

        if variation_id is not None:
            conditions = "WHERE m.variation_id = ?"
            parametres.append(variation_id)

        elif produit_id is not None:
            conditions = "WHERE m.produit_id = ?"
            parametres.append(produit_id)

        limitation = f"LIMIT {int(limite)}" if limite else ""

        return self.db.lire(
            f"""
            SELECT
                m.id,
                m.date,
                m.type,
                m.quantite,
                m.origine,
                m.reference,
                m.prix_unitaire_ht,
                m.commentaire,
                p.nom AS nom_produit,
                p.sku,
                m.variation_id,
                v.libelle AS libelle_variation
            FROM mouvements_stock m
            LEFT JOIN produits p
                ON p.id = m.produit_id
            LEFT JOIN produits_variations v
                ON v.id = m.variation_id
            {conditions}
            ORDER BY m.date DESC, m.id DESC
            {limitation}
            """,
            tuple(parametres)
        )