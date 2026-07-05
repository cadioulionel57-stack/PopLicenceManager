from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.entity_dialog import EntityDialog
from modules.reference_manager import ReferenceManager


class LicencesPage(ListPage):

    def __init__(self):

        super().__init__("🏷️ Gestion des licences")

        self.manager = ReferenceManager()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nom",
            "Description",
            "Couleur",
            "Produits",
            "Active"
        ])

        # Masquer la colonne ID
        self.table.setColumnHidden(0, True)

        # Connexions
        self.btnAjouter.clicked.connect(self.ajouterLicence)
        self.btnModifier.clicked.connect(self.modifierLicence)
        self.btnSupprimer.clicked.connect(self.supprimerLicence)

        self.table.doubleClicked.connect(self.modifierLicence)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        licences = self.manager.tous("licences")

        for ligne, licence in enumerate(licences):

            self.table.insertRow(ligne)

            self.table.setItem(
                ligne,
                0,
                QTableWidgetItem(str(licence["id"]))
            )

            self.table.setItem(
                ligne,
                1,
                QTableWidgetItem(licence["nom"] or "")
            )

            self.table.setItem(
                ligne,
                2,
                QTableWidgetItem(licence["description"] or "")
            )

            self.table.setItem(
                ligne,
                3,
                QTableWidgetItem(licence["couleur"] or "")
            )

            self.table.setItem(
                ligne,
                4,
                QTableWidgetItem("0")
            )

            self.table.setItem(
                ligne,
                5,
                QTableWidgetItem(
                    "Oui" if licence["actif"] else "Non"
                )
            )

    def ajouterLicence(self):

        dialog = EntityDialog("Nouvelle licence")

        if dialog.exec() != EntityDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            "licences",
            nom,
            dialog.description.toPlainText(),
            dialog.actif.isChecked()
        )

        self.charger()

    def modifierLicence(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une licence."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        licence = self.manager.obtenir(
            "licences",
            identifiant
        )

        dialog = EntityDialog(
            "Modifier la licence",
            licence["nom"],
            licence["description"] or "",
            bool(licence["actif"])
        )

        if dialog.exec() != EntityDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            "licences",
            identifiant,
            nom,
            dialog.description.toPlainText(),
            dialog.actif.isChecked()
        )

        self.charger()

    def supprimerLicence(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une licence."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cette licence ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        self.manager.supprimer(
            "licences",
            identifiant
        )

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