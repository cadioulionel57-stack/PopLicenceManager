from database.database import Database


class BlocLivraisonManager:
    """
    Gère le bloc HTML réutilisable « Optimisez votre
    livraison » — un seul exemplaire, modifiable une fois
    pour toutes, inséré automatiquement dans toutes les
    fiches produit via {{bloc_livraison}}.

    Avant, ce pavé était recopié dans chaque modèle : changer
    un tarif obligeait à rouvrir tous les modèles un par un.
    """

    def obtenir(self):

        db = Database()

        ligne = db.lire_un(
            "SELECT * FROM bloc_livraison LIMIT 1"
        )

        if ligne is None:
            return ""

        return ligne["html_template"] or ""

    def definir(self, html_template):

        db = Database()

        ligne = db.lire_un(
            "SELECT id FROM bloc_livraison LIMIT 1"
        )

        if ligne is None:

            db.executer(
                "INSERT INTO bloc_livraison (html_template) VALUES (?)",
                (html_template,)
            )
            return

        db.executer(
            "UPDATE bloc_livraison SET html_template = ? WHERE id = ?",
            (html_template, ligne["id"])
        )