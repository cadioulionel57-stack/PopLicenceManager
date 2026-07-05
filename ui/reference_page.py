from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.entity_dialog import EntityDialog


class ReferencePage(ListPage):

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