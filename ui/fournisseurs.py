from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.fournisseur_dialog import FournisseurDialog
from modules.fournisseur_manager import FournisseurManager


class FournisseursPage(ListPage):

    def __init__(self):

        super().__init__("🚚 Gestion des fournisseurs")

        self.manager = FournisseurManager()

        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nom",
            "Contact",
            "Téléphone",
            "Email",
            "Site web",
            "Conditions règlement",
            "Délai livraison",
            "Actif"
        ])

        self.table.setColumnHidden(0, True)

        self.btnAjouter.clicked.connect(self.ajouterFournisseur)
        self.btnModifier.clicked.connect(self.modifierFournisseur)
        self.btnSupprimer.clicked.connect(self.supprimerFournisseur)

        self.table.doubleClicked.connect(self.modifierFournisseur)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        fournisseurs = self.manager.tous()

        for ligne, fournisseur in enumerate(fournisseurs):

            self.table.insertRow(ligne)

            valeurs = [
                str(fournisseur["id"]),
                fournisseur["nom"] or "",
                fournisseur["contact"] or "",
                fournisseur["telephone"] or "",
                fournisseur["email"] or "",
                fournisseur["site"] or "",
                fournisseur["conditions_reglement"] or "",
                fournisseur["delai_livraison"] or "",
                "Oui" if fournisseur["actif"] else "Non",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterFournisseur(self):

        dialog = FournisseurDialog("Nouveau fournisseur")

        if dialog.exec() != FournisseurDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            nom,
            dialog.contact.text(),
            dialog.telephone.text(),
            dialog.email.text(),
            dialog.site.text(),
            dialog.seuilMinimumCommande.value(),
            dialog.francoPort.value(),
            dialog.fraisPort.value(),
            dialog.conditionsReglement.text(),
            dialog.delaiLivraison.text(),
            dialog.actif.isChecked()
        )

        self.charger()

    def modifierFournisseur(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un fournisseur."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        fournisseur = self.manager.obtenir(identifiant)

        dialog = FournisseurDialog(
            "Modifier le fournisseur",
            fournisseur["nom"],
            fournisseur["contact"] or "",
            fournisseur["telephone"] or "",
            fournisseur["email"] or "",
            fournisseur["site"] or "",
            fournisseur["seuil_minimum_commande"],
            fournisseur["franco_port"],
            fournisseur["frais_port"],
            fournisseur["conditions_reglement"] or "",
            fournisseur["delai_livraison"] or "",
            bool(fournisseur["actif"])
        )

        if dialog.exec() != FournisseurDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant,
            nom,
            dialog.contact.text(),
            dialog.telephone.text(),
            dialog.email.text(),
            dialog.site.text(),
            dialog.seuilMinimumCommande.value(),
            dialog.francoPort.value(),
            dialog.fraisPort.value(),
            dialog.conditionsReglement.text(),
            dialog.delaiLivraison.text(),
            dialog.actif.isChecked()
        )

        self.charger()

    def supprimerFournisseur(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un fournisseur."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver ce fournisseur ?"
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

            visible = False

            for colonne in range(1, self.table.columnCount()):

                item = self.table.item(ligne, colonne)

                if item and texte in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(
                ligne,
                not visible
            )