from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.categorie_dialog import CategorieDialog
from modules.categorie_manager import CategorieManager


class CategoriesPage(ListPage):
    """
    Écran de gestion des catégories : catégories internes
    Pop Licence, et catégories propres à chaque canal de
    vente (Amazon, Cdiscount, WiziShop...).
    """

    def __init__(self):

        super().__init__("📂 Gestion des catégories")

        self.manager = CategorieManager()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nom",
            "Rattachée à",
            "Commission",
            "Active",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterCategorie)
        self.btnModifier.clicked.connect(self.modifierCategorie)
        self.btnSupprimer.clicked.connect(self.supprimerCategorie)

        self.table.doubleClicked.connect(self.modifierCategorie)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        categories = self.manager.tous()

        for ligne, categorie in enumerate(categories):

            self.table.insertRow(ligne)

            paliers = self.manager.paliers(categorie["id"])

            if categorie["canal_id"] is None:
                commission_affichee = "—"
            elif paliers:
                resume = " / ".join(
                    f"≤{p['seuil_prix_max']}€:{p['commission_pourcentage']}%"
                    if p["seuil_prix_max"] is not None
                    else f">:{p['commission_pourcentage']}%"
                    for p in paliers
                )
                commission_affichee = f"Paliers : {resume}"
            elif categorie["commission_pourcentage"] is not None:
                commission_affichee = (
                    f"{categorie['commission_pourcentage']:.2f} % "
                    "(propre à la catégorie)"
                )
            else:
                commission_affichee = (
                    f"{categorie['commission_canal'] or 0:.2f} % "
                    "(défaut du canal)"
                )

            valeurs = [
                str(categorie["id"]),
                categorie["nom"] or "",
                categorie["canal"] or "Pop Licence (interne)",
                commission_affichee,
                "Oui" if categorie["actif"] else "Non",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterCategorie(self):

        dialog = CategorieDialog("Nouvelle catégorie")

        if dialog.exec() != CategorieDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        identifiant = self.manager.ajouter(
            nom=nom,
            canal_id=dialog.canal_id(),
            commission_pourcentage=dialog.commission_pourcentage(),
        )

        self.manager.definir_paliers(
            identifiant,
            dialog.paliers_saisis()
        )

        self.charger()

    def modifierCategorie(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une catégorie."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        categorie = self.manager.obtenir(identifiant)
        paliers_existants = self.manager.paliers(identifiant)

        dialog = CategorieDialog(
            "Modifier la catégorie",
            nom=categorie["nom"],
            canal_id=categorie["canal_id"],
            commission_pourcentage=categorie["commission_pourcentage"],
            paliers=paliers_existants,
        )

        if dialog.exec() != CategorieDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant=identifiant,
            nom=nom,
            canal_id=dialog.canal_id(),
            commission_pourcentage=dialog.commission_pourcentage(),
        )

        self.manager.definir_paliers(
            identifiant,
            dialog.paliers_saisis()
        )

        self.charger()

    def supprimerCategorie(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une catégorie."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cette catégorie ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        self.manager.supprimer(identifiant)

        self.charger()

    def filtrer(self):

        texte = self.recherche.text().lower().strip()

        for ligne in range(self.table.rowCount()):

            afficher = False

            for colonne in range(1, self.table.columnCount()):

                item = self.table.item(ligne, colonne)

                if item and texte in item.text().lower():
                    afficher = True
                    break

            self.table.setRowHidden(
                ligne,
                not afficher
            )