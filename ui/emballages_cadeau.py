from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.emballage_cadeau_dialog import EmballageCadeauDialog
from modules.emballage_cadeau_manager import EmballageCadeauManager


class EmballagesCadeauPage(ListPage):
    """
    Gestion de la grille des emballages cadeau — coûts
    d'achat modifiables à tout moment (évolution des
    fournisseurs), séparée de la grille d'emballages
    d'expédition.
    """

    def __init__(self):

        super().__init__("🎁 Emballages Cadeau")

        self.manager = EmballageCadeauManager()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Code",
            "Nom / catégorie",
            "Coût HT",
            "Type",
            "Tarif facturé client",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterEmballage)
        self.btnModifier.clicked.connect(self.modifierEmballage)
        self.btnSupprimer.clicked.connect(self.supprimerEmballage)

        self.table.doubleClicked.connect(self.modifierEmballage)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        emballages = self.manager.tous()

        for ligne, e in enumerate(emballages):

            self.table.insertRow(ligne)

            type_libelle = (
                "Principal (facturé)"
                if e["type"] == "principal"
                else "Supplément (coût seul)"
            )

            tarif_texte = (
                f"{e['tarif_facture_ht']:.2f} €"
                if e["tarif_facture_ht"] is not None
                else "—"
            )

            valeurs = [
                str(e["id"]),
                e["code"] or "",
                e["nom"] or "",
                f"{e['cout_ht'] or 0:.2f} €",
                type_libelle,
                tarif_texte,
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne, colonne, QTableWidgetItem(valeur)
                )

    def ajouterEmballage(self):

        dialog = EmballageCadeauDialog("Nouvel emballage cadeau")

        if dialog.exec() != EmballageCadeauDialog.DialogCode.Accepted:
            return

        code = dialog.code.text().strip()

        if code == "":
            return

        self.manager.ajouter(
            code,
            dialog.nom.text(),
            dialog.coutHt.value(),
            dialog.type_selectionne(),
            dialog.tarifFacture.value()
            if dialog.type_selectionne() == "principal"
            else None,
        )

        self.charger()

    def modifierEmballage(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self, "Information", "Sélectionnez un emballage."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())

        e = self.manager.obtenir(identifiant)

        dialog = EmballageCadeauDialog(
            "Modifier l'emballage cadeau",
            e["code"],
            e["nom"],
            e["cout_ht"],
            e["type"],
            e["tarif_facture_ht"],
        )

        if dialog.exec() != EmballageCadeauDialog.DialogCode.Accepted:
            return

        code = dialog.code.text().strip()

        if code == "":
            return

        self.manager.modifier(
            identifiant,
            code,
            dialog.nom.text(),
            dialog.coutHt.value(),
            dialog.type_selectionne(),
            dialog.tarifFacture.value()
            if dialog.type_selectionne() == "principal"
            else None,
        )

        self.charger()

    def supprimerEmballage(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self, "Information", "Sélectionnez un emballage."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cet emballage ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())

        self.manager.supprimer(identifiant)

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

            self.table.setRowHidden(ligne, not visible)