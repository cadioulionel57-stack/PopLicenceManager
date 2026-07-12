from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage
from ui.entity_dialog import EntityDialog


class MarquesPage(ReferencePage):
    """
    Gestion des marques — avec en plus l'ID WiziShop de
    chaque marque, obligatoire pour l'export du catalogue
    produits.
    """

    def __init__(self):

        super().__init__(
            "™️ Gestion des marques",
            "marques",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "ID WiziShop",
                "Description",
                "Active"
            ]
        )

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        donnees = self.manager.tous(self.table_name)

        for ligne, element in enumerate(donnees):

            self.table.insertRow(ligne)

            valeurs = [
                str(element["id"]),
                element["nom"] or "",
                element["id_wizishop"] or "",
                element["description"] or "",
                "Oui" if element["actif"] else "Non",
            ]

            for colonne, valeur in enumerate(valeurs):
                self.table.setItem(
                    ligne, colonne, QTableWidgetItem(valeur)
                )

    def ajouterElement(self):

        dialog = EntityDialog(
            "Nouvelle marque",
            champ_supplementaire_label="ID WiziShop (le #N de cette "
            "marque sur WiziShop)",
        )

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

        # Récupère l'id fraîchement créé pour y attacher
        # l'ID WiziShop (ajouter() ne le gère pas, générique
        # à toutes les tables de référence).
        toutes = self.manager.tous(self.table_name)
        nouvelle = next((m for m in toutes if m["nom"] == nom), None)

        if nouvelle is not None and dialog.champSupplementaire.text().strip():

            self.manager.definir_champ(
                self.table_name, nouvelle["id"], "id_wizishop",
                dialog.champSupplementaire.text().strip()
            )

        self.charger()

    def modifierElement(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(
                self, "Information", "Sélectionnez un élément."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())

        element = self.manager.obtenir(self.table_name, identifiant)

        dialog = EntityDialog(
            "Modifier la marque",
            element["nom"],
            element["description"] or "",
            bool(element["actif"]),
            champ_supplementaire_label="ID WiziShop (le #N de cette "
            "marque sur WiziShop)",
            champ_supplementaire_valeur=element["id_wizishop"] or "",
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

        self.manager.definir_champ(
            self.table_name, identifiant, "id_wizishop",
            dialog.champSupplementaire.text().strip()
        )

        self.charger()