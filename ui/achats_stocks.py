from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.achat_fournisseur_dialog import AchatFournisseurDialog
from ui.reception_scan_dialog import ReceptionScanDialog
from modules.achat_fournisseur_manager import AchatFournisseurManager
from modules.reception_scan_manager import ReceptionScanManager
from modules.stock_manager import StockManager


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

        self.btnImporter.setText("📥 Contrôler la réception")
        self.btnImporter.clicked.connect(self.controlerReception)

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
                self._dateFr(achat["date_achat"]),
                self._dateFr(achat["date_reception"]),
                achat["statut"] or "",
                f"{achat['montant_ht'] or 0:.2f} €",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne, colonne, QTableWidgetItem(valeur)
                )

    def _dateFr(self, valeur):
        """
        Les dates sont stockées en AAAA-MM-JJ dans la base.
        On les affiche en JJ/MM/AAAA, comme les champs de
        saisie du logiciel.
        """

        if not valeur:
            return ""

        morceaux = str(valeur)[:10].split("-")

        if len(morceaux) != 3:
            return str(valeur)

        return f"{morceaux[2]}/{morceaux[1]}/{morceaux[0]}"

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

    ########################################################
    # Réception au collecteur
    ########################################################

    def _dejaReceptionne(self, identifiant):
        """
        Vrai dès qu'une livraison a été enregistrée au scan.
        Les lignes ne doivent alors plus être remplacées :
        elles portent les quantités déjà reçues.
        """

        if identifiant is None:
            return False

        lignes = ReceptionScanManager().lignes_commande(identifiant)

        return any((l["quantite_recue"] or 0) > 0 for l in lignes)

    def controlerReception(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self, "Information", "Sélectionnez une commande."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())
        numero = self.table.item(ligne, 1).text()

        dialog = ReceptionScanDialog(identifiant, numero, self)

        if dialog.exec() == ReceptionScanDialog.DialogCode.Accepted:
            self.charger()

    ########################################################
    # Enregistrement
    ########################################################

    def _enregistrerDepuisDialogue(self, dialog, identifiant=None):

        # Une commande déjà réceptionnée au scan ne voit plus
        # ses lignes remplacées : elles portent les quantités
        # reçues, et les recréer les remettrait à zéro.
        verrouille = self._dejaReceptionne(identifiant)

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

        if verrouille:

            QMessageBox.information(
                self,
                "Commande déjà réceptionnée",
                "L'en-tête a été enregistré, mais les lignes "
                "n'ont pas été modifiées : cette commande a "
                "déjà fait l'objet d'une réception au scan.\n\n"
                "Pour corriger une ligne, passe par un "
                "mouvement de stock manuel."
            )

            self.charger()
            return

        self.manager.definir_lignes(identifiant, lignes_saisies)

        # STOCK : la marchandise n'entre qu'au statut
        # "Recu". Tout autre statut annule l'entree,
        # ce qui permet de revenir en arriere.
        stock = StockManager()
        stock.annuler_entree_achat(identifiant)

        if dialog.statut.currentText() == "Reçu":
            stock.entrer_reception_achat(identifiant)

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

        # STOCK : on retire l'entree avant de supprimer.
        StockManager().annuler_entree_achat(identifiant)

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