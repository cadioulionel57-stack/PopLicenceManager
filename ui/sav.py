from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)
from PySide6.QtGui import QColor

from ui.list_page import ListPage
from modules.commande_manager import CommandeManager


class SavPage(ListPage):
    """
    Vue transversale de tous les retours/SAV, toutes
    commandes confondues — pour suivre un dossier par
    client ou par commande sans ouvrir chaque commande une
    par une. En lecture seule : pour modifier un retour,
    on ouvre la commande concernée (bouton dédié).
    """

    COULEURS_STATUT = {
        "Demandé": "#e67e22",
        "Reçu": "#2980b9",
        "Remboursé": "#c0392b",
        "Refusé": "#7f8c8d",
    }

    def __init__(self, ouvrir_commande_callback=None):

        super().__init__("🔧 Suivi SAV / Retours")

        self.manager = CommandeManager()
        self.ouvrir_commande_callback = ouvrir_commande_callback

        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels([
            "ID retour",
            "Commande",
            "Client",
            "Produit",
            "Date",
            "Motif",
            "Statut",
            "Remboursé TTC",
            "Coût total SAV",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.setVisible(False)
        self.btnImporter.setVisible(False)
        self.btnExporter.setVisible(False)

        self.btnModifier.setText("📂 Ouvrir la commande")
        self.btnModifier.clicked.connect(self.ouvrirCommande)
        self.btnSupprimer.clicked.connect(self.supprimerRetour)

        self.table.doubleClicked.connect(self.ouvrirCommande)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        retours = self.manager.tous_les_retours()

        for ligne, retour in enumerate(retours):

            self.table.insertRow(ligne)

            cout_total = (
                (retour["montant_rembourse_ttc"] or 0) / 1.2
                + (retour["frais_reexpedition_ht"] or 0)
                + (retour["cout_retour_ht"] or 0)
            )

            valeurs = [
                str(retour["id"]),
                retour["numero_commande"] or "",
                retour["nom_client"] or "",
                retour["nom_produit"] or "",
                retour["date_retour"] or "",
                retour["motif"] or "",
                retour["statut"] or "",
                f"{retour['montant_rembourse_ttc'] or 0:.2f} €",
                f"{cout_total:.2f} €",
            ]

            for colonne, valeur in enumerate(valeurs):

                item = QTableWidgetItem(valeur)

                if colonne == 6:

                    couleur = self.COULEURS_STATUT.get(
                        retour["statut"], "#2c3e50"
                    )
                    item.setForeground(QColor(couleur))

                self.table.setItem(ligne, colonne, item)

    def ouvrirCommande(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un retour."
            )
            return

        numero_commande = self.table.item(ligne, 1).text()

        commande = self.manager.db.lire_un(
            """
            SELECT id
            FROM commandes
            WHERE numero = ?
            """,
            (numero_commande,)
        )

        if commande is None:
            return

        if self.ouvrir_commande_callback:
            self.ouvrir_commande_callback(commande["id"])

    def supprimerRetour(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un retour."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer ce retour ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())

        self.manager.supprimer_retour(identifiant)

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