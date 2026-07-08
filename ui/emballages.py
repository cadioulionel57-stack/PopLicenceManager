from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.emballage_dialog import EmballageDialog
from modules.emballage_manager import EmballageManager


class EmballagesPage(ListPage):
    """
    Écran de gestion de la grille d'emballage (pochettes,
    cartons...), utilisée automatiquement par les familles
    de produit pour calculer leur coût d'emballage.
    """

    def __init__(self):

        super().__init__("📮 Grille d'emballage")

        self.manager = EmballageManager()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Code",
            "Nom",
            "Dimensions (cm)",
            "Poids",
            "Coût HT",
            "Calage HT",
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

        for ligne, emb in enumerate(emballages):

            self.table.insertRow(ligne)

            valeurs = [
                str(emb["id"]),
                emb["code"] or "",
                emb["nom"] or "",
                f"{emb['longueur_ext_cm']:.0f} x "
                f"{emb['largeur_ext_cm']:.0f} x "
                f"{emb['hauteur_ext_cm']:.0f}",
                f"{emb['poids_g']:.0f} g",
                f"{emb['cout_ht']:.2f} €",
                f"{emb['calage_ht']:.2f} €",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterEmballage(self):

        dialog = EmballageDialog("Nouvel emballage")

        if dialog.exec() != EmballageDialog.DialogCode.Accepted:
            return

        code = dialog.code.text().strip()

        if code == "":
            return

        self.manager.ajouter(
            code=code,
            nom=dialog.nom.text().strip(),
            longueur_ext_cm=dialog.longueurExt.value(),
            largeur_ext_cm=dialog.largeurExt.value(),
            hauteur_ext_cm=dialog.hauteurExt.value(),
            poids_g=dialog.poids.value(),
            cout_ht=dialog.coutHt.value(),
            calage_ht=dialog.calageHt.value(),
        )

        self.charger()

    def modifierEmballage(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un emballage."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        emb = self.manager.obtenir(identifiant)

        dialog = EmballageDialog(
            "Modifier l'emballage",
            code=emb["code"],
            nom=emb["nom"],
            longueur_ext_cm=emb["longueur_ext_cm"],
            largeur_ext_cm=emb["largeur_ext_cm"],
            hauteur_ext_cm=emb["hauteur_ext_cm"],
            poids_g=emb["poids_g"],
            cout_ht=emb["cout_ht"],
            calage_ht=emb["calage_ht"],
        )

        if dialog.exec() != EmballageDialog.DialogCode.Accepted:
            return

        self.manager.modifier(
            identifiant=identifiant,
            code=dialog.code.text().strip(),
            nom=dialog.nom.text().strip(),
            longueur_ext_cm=dialog.longueurExt.value(),
            largeur_ext_cm=dialog.largeurExt.value(),
            hauteur_ext_cm=dialog.hauteurExt.value(),
            poids_g=dialog.poids.value(),
            cout_ht=dialog.coutHt.value(),
            calage_ht=dialog.calageHt.value(),
        )

        self.charger()

    def supprimerEmballage(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un emballage."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cet emballage ?"
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