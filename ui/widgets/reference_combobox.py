from PySide6.QtWidgets import QComboBox

from modules.reference_manager import ReferenceManager


class ReferenceComboBox(QComboBox):

    def __init__(self, table):

        super().__init__()

        self.manager = ReferenceManager()
        self.table = table

        self.charger()

    def charger(self):

        self.clear()

        self.addItem("")

        elements = self.manager.tous(self.table)

        for element in elements:

            self.addItem(
                element["nom"],
                element["id"]
            )

    def id(self):

        return self.currentData()

    def texte(self):

        return self.currentText()

    def selectionner(self, identifiant):

        for i in range(self.count()):

            if self.itemData(i) == identifiant:

                self.setCurrentIndex(i)
                return