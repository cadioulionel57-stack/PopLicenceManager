import unicodedata

from database.database import Database


class VariationManager:

    def __init__(self):

        self.db = Database()

    ########################################################
    # Lecture
    ########################################################

    def variations(self, produit_id, actives_seulement=False):
        """
        Toutes les variations d'un produit, avec le détail
        des critères de chacune.
        """

        condition = "AND v.actif = 1" if actives_seulement else ""

        lignes = self.db.lire(f"""
            SELECT * FROM produits_variations v
            WHERE v.produit_id = ? {condition}
            ORDER BY v.ordre, v.id
        """, (produit_id,))

        resultat = []

        for ligne in lignes:

            variation = dict(ligne)
            variation["criteres"] = self.criteres_de(ligne["id"])
            resultat.append(variation)

        return resultat

    def criteres_de(self, variation_id):
        """
        Les critères d'une variation : [(attribut, valeur)].
        """

        return self.db.lire("""
            SELECT a.id AS attribut_id, a.nom AS attribut,
                   val.id AS valeur_id, val.valeur AS valeur,
                   val.ordre AS ordre
            FROM variations_valeurs vv
            JOIN attributs a ON a.id = vv.attribut_id
            JOIN valeurs_attributs val ON val.id = vv.valeur_id
            WHERE vv.variation_id = ?
            ORDER BY a.nom
        """, (variation_id,))

    def selection_actuelle(self, produit_id):
        """
        Reconstruit ce qui avait été coché : quels critères,
        et quelles valeurs pour chacun. Sert à rouvrir la
        fiche dans l'état où on l'avait laissée.
        """

        lignes = self.db.lire("""
            SELECT DISTINCT vv.attribut_id, vv.valeur_id
            FROM variations_valeurs vv
            JOIN produits_variations v ON v.id = vv.variation_id
            WHERE v.produit_id = ?
        """, (produit_id,))

        selection = {}

        for ligne in lignes:
            selection.setdefault(
                ligne["attribut_id"], []
            ).append(ligne["valeur_id"])

        return selection

    def obtenir(self, variation_id):

        return self.db.lire_un(
            "SELECT * FROM produits_variations WHERE id = ?",
            (variation_id,)
        )

    ########################################################
    # Génération
    ########################################################

    def _abreger(self, texte):
        """
        Transforme une valeur en morceau de SKU : sans
        accent, en majuscules, sans espace ni ponctuation.
        « Bleu marine » devient BLEUMARINE.
        """

        texte = unicodedata.normalize("NFD", texte or "")
        texte = "".join(
            c for c in texte
            if unicodedata.category(c) != "Mn"
        )

        return "".join(
            c for c in texte.upper() if c.isalnum()
        )

    def _combinaisons(self, selection):
        """
        Produit cartésien des valeurs retenues.

        selection = {attribut_id: [valeur_id, ...]}

        Renvoie une liste de listes de (attribut_id,
        valeur_id) — une par référence à créer.
        """

        combinaisons = [[]]

        for attribut_id in sorted(selection):

            valeurs = selection[attribut_id]

            if not valeurs:
                continue

            nouvelles = []

            for debut in combinaisons:
                for valeur_id in valeurs:
                    nouvelles.append(
                        debut + [(attribut_id, valeur_id)]
                    )

            combinaisons = nouvelles

        return [c for c in combinaisons if c]

    def _signature(self, criteres):
        """
        Empreinte d'une combinaison, pour reconnaître une
        variation déjà existante et ne pas la recréer.
        """

        return tuple(sorted(criteres))

    def generer(self, produit_id, selection):
        """
        Crée toutes les combinaisons manquantes pour ce
        produit, sans jamais toucher à celles qui existent
        déjà — leurs EAN et leurs stocks sont préservés.

        Renvoie (nombre créées, nombre déjà présentes).
        """

        produit = self.db.lire_un(
            "SELECT sku FROM produits WHERE id = ?", (produit_id,)
        )

        sku_parent = (produit["sku"] if produit else "") or "SKU"

        # Ce qui existe déjà, par empreinte
        existantes = set()

        for variation in self.variations(produit_id):
            existantes.add(self._signature([
                (c["attribut_id"], c["valeur_id"])
                for c in variation["criteres"]
            ]))

        # Libellés des valeurs, pour composer SKU et libellé
        libelles = {}

        for ligne in self.db.lire(
            "SELECT id, valeur, ordre FROM valeurs_attributs"
        ):
            libelles[ligne["id"]] = (ligne["valeur"], ligne["ordre"] or 0)

        creees = 0
        deja = 0

        rang = self.db.lire_un("""
            SELECT MAX(ordre) AS rang FROM produits_variations
            WHERE produit_id = ?
        """, (produit_id,))

        ordre = (rang["rang"] or 0)

        for combinaison in self._combinaisons(selection):

            if self._signature(combinaison) in existantes:
                deja += 1
                continue

            valeurs = [
                libelles.get(valeur_id, ("?", 0))[0]
                for _attribut_id, valeur_id in combinaison
            ]

            libelle = " / ".join(valeurs)

            sku = sku_parent + "".join(
                "-" + self._abreger(v) for v in valeurs
            )

            ordre += 1

            curseur = self.db.executer("""
                INSERT INTO produits_variations
                    (produit_id, sku, libelle, quantite_stock,
                     prix_supplement_ht, ordre, actif)
                VALUES (?, ?, ?, 0, 0, ?, 1)
            """, (produit_id, sku, libelle, ordre))

            variation_id = curseur.lastrowid

            for attribut_id, valeur_id in combinaison:
                self.db.executer("""
                    INSERT INTO variations_valeurs
                        (variation_id, attribut_id, valeur_id)
                    VALUES (?, ?, ?)
                """, (variation_id, attribut_id, valeur_id))

            creees += 1

        self._reordonner(produit_id)

        return creees, deja

    def _reordonner(self, produit_id):
        """
        Range les variations dans l'ordre des valeurs tel
        qu'il a été défini dans Paramètres — S avant M avant
        L, et non l'ordre de création.
        """

        variations = self.variations(produit_id)

        def cle(variation):
            return tuple(
                (c["attribut"], c["ordre"] or 0)
                for c in sorted(
                    variation["criteres"], key=lambda x: x["attribut"]
                )
            )

        for rang, variation in enumerate(
            sorted(variations, key=cle), start=1
        ):
            self.db.executer(
                "UPDATE produits_variations SET ordre = ? WHERE id = ?",
                (rang, variation["id"])
            )

    ########################################################
    # Modification
    ########################################################

    def modifier(self, variation_id, **champs):
        """
        Met à jour les champs saisis à l'écran. On n'écrit
        que ce qui est fourni, pour ne jamais effacer par
        inadvertance une valeur qu'on n'affichait pas.
        """

        autorises = (
            "sku", "ean", "quantite_stock", "prix_supplement_ht",
            "prix_achat_ht", "poids", "actif", "id_wizishop",
        )

        colonnes = []
        valeurs = []

        for nom, valeur in champs.items():

            if nom not in autorises:
                continue

            colonnes.append(f"{nom} = ?")
            valeurs.append(valeur)

        if not colonnes:
            return

        valeurs.append(variation_id)

        self.db.executer(
            f"UPDATE produits_variations SET {', '.join(colonnes)} "
            f"WHERE id = ?",
            valeurs
        )

    def supprimer(self, variation_id):
        """
        Supprime une variation et ses critères. Refuse si
        elle a déjà été vendue ou si elle a bougé en stock :
        on ne fait pas disparaître une référence qui a une
        histoire.
        """

        vendue = self.db.lire_un("""
            SELECT COUNT(*) AS total FROM lignes_commandes
            WHERE variation_id = ?
        """, (variation_id,))

        if vendue and vendue["total"]:
            raise ValueError(
                "Cette référence figure dans des commandes. "
                "Désactive-la plutôt que de la supprimer."
            )

        bougee = self.db.lire_un("""
            SELECT COUNT(*) AS total FROM mouvements_stock
            WHERE variation_id = ?
        """, (variation_id,))

        if bougee and bougee["total"]:
            raise ValueError(
                "Cette référence a un historique de stock. "
                "Désactive-la plutôt que de la supprimer."
            )

        self.db.executer(
            "DELETE FROM variations_valeurs WHERE variation_id = ?",
            (variation_id,)
        )
        self.db.executer(
            "DELETE FROM produits_variations WHERE id = ?",
            (variation_id,)
        )

    def a_des_variations(self, produit_id):

        ligne = self.db.lire_un("""
            SELECT COUNT(*) AS total FROM produits_variations
            WHERE produit_id = ? AND actif = 1
        """, (produit_id,))

        return bool(ligne and ligne["total"])

    def stock_total(self, produit_id):
        """
        Somme des stocks de toutes les variations actives —
        c'est ce que vaut le produit dans son ensemble.
        """

        ligne = self.db.lire_un("""
            SELECT SUM(quantite_stock) AS total
            FROM produits_variations
            WHERE produit_id = ? AND actif = 1
        """, (produit_id,))

        return (ligne["total"] if ligne and ligne["total"] else 0)