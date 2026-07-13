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
    QCheckBox,
    QLineEdit,
    QDialog,
    QFormLayout,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from modules.reference_manager import ReferenceManager


class ThemeDialog(QDialog):
    """
    Fenêtre de création/modification d'un thème de template.
    """

    def __init__(self, titre, nom="", description=""):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(420, 220)

        self.setStyleSheet("""
            QDialog{ background:#f4f7fb; font-family:"Segoe UI"; }
            QFrame#card{ background:white; border:1px solid #e1e8f0; border-radius:12px; }
            QLineEdit{
                background:#f7f9fc; border:1px solid #d7e0ec;
                border-radius:7px; padding:8px; font-size:10.5pt;
            }
            QPushButton{
                background:#144b8b; color:white; border:none;
                border-radius:8px; padding:10px 18px; min-width:110px;
            }
            QPushButton:hover{ background:#1d61b4; }
        """)

        principal = QVBoxLayout(self)
        carte = QFrame()
        carte.setObjectName("card")
        principal.addWidget(carte)
        layout = QVBoxLayout(carte)

        form = QFormLayout()

        self.nom = QLineEdit()
        self.nom.setText(nom)
        self.nom.setPlaceholderText("Ex : Vêtements, Figurines, Peluches...")
        form.addRow("Nom du thème", self.nom)

        self.description = QLineEdit()
        self.description.setText(description)
        self.description.setPlaceholderText("Facultatif")
        form.addRow("Description", self.description)

        layout.addLayout(form)

        boutons = QHBoxLayout()
        boutons.addStretch()
        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")
        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)
        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)


class ThemesTemplatePage(QWidget):
    """
    Gestion des thèmes de template (Vêtements, Figurines,
    Peluches...) — regroupent les modèles de fiche produit.

    Contrairement aux autres écrans de référence du logiciel
    (Marques, Licences...), un thème décoché reste visible
    ici, grisé, plutôt que de disparaître — un thème peut
    être référencé par des modèles existants, le désactiver
    par erreur ne doit pas le rendre introuvable.
    """

    def __init__(self):

        super().__init__()

        self.manager = ReferenceManager()
        self.table_nom = "themes_template"

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
        }
        QHeaderView::section{
            background:#0f2f5c; color:white; font-weight:600;
            border:none; padding:8px 6px;
        }
        QCheckBox::indicator{
            width:20px; height:20px;
            border:2px solid #144b8b; border-radius:5px;
            background:white;
        }
        QCheckBox::indicator:checked{
            background:#144b8b;
            image:none;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        entete = QHBoxLayout()
        titre = QLabel("🎨 Thèmes de template")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        info = QLabel(
            "Regroupent les modèles de fiche produit (ex : \"Vêtements\", "
            "\"Figurines\"). Un thème décoché \"Actif\" reste visible ici, "
            "grisé, plutôt que de disparaître — il ne sera juste plus "
            "proposé pour un nouveau modèle."
        )
        info.setStyleSheet("color:#5a6b7d; font-size:9.5pt;")
        info.setWordWrap(True)
        layout.addWidget(info)

        boutons = QHBoxLayout()

        self.btnAjouter = QPushButton("➕ Nouveau thème")
        self.btnAjouter.clicked.connect(self.ajouter)
        boutons.addWidget(self.btnAjouter)

        self.btnModifier = QPushButton("✏ Modifier")
        self.btnModifier.clicked.connect(self.modifier)
        boutons.addWidget(self.btnModifier)

        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnSupprimer.setObjectName("btnSupprimer")
        self.btnSupprimer.clicked.connect(self.supprimer)
        boutons.addWidget(self.btnSupprimer)

        boutons.addStretch()

        layout.addLayout(boutons)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Description", "Actif"
        ])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        themes = self.manager.tous_y_compris_inactifs(self.table_nom)

        for ligne, theme in enumerate(themes):

            self.table.insertRow(ligne)

            est_actif = bool(theme["actif"])

            item_id = QTableWidgetItem(str(theme["id"]))
            item_nom = QTableWidgetItem(theme["nom"] or "")
            item_description = QTableWidgetItem(theme["description"] or "")

            for item in (item_id, item_nom, item_description):

                if not est_actif:
                    item.setForeground(QColor("#a0a8b4"))

            self.table.setItem(ligne, 0, item_id)
            self.table.setItem(ligne, 1, item_nom)
            self.table.setItem(ligne, 2, item_description)

            case = QCheckBox()
            case.setChecked(est_actif)
            case.toggled.connect(
                lambda coche, tid=theme["id"]: self._basculerActif(
                    tid, coche
                )
            )

            conteneur = QWidget()
            layoutCase = QHBoxLayout(conteneur)
            layoutCase.addWidget(case)
            layoutCase.setAlignment(case, Qt.AlignmentFlag.AlignCenter)
            layoutCase.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(ligne, 3, conteneur)

    def _basculerActif(self, theme_id, coche):

        theme = self.manager.obtenir(self.table_nom, theme_id)

        self.manager.modifier(
            self.table_nom,
            theme_id,
            theme["nom"],
            theme["description"],
            coche,
        )

        self.charger()

    def ajouter(self):

        dialog = ThemeDialog("Nouveau thème")

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            self.table_nom, nom, dialog.description.text().strip(), True
        )

        self.charger()

    def modifier(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez un thème.")
            return

        identifiant = int(self.table.item(ligne, 0).text())
        theme = self.manager.obtenir(self.table_nom, identifiant)

        dialog = ThemeDialog(
            "Modifier le thème", theme["nom"], theme["description"] or ""
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            self.table_nom,
            identifiant,
            nom,
            dialog.description.text().strip(),
            bool(theme["actif"]),
        )

        self.charger()

    def supprimer(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez un thème.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Désactiver définitivement ce thème ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())
        self.manager.supprimer(self.table_nom, identifiant)

        self.charger()