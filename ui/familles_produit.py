from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.famille_produit_dialog import FamilleProduitDialog
from modules.famille_produit_manager import FamilleProduitManager


class FamillesProduitPage(ListPage):
    """
    Écran de gestion des familles de produit (Textile &
    Mode, Chaussures, Linge de maison...), utilisées pour
    calculer le coût de revient (emballage + provision
    retour) de chaque produit.
    """

    def __init__(self):

        super().__init__("🏭 Familles de produit")

        self.manager = FamilleProduitManager()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nom",
            "Coût emballage HT",
            "Taux de retour",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterFamille)
        self.btnModifier.clicked.connect(self.modifierFamille)
        self.btnSupprimer.clicked.connect(self.supprimerFamille)

        self.table.doubleClicked.connect(self.modifierFamille)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        familles = self.manager.tous()

        for ligne, famille in enumerate(familles):

            self.table.insertRow(ligne)

            valeurs = [
                str(famille["id"]),
                famille["nom"] or "",
                f"{famille['cout_emballage_ht'] or 0:.2f} €",
                f"{(famille['taux_retour'] or 0) * 100:.1f} %",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterFamille(self):

        dialog = FamilleProduitDialog("Nouvelle famille de produit")

        if dialog.exec() != FamilleProduitDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            nom=nom,
            cout_emballage_ht=dialog.coutEmballage.value(),
            taux_retour=dialog.taux_retour_decimal(),
        )

        self.charger()

    def modifierFamille(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une famille de produit."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        famille = self.manager.obtenir(identifiant)

        dialog = FamilleProduitDialog(
            "Modifier la famille de produit",
            nom=famille["nom"],
            cout_emballage_ht=famille["cout_emballage_ht"] or 0,
            taux_retour=famille["taux_retour"] or 0,
        )

        if dialog.exec() != FamilleProduitDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant=identifiant,
            nom=nom,
            cout_emballage_ht=dialog.coutEmballage.value(),
            taux_retour=dialog.taux_retour_decimal(),
        )

        self.charger()

    def supprimerFamille(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une famille de produit."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cette famille de produit ?"
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