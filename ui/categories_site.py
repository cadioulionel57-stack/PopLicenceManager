from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from modules.categorie_site_manager import CategorieSiteManager
from ui.categorie_site_dialog import CategorieSiteDialog


class CategoriesSitePage(QWidget):
    """
    Gestion des catégories du site (WiziShop) : catégories
    principales et leurs sous-catégories, chacune avec son
    ID WiziShop — nécessaire pour l'export du catalogue.
    """

    def __init__(self):

        super().__init__()

        self.manager = CategorieSiteManager()

        self.setStyleSheet("""
        QWidget{ background:#f4f7fb; font-family:'Segoe UI'; }
        QLabel#titre{ font-size:24px; font-weight:600; color:#0f2f5c; }
        QPushButton{
            background:#144b8b; color:white; border:none;
            border-radius:8px; padding:9px 16px; font-weight:500;
        }
        QPushButton:hover{ background:#1d61b4; }
        QPushButton#btnSupprimer{ background:#c0392b; }
        QTableWidget{
            background:white; gridline-color:#eef1f6;
            alternate-background-color:#f8fafc;
        }
        QHeaderView::section{
            background:#0f2f5c; color:white; font-weight:600;
            border:none; padding:8px 6px;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        entete = QHBoxLayout()
        titre = QLabel("⚙️ Catégories Site (WiziShop)")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        info = QLabel(
            "Crée ici tes catégories exactement comme elles existent "
            "sur WiziShop (nom + ID WiziShop), avec leurs "
            "sous-catégories — nécessaire pour l'export du catalogue."
        )
        info.setStyleSheet("color:#5a6b7d; font-size:9.5pt;")
        info.setWordWrap(True)
        layout.addWidget(info)

        entêteBoutons = QHBoxLayout()

        self.btnAjouter = QPushButton("➕ Nouvelle catégorie")
        self.btnAjouter.clicked.connect(self.ajouter)
        entêteBoutons.addWidget(self.btnAjouter)

        self.btnModifier = QPushButton("✏ Modifier")
        self.btnModifier.clicked.connect(self.modifier)
        entêteBoutons.addWidget(self.btnModifier)

        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnSupprimer.setObjectName("btnSupprimer")
        self.btnSupprimer.clicked.connect(self.supprimer)
        entêteBoutons.addWidget(self.btnSupprimer)

        entêteBoutons.addStretch()

        layout.addLayout(entêteBoutons)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "ID WiziShop", "Catégorie principale", "Type"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        principales = self.manager.categories_principales()

        ligne = 0

        for principale in principales:

            self.table.insertRow(ligne)

            valeurs = [
                str(principale["id"]),
                principale["nom"] or "",
                principale["id_wizishop"] or "",
                "—",
                "Catégorie principale",
            ]

            for colonne, valeur in enumerate(valeurs):
                self.table.setItem(
                    ligne, colonne, QTableWidgetItem(valeur)
                )

            ligne += 1

            for sous in self.manager.sous_categories(principale["id"]):

                self.table.insertRow(ligne)

                valeurs = [
                    str(sous["id"]),
                    f"    ↳ {sous['nom'] or ''}",
                    sous["id_wizishop"] or "",
                    principale["nom"] or "",
                    "Sous-catégorie",
                ]

                for colonne, valeur in enumerate(valeurs):
                    self.table.setItem(
                        ligne, colonne, QTableWidgetItem(valeur)
                    )

                ligne += 1

    def ajouter(self):

        dialog = CategorieSiteDialog(
            "Nouvelle catégorie",
            self.manager.categories_principales(),
        )

        if dialog.exec() != CategorieSiteDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            nom,
            dialog.idWizishop.text().strip(),
            dialog.categorie_parente_choisie(),
        )

        self.charger()

    def modifier(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(
                self, "Information", "Sélectionnez une catégorie."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())
        categorie = self.manager.obtenir(identifiant)

        principales = [
            p for p in self.manager.categories_principales()
            if p["id"] != identifiant
        ]

        dialog = CategorieSiteDialog(
            "Modifier la catégorie",
            principales,
            categorie["nom"],
            categorie["id_wizishop"],
            categorie["categorie_parente_id"],
        )

        if dialog.exec() != CategorieSiteDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant,
            nom,
            dialog.idWizishop.text().strip(),
            dialog.categorie_parente_choisie(),
        )

        self.charger()

    def supprimer(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(
                self, "Information", "Sélectionnez une catégorie."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())

        reponse = QMessageBox.question(
            self, "Confirmation",
            "Supprimer cette catégorie ? Si elle a des "
            "sous-catégories, elles resteront mais perdront leur "
            "catégorie principale."
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        self.manager.supprimer(identifiant)

        self.charger()