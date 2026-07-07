from PySide6.QtWidgets import QComboBox

from modules.reference_manager import ReferenceManager


class ReferenceComboBox(QComboBox):
    """
    Menu déroulant générique, alimenté automatiquement
    depuis une table de référence (fournisseurs, licences,
    marques, catégories, canaux de vente...).

    filtre_colonne / filtre_valeur permettent de ne charger
    qu'une partie des lignes d'une table (voir
    ReferenceManager.tous pour le détail du comportement).
    """

    def __init__(self, table, filtre_colonne=None, filtre_valeur=None):

        super().__init__()

        self.manager = ReferenceManager()
        self.table = table
        self.filtre_colonne = filtre_colonne
        self.filtre_valeur = filtre_valeur

        self.charger()

    def charger(self):

        self.clear()

        self.addItem("")

        elements = self.manager.tous(
            self.table,
            self.filtre_colonne,
            self.filtre_valeur
        )

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