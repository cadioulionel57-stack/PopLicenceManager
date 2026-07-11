from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.entity_dialog import EntityDialog


class ReferencePage(ListPage):
    """
    Écran générique pour une table de référence simple
    (id, nom, description, actif) : Marques, et toute autre
    liste future du même genre.

    Contrairement à Licences (qui gère sa logique en
    interne, car elle a des colonnes en plus), cette page
    factorise tout le CRUD une seule fois ici — pas besoin
    de le réécrire pour chaque nouvelle table de ce type.
    """

    def __init__(
        self,
        titre,
        table,
        manager,
        colonnes
    ):

        super().__init__(titre)

        self.table_name = table
        self.manager = manager

        self.table.setColumnCount(len(colonnes))
        self.table.setHorizontalHeaderLabels(colonnes)

        # La première colonne est toujours l'ID
        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterElement)
        self.btnModifier.clicked.connect(self.modifierElement)
        self.btnSupprimer.clicked.connect(self.supprimerElement)

        self.table.doubleClicked.connect(self.modifierElement)

        self.recherche.textChanged.connect(self.filtrer)

    def charger(self):

        self.table.setRowCount(0)

        donnees = self.manager.tous(self.table_name)

        for ligne, element in enumerate(donnees):

            self.table.insertRow(ligne)

            self.table.setItem(
                ligne,
                0,
                QTableWidgetItem(str(element["id"]))
            )

            self.table.setItem(
                ligne,
                1,
                QTableWidgetItem(element["nom"] or "")
            )

            description = ""

            if "description" in element.keys():
                description = element["description"] or ""

            self.table.setItem(
                ligne,
                2,
                QTableWidgetItem(description)
            )

            actif = "Oui"

            if "actif" in element.keys():
                actif = "Oui" if element["actif"] else "Non"

            self.table.setItem(
                ligne,
                3,
                QTableWidgetItem(actif)
            )

    def ajouterElement(self):

        dialog = EntityDialog(f"Nouveau — {self.table_name}")

        if dialog.exec() != EntityDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            self.table_name,
            nom,
            dialog.description.toPlainText(),
            dialog.actif.isChecked()
        )

        self.charger()

    def modifierElement(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un élément."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        element = self.manager.obtenir(
            self.table_name,
            identifiant
        )

        dialog = EntityDialog(
            f"Modifier — {self.table_name}",
            element["nom"],
            element["description"] or "",
            bool(element["actif"])
        )

        if dialog.exec() != EntityDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            self.table_name,
            identifiant,
            nom,
            dialog.description.toPlainText(),
            dialog.actif.isChecked()
        )

        self.charger()

    def supprimerElement(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un élément."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cet élément ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        self.manager.supprimer(
            self.table_name,
            identifiant
        )

        self.charger()

    def filtrer(self):

        texte = self.recherche.text().lower().strip()

        for ligne in range(self.table.rowCount()):

            visible = False

            for colonne in range(1, self.table.columnCount()):

                item = self.table.item(ligne, colonne)

                if item and texte in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(
                ligne,
                not visible
            )