from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
)

from ui.list_page import ListPage
from ui.grille_fba_dialog import GrilleFbaDialog
from modules.grille_fba_manager import GrilleFbaManager


class GrilleFbaPage(ListPage):
    """
    Écran de gestion de la grille tarifaire FBA (Expédié
    par Amazon) : formats de colis, dimensions, et tarifs
    par tranche de poids. Entièrement modifiable, pour
    suivre les évolutions tarifaires d'Amazon.
    """

    def __init__(self):

        super().__init__("📦 Grille FBA (Expédié par Amazon)")

        self.manager = GrilleFbaManager()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Format",
            "Catégorie spéciale",
            "Dimensions max (cm)",
            "Poids inclus",
            "Prix de base",
            "Supplément",
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
                ligne["format_colis"] or "",
                ligne["categorie_speciale"] or "Standard (toutes catégories)",
                f"{ligne['longueur_max_cm']:.0f} x "
                f"{ligne['largeur_max_cm']:.0f} x "
                f"{ligne['hauteur_max_cm']:.0f}",
                f"{ligne['poids_seuil_g']:.0f} g",
                f"{ligne['prix_base_ht']:.2f} €",
                f"+{ligne['prix_supplement_ht']:.2f} € / "
                f"{ligne['supplement_pas_g']:.0f} g",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne_index,
                    colonne,
                    QTableWidgetItem(valeur)
                )

    def ajouterLigne(self):

        dialog = GrilleFbaDialog("Nouvelle ligne de grille FBA")

        if dialog.exec() != GrilleFbaDialog.DialogCode.Accepted:
            return

        format_colis = dialog.formatColis.text().strip()

        if format_colis == "":
            return

        self.manager.ajouter(
            format_colis=format_colis,
            categorie_speciale=dialog.categorie_speciale_texte(),
            longueur_max_cm=dialog.longueurMax.value(),
            largeur_max_cm=dialog.largeurMax.value(),
            hauteur_max_cm=dialog.hauteurMax.value(),
            poids_seuil_g=dialog.poidsSeuil.value(),
            prix_base_ht=dialog.prixBase.value(),
            prix_supplement_ht=dialog.prixSupplement.value(),
            supplement_pas_g=dialog.supplementPas.value(),
        )

        self.charger()

    def modifierLigne(self):

        ligne_selection = self.table.currentRow()

        if ligne_selection == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une ligne de grille FBA."
            )
            return

        identifiant = int(
            self.table.item(ligne_selection, 0).text()
        )

        ligne = self.manager.obtenir(identifiant)

        dialog = GrilleFbaDialog(
            "Modifier la ligne de grille FBA",
            format_colis=ligne["format_colis"],
            categorie_speciale=ligne["categorie_speciale"],
            longueur_max_cm=ligne["longueur_max_cm"],
            largeur_max_cm=ligne["largeur_max_cm"],
            hauteur_max_cm=ligne["hauteur_max_cm"],
            poids_seuil_g=ligne["poids_seuil_g"],
            prix_base_ht=ligne["prix_base_ht"],
            prix_supplement_ht=ligne["prix_supplement_ht"],
            supplement_pas_g=ligne["supplement_pas_g"],
        )

        if dialog.exec() != GrilleFbaDialog.DialogCode.Accepted:
            return

        self.manager.modifier(
            identifiant=identifiant,
            format_colis=dialog.formatColis.text().strip(),
            categorie_speciale=dialog.categorie_speciale_texte(),
            longueur_max_cm=dialog.longueurMax.value(),
            largeur_max_cm=dialog.largeurMax.value(),
            hauteur_max_cm=dialog.hauteurMax.value(),
            poids_seuil_g=dialog.poidsSeuil.value(),
            prix_base_ht=dialog.prixBase.value(),
            prix_supplement_ht=dialog.prixSupplement.value(),
            supplement_pas_g=dialog.supplementPas.value(),
        )

        self.charger()

    def supprimerLigne(self):

        ligne_selection = self.table.currentRow()

        if ligne_selection == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une ligne de grille FBA."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment désactiver cette ligne ?"
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