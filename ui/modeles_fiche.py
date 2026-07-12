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
)
from PySide6.QtCore import Qt

from modules.modele_fiche_manager import ModeleFicheManager
from modules.reference_manager import ReferenceManager
from ui.modele_fiche_dialog import ModeleFicheDialog


LIBELLES_TYPE = {
    "stock": "Produit en stock",
    "dropshipping": "Direct Fournisseur",
    "les_deux": "Les deux (événementiel)",
}


class ModelesFichePage(QWidget):
    """
    Gestion des modèles de fiche produit (chartes HTML) par
    thème + type de produit — plusieurs modèles possibles
    par combinaison (Normal, Noël, Soldes...), un seul actif
    à la fois (celui utilisé en mode "Automatique").
    """

    def __init__(self):

        super().__init__()

        self.manager = ModeleFicheManager()
        self.managerThemes = ReferenceManager()

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
        titre = QLabel("📄 Modèles de fiche produit")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        info = QLabel(
            "Un seul modèle \"Automatique\" actif à la fois par thème "
            "+ type de produit — coche \"Actif\" sur celui à utiliser "
            "(ex : passe tout le thème \"Vêtements\" en mode Noël d'un "
            "coup, puis reviens au modèle normal plus tard, rien n'est "
            "perdu). Sur chaque fiche produit, tu peux aussi forcer un "
            "modèle précis, indépendamment de ce réglage global."
        )
        info.setStyleSheet("color:#5a6b7d; font-size:9.5pt;")
        info.setWordWrap(True)
        layout.addWidget(info)

        entêteBoutons = QHBoxLayout()

        self.btnAjouter = QPushButton("➕ Nouveau modèle")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Thème", "Type", "Types d'articles", "Actif"
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

        for ligne, modele in enumerate(self.manager.tous()):

            self.table.insertRow(ligne)

            self.table.setItem(
                ligne, 0, QTableWidgetItem(str(modele["id"]))
            )
            self.table.setItem(
                ligne, 1, QTableWidgetItem(modele["nom"] or "")
            )
            self.table.setItem(
                ligne, 2, QTableWidgetItem(modele["nom_theme"] or "")
            )
            self.table.setItem(
                ligne, 3,
                QTableWidgetItem(
                    LIBELLES_TYPE.get(
                        modele["type_produit"], modele["type_produit"]
                    )
                )
            )
            self.table.setItem(
                ligne, 4,
                QTableWidgetItem(modele["types_articles_concernes"] or "")
            )

            case = QCheckBox()
            case.setChecked(bool(modele["actif"]))
            case.toggled.connect(
                lambda coche, mid=modele["id"]: self._basculerActif(
                    mid, coche
                )
            )

            conteneur = QWidget()
            layoutCase = QHBoxLayout(conteneur)
            layoutCase.addWidget(case)
            layoutCase.setAlignment(case, Qt.AlignmentFlag.AlignCenter)
            layoutCase.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(ligne, 5, conteneur)

    def _basculerActif(self, modele_id, coche):

        if not coche:
            # On ne permet pas de décocher directement — il
            # faut activer un AUTRE modèle du même thème+type
            # pour que celui-ci se désactive automatiquement
            # (sinon on pourrait finir sans aucun modèle
            # "Automatique" du tout).
            self.charger()
            return

        self.manager.basculer_actif(modele_id)
        self.charger()

    def ajouter(self):

        themes = self.managerThemes.tous("themes_template")

        if not themes:
            QMessageBox.information(
                self, "Information",
                "Crée d'abord au moins un thème dans l'écran "
                "\"Thèmes de template\"."
            )
            return

        dialog = ModeleFicheDialog("Nouveau modèle", themes)

        if dialog.exec() != ModeleFicheDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            nom,
            dialog.themeTemplate.currentData(),
            dialog.typeProduit.currentData(),
            dialog.htmlTemplate.toPlainText(),
            dialog.typesArticles.text().strip(),
        )

        self.charger()

    def modifier(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez un modèle.")
            return

        identifiant = int(self.table.item(ligne, 0).text())
        modele = self.manager.obtenir(identifiant)

        themes = self.managerThemes.tous("themes_template")

        dialog = ModeleFicheDialog(
            "Modifier le modèle",
            themes,
            modele["nom"],
            modele["theme_id"],
            modele["type_produit"],
            modele["html_template"],
            modele["types_articles_concernes"] or "",
        )

        if dialog.exec() != ModeleFicheDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant,
            nom,
            dialog.themeTemplate.currentData(),
            dialog.typeProduit.currentData(),
            dialog.htmlTemplate.toPlainText(),
            dialog.typesArticles.text().strip(),
        )

        self.charger()

    def supprimer(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez un modèle.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Supprimer définitivement ce modèle ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())
        self.manager.supprimer(identifiant)

        self.charger()