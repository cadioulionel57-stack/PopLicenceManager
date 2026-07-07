from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.canal_dialog import CanalDialog
from modules.canal_manager import CanalManager


class CanauxPage(ListPage):
    """
    Écran de gestion des canaux de vente : WiziShop,
    Amazon FBM, Cdiscount, eBay, Leclerc, Rakuten,
    Fnac, ou tout autre canal ajouté par l'utilisateur.

    Rien n'est figé dans le code : ajouter, modifier
    ou désactiver un canal se fait entièrement depuis
    cet écran.
    """

    def __init__(self):

        super().__init__("🌐 Canaux de vente")

        self.manager = CanalManager()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nom",
            "Type",
            "Commission",
            "Frais fixe HT",
            "Port inclus",
            "Actif",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterCanal)
        self.btnModifier.clicked.connect(self.modifierCanal)
        self.btnSupprimer.clicked.connect(self.supprimerCanal)

        self.table.doubleClicked.connect(self.modifierCanal)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        canaux = self.manager.tous()

        libelles_type = {
            "site": "Site",
            "marketplace": "Marketplace",
        }

        for ligne, canal in enumerate(canaux):

            self.table.insertRow(ligne)

            valeurs = [
                str(canal["id"]),
                canal["nom"] or "",
                libelles_type.get(canal["type"], canal["type"] or ""),
                f"{canal['commission_pourcentage'] or 0:.2f} %",
                f"{canal['frais_fixe_ht'] or 0:.2f} €",
                "Oui" if canal["port_inclus"] else "Non",
                "Oui" if canal["actif"] else "Non",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterCanal(self):

        dialog = CanalDialog("Nouveau canal de vente")

        if dialog.exec() != CanalDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            nom=nom,
            type_canal=dialog.type_canal(),
            commission_pourcentage=dialog.commission.value(),
            frais_fixe_ht=dialog.fraisFixe.value(),
            port_inclus=dialog.portInclus.isChecked(),
            ordre=dialog.valeur_ordre(),
        )

        self.charger()

    def modifierCanal(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un canal de vente."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        canal = self.manager.obtenir(identifiant)

        dialog = CanalDialog(
            "Modifier le canal de vente",
            nom=canal["nom"],
            type_canal=canal["type"] or "marketplace",
            commission_pourcentage=canal["commission_pourcentage"] or 0,
            frais_fixe_ht=canal["frais_fixe_ht"] or 0,
            port_inclus=bool(canal["port_inclus"]),
            ordre=canal["ordre"] or 0,
        )

        if dialog.exec() != CanalDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant=identifiant,
            nom=nom,
            type_canal=dialog.type_canal(),
            commission_pourcentage=dialog.commission.value(),
            frais_fixe_ht=dialog.fraisFixe.value(),
            port_inclus=dialog.portInclus.isChecked(),
            ordre=dialog.valeur_ordre(),
        )

        self.charger()

    def supprimerCanal(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un canal de vente."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver ce canal de vente ?"
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