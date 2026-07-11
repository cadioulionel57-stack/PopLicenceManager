from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.achat_fournisseur_dialog import AchatFournisseurDialog
from modules.achat_fournisseur_manager import AchatFournisseurManager


class AchatsStocksPage(ListPage):
    """
    Commandes passées à tes fournisseurs pour réapprovisionner
    ton stock — distinct des commandes clients.
    """

    def __init__(self):

        super().__init__("🧾 Achats Stocks")

        self.manager = AchatFournisseurManager()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Numéro",
            "Fournisseur",
            "Date commande",
            "Date réception",
            "Statut",
            "Montant HT",
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterAchat)
        self.btnModifier.clicked.connect(self.modifierAchat)
        self.btnSupprimer.clicked.connect(self.supprimerAchat)

        self.table.doubleClicked.connect(self.modifierAchat)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        achats = self.manager.tous()

        for ligne, achat in enumerate(achats):

            self.table.insertRow(ligne)

            valeurs = [
                str(achat["id"]),
                achat["numero"] or "",
                achat["nom_fournisseur"] or "",
                achat["date_achat"] or "",
                achat["date_reception"] or "",
                achat["statut"] or "",
                f"{achat['montant_ht'] or 0:.2f} €",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne, colonne, QTableWidgetItem(valeur)
                )

    def ajouterAchat(self):

        dialog = AchatFournisseurDialog("Nouvelle commande fournisseur")

        if dialog.exec() != AchatFournisseurDialog.DialogCode.Accepted:
            return

        self._enregistrerDepuisDialogue(dialog)

    def modifierAchat(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self, "Information", "Sélectionnez une commande."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())

        achat = self.manager.obtenir(identifiant)
        lignes = self.manager.lignes(identifiant)

        dialog = AchatFournisseurDialog(
            "Modifier la commande fournisseur",
            achat=achat, lignes=lignes,
        )

        if dialog.exec() != AchatFournisseurDialog.DialogCode.Accepted:
            return

        self._enregistrerDepuisDialogue(dialog, identifiant)

    def _enregistrerDepuisDialogue(self, dialog, identifiant=None):

        lignes_saisies = dialog.lignes_saisies()

        montant_ht = sum(
            (l["prix_unitaire_ht"] or 0) * (l["quantite"] or 1)
            for l in lignes_saisies
        )

        if identifiant is None:

            identifiant = self.manager.ajouter(
                numero=dialog.numero.text().strip(),
                fournisseur_id=dialog.fournisseur.id(),
                date_achat=dialog.dateAchat.date().toString("yyyy-MM-dd"),
                date_reception=dialog.dateReception.date().toString("yyyy-MM-dd"),
                statut=dialog.statut.currentText(),
                montant_ht=montant_ht,
                frais_port_ht=dialog.fraisPort.value(),
                commentaire=dialog.commentaire.toPlainText(),
            )

        else:

            self.manager.modifier(
                identifiant=identifiant,
                numero=dialog.numero.text().strip(),
                fournisseur_id=dialog.fournisseur.id(),
                date_achat=dialog.dateAchat.date().toString("yyyy-MM-dd"),
                date_reception=dialog.dateReception.date().toString("yyyy-MM-dd"),
                statut=dialog.statut.currentText(),
                montant_ht=montant_ht,
                frais_port_ht=dialog.fraisPort.value(),
                commentaire=dialog.commentaire.toPlainText(),
            )

        self.manager.definir_lignes(identifiant, lignes_saisies)

        self.charger()

    def supprimerAchat(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self, "Information", "Sélectionnez une commande."
            )
            return

        reponse = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment supprimer cette commande ?"
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