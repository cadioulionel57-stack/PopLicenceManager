from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.grille_transport_dialog import GrilleTransportDialog
from modules.grille_transport_manager import GrilleTransportManager


class GrilleTransportPage(ListPage):
    """
    Écran de gestion de la grille tarifaire des
    transporteurs (basée sur Boxtal), utilisée pour
    calculer automatiquement le coût de transport d'un
    produit selon son poids.
    """

    def __init__(self):

        super().__init__("🚚 Grille de transport")

        self.manager = GrilleTransportManager()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Transporteur",
            "Offre",
            "Jusqu'à (kg)",
            "Prix HT",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterLigne)
        self.btnModifier.clicked.connect(self.modifierLigne)
        self.btnSupprimer.clicked.connect(self.supprimerLigne)

        self.table.doubleClicked.connect(self.modifierLigne)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        lignes = self.manager.tous()

        for ligne_index, ligne in enumerate(lignes):

            self.table.insertRow(ligne_index)

            valeurs = [
                str(ligne["id"]),
                ligne["transporteur"] or "",
                ligne["offre"] or "",
                f"{ligne['poids_max_kg']:.2f} kg",
                f"{ligne['prix_ht']:.2f} €",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne_index,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterLigne(self):

        dialog = GrilleTransportDialog("Nouvelle ligne de tarif")

        if dialog.exec() != GrilleTransportDialog.DialogCode.Accepted:
            return

        if dialog.transporteur_id() is None:

            QMessageBox.information(
                self,
                "Information",
                "Choisissez un transporteur "
                "(créez-le d'abord si besoin)."
            )
            return

        self.manager.ajouter(
            transporteur_id=dialog.transporteur_id(),
            offre=dialog.offre.text().strip(),
            poids_max_kg=dialog.poidsMax.value(),
            prix_ht=dialog.prixHt.value(),
        )

        self.charger()

    def modifierLigne(self):

        ligne_selection = self.table.currentRow()

        if ligne_selection == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une ligne de tarif."
            )
            return

        identifiant = int(
            self.table.item(ligne_selection, 0).text()
        )

        ligne = self.manager.obtenir(identifiant)

        dialog = GrilleTransportDialog(
            "Modifier la ligne de tarif",
            transporteur_id=ligne["transporteur_id"],
            offre=ligne["offre"],
            poids_max_kg=ligne["poids_max_kg"],
            prix_ht=ligne["prix_ht"],
        )

        if dialog.exec() != GrilleTransportDialog.DialogCode.Accepted:
            return

        self.manager.modifier(
            identifiant=identifiant,
            transporteur_id=dialog.transporteur_id(),
            offre=dialog.offre.text().strip(),
            poids_max_kg=dialog.poidsMax.value(),
            prix_ht=dialog.prixHt.value(),
        )

        self.charger()

    def supprimerLigne(self):

        ligne_selection = self.table.currentRow()

        if ligne_selection == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une ligne de tarif."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cette ligne de tarif ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(
            self.table.item(ligne_selection, 0).text()
        )

        self.manager.supprimer(identifiant)

        self.charger()

    def filtrer(self):

        texte = self.recherche.text().lower().strip()

        for ligne_index in range(self.table.rowCount()):

            afficher = False

            for colonne in range(1, self.table.columnCount()):

                item = self.table.item(ligne_index, colonne)

                if item and texte in item.text().lower():
                    afficher = True
                    break

            self.table.setRowHidden(
                ligne_index,
                not afficher
            )