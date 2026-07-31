from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QLabel,
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

    # Règle UPS : L x l x H en cm, divisé par 5000.
    DIVISEUR_UPS = 5000

    # 10 000 cm³, soit 10 litres : au-delà, UPS décroche.
    VOLUME_LIMITE_UPS = 10000

    def __init__(self):

        super().__init__("📮 Grille d'emballage")

        self.manager = EmballageManager()

        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Code",
            "Nom",
            "Dimensions (cm)",
            "Poids",
            "Coût HT",
            "Calage HT",
            "Volume",
            "Transporteur Europe",
        ])

        self.table.setColumnHidden(0, True)

        aide = QLabel(
            "La colonne « Transporteur Europe » indique, pour "
            "chaque emballage, lequel de tes deux transporteurs "
            "revient le moins cher sur une commande européenne. "
            "UPS facture au volume au-delà de 10 litres de "
            "carton ; Mondial Relay facture toujours au poids "
            "réel. En France, Mondial Relay reste le choix par "
            "défaut quel que soit l'emballage."
        )
        aide.setWordWrap(True)
        aide.setStyleSheet("color:#64748b; font-size:12px;")
        self.layout().addWidget(aide)

        self.btnAjouter.clicked.connect(self.ajouterEmballage)
        self.btnModifier.clicked.connect(self.modifierEmballage)
        self.btnSupprimer.clicked.connect(self.supprimerEmballage)

        self.btnImporter.setVisible(False)
        self.btnExporter.setVisible(False)

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

            # Volume du carton, et transporteur le moins cher
            # en Europe qui en découle.
            #
            # UPS facture au poids VOLUMÉTRIQUE : longueur x
            # largeur x hauteur / 5000. Au-delà de 10 litres de
            # carton, il passe dans la tranche supérieure et
            # devient plus cher que Mondial Relay, qui facture
            # au poids réel.
            #
            # Cette indication ne concerne QUE les commandes
            # européennes : en France, Mondial Relay reste le
            # choix par défaut.
            volume = (
                (emb["longueur_ext_cm"] or 0)
                * (emb["largeur_ext_cm"] or 0)
                * (emb["hauteur_ext_cm"] or 0)
            )

            if volume:

                valeurs.append(
                    f"{volume:.0f} cm³  ({volume/1000:.1f} L)"
                )

                if volume <= self.VOLUME_LIMITE_UPS:
                    valeurs.append(
                        f"UPS  — {volume/self.DIVISEUR_UPS:.2f} kg "
                        f"volumétriques"
                    )
                else:
                    valeurs.append(
                        f"Mondial Relay  — trop volumineux "
                        f"pour UPS"
                    )

            else:
                valeurs.append("—")
                valeurs.append("— dimensions manquantes")

            for colonne, valeur in enumerate(valeurs):

                item = QTableWidgetItem(valeur)

                if colonne == 8:

                    if valeur.startswith("UPS"):
                        item.setForeground(QColor("#15803d"))
                    elif valeur.startswith("Mondial"):
                        item.setForeground(QColor("#b35c10"))
                    else:
                        item.setForeground(QColor("#767676"))

                    police = QFont()
                    police.setBold(True)
                    item.setFont(police)

                self.table.setItem(ligne, colonne, item)

    def ajouterEmballage(self):

        dialog = EmballageDialog("Nouvel emballage")

        if dialog.exec() != EmballageDialog.DialogCode.Accepted:
            return

        valeurs = dialog.valeurs()

        if not valeurs["code"] or not valeurs["nom"]:

            QMessageBox.warning(
                self,
                "Champs manquants",
                "Le code et le nom sont obligatoires."
            )
            return

        try:

            self.manager.ajouter(**valeurs)

        except Exception as erreur:

            QMessageBox.warning(
                self,
                "Enregistrement impossible",
                f"Cet emballage n'a pas pu être créé :\n\n{erreur}"
            )
            return

        self.charger()

    def modifierEmballage(self):

        ligne = self.table.currentRow()

        if ligne < 0:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un emballage."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())

        emballage = self.manager.obtenir(identifiant)

        dialog = EmballageDialog(
            "Modifier l'emballage", emballage=emballage
        )

        if dialog.exec() != EmballageDialog.DialogCode.Accepted:
            return

        valeurs = dialog.valeurs()

        try:

            self.manager.modifier(identifiant, **valeurs)

        except Exception as erreur:

            QMessageBox.warning(
                self,
                "Enregistrement impossible",
                f"Cet emballage n'a pas pu être modifié :\n\n{erreur}"
            )
            return

        self.charger()

    def supprimerEmballage(self):

        ligne = self.table.currentRow()

        if ligne < 0:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez un emballage."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet emballage ?"
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