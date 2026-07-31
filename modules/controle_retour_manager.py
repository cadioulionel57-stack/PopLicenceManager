from database.database import Database


class ControleRetourManager:
    """
    Contrôle des articles renvoyés par un client.

    Quand un retour arrive, on scanne le code-barres de ce
    qui est dans le carton et on le compare à celui qui avait
    été expédié. L'arnaque classique n'est pas la fausse
    réclamation : c'est le renvoi d'un autre exemplaire,
    abîmé, contrefait, ou d'une boîte vide.

    Le résultat est enregistré sur le retour, dans les
    colonnes ean_controle et ean_conforme.
    """

    def __init__(self):

        self.db = Database()

    def eans_attendus_ligne(self, ligne_commande_id):
        """
        Renvoie les codes-barres qui peuvent légitimement
        revenir pour cette ligne de commande : celui du
        produit, et ceux de ses déclinaisons quand il en a
        (chaque taille a son propre EAN).
        """

        if ligne_commande_id is None:
            return []

        ligne = self.db.lire_un(
            """
            SELECT produit_id
            FROM lignes_commandes
            WHERE id = ?
            """,
            (ligne_commande_id,)
        )

        if ligne is None or ligne["produit_id"] is None:
            return []

        codes = []

        produit = self.db.lire_un(
            """
            SELECT ean FROM produits WHERE id = ?
            """,
            (ligne["produit_id"],)
        )

        if produit is not None and produit["ean"]:
            codes.append(str(produit["ean"]).strip())

        declinaisons = self.db.lire(
            """
            SELECT ean, libelle
            FROM produits_variations
            WHERE produit_id = ?
            """,
            (ligne["produit_id"],)
        )

        for declinaison in declinaisons:

            if declinaison["ean"]:
                codes.append(str(declinaison["ean"]).strip())

        return codes

    def controler(self, retour_id, ean_scanne):
        """
        Compare le code-barres scanné à ceux attendus,
        enregistre le résultat et renvoie True si l'article
        renvoyé est bien celui qui avait été expédié.
        """

        retour = self.db.lire_un(
            """
            SELECT ligne_commande_id
            FROM commandes_retours
            WHERE id = ?
            """,
            (retour_id,)
        )

        if retour is None:
            return False

        attendus = self.eans_attendus_ligne(
            retour["ligne_commande_id"]
        )

        scanne = (ean_scanne or "").strip()

        conforme = scanne != "" and scanne in attendus

        self.db.executer(
            """
            UPDATE commandes_retours
            SET ean_controle = ?, ean_conforme = ?
            WHERE id = ?
            """,
            (scanne, 1 if conforme else 0, retour_id)
        )

        return conforme

    def verifier_sans_enregistrer(
        self,
        ligne_commande_id,
        ean_scanne
    ):
        """
        Même comparaison, mais sans rien écrire en base :
        sert à afficher le vert ou le rouge à l'écran tant
        que la commande n'a pas encore été enregistrée.
        """

        attendus = self.eans_attendus_ligne(ligne_commande_id)

        scanne = (ean_scanne or "").strip()

        return scanne != "" and scanne in attendus

    def resultat(self, retour_id):
        """
        Renvoie le dernier contrôle effectué sur un retour,
        sous la forme (code_scanne, conforme), ou (None,
        None) si aucun contrôle n'a encore été fait.
        """

        ligne = self.db.lire_un(
            """
            SELECT ean_controle, ean_conforme
            FROM commandes_retours
            WHERE id = ?
            """,
            (retour_id,)
        )

        if ligne is None or not ligne["ean_controle"]:
            return (None, None)

        return (
            ligne["ean_controle"],
            bool(ligne["ean_conforme"])
        )