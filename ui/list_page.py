from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QHeaderView,
    QFrame,
)


class ListPage(QWidget):
    """
    Base commune à tous les écrans de liste (Canaux, Grille
    de transport, Emballages, Fournisseurs, Commandes, SAV,
    Marques, Licences...) — un seul style à entretenir pour
    que tout le logiciel ait un rendu cohérent et pro.
    """

    def __init__(self, titre):

        super().__init__()

        self.setStyleSheet("""
        QWidget{
            background:#f4f7fb;
            font-family:'Segoe UI';
        }

        QLabel#titre{
            font-size:24px;
            font-weight:600;
            color:#0f2f5c;
        }

        QFrame#barreOutils{
            background:white;
            border:1px solid #e1e8f0;
            border-radius:10px;
        }

        QFrame#carteTable{
            background:white;
            border:1px solid #e1e8f0;
            border-radius:12px;
        }

        QLineEdit{
            background:#f7f9fc;
            border:1px solid #d7e0ec;
            border-radius:8px;
            padding:9px 12px;
            font-size:10.5pt;
            color:#1c2b3a;
        }

        QLineEdit:focus{
            border:1px solid #144b8b;
            background:white;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:9px 16px;
            min-width:100px;
            font-size:10pt;
            font-weight:500;
        }

        QPushButton:hover{
            background:#1d61b4;
        }

        QPushButton:pressed{
            background:#0d3a6e;
        }

        QPushButton#btnSupprimer{
            background:#c0392b;
        }

        QPushButton#btnSupprimer:hover{
            background:#d9483a;
        }

        QPushButton#btnSecondaire{
            background:#eef2f8;
            color:#144b8b;
            border:1px solid #d7e0ec;
        }

        QPushButton#btnSecondaire:hover{
            background:#e2eaf5;
        }

        QTableWidget{
            background:white;
            border:none;
            border-radius:12px;
            gridline-color:#eef1f6;
            selection-background-color:#dbe7f7;
            selection-color:#0f2f5c;
            alternate-background-color:#f8fafc;
            font-size:10pt;
        }

        QTableWidget::item{
            padding:9px 6px;
            border-bottom:1px solid #f0f3f8;
        }

        QTableWidget::item:hover{
            background:#eef4fb;
        }

        QTableWidget::item:selected{
            background:#dbe7f7;
            color:#0f2f5c;
        }

        QHeaderView::section{
            background:#0f2f5c;
            color:white;
            font-weight:600;
            font-size:9.5pt;
            border:none;
            border-right:1px solid #1a4a8a;
            padding:10px 6px;
        }

        QHeaderView::section:last{
            border-right:none;
        }

        QScrollBar:vertical{
            background:#f4f7fb;
            width:10px;
            margin:0;
        }

        QScrollBar::handle:vertical{
            background:#c7d3e3;
            border-radius:5px;
            min-height:30px;
        }

        QScrollBar::handle:vertical:hover{
            background:#a9bad2;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical{
            height:0;
        }
        """)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(24, 20, 24, 20)
        principal.setSpacing(14)

        ####################################################
        # Titre
        ####################################################

        entete = QHBoxLayout()

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")

        entete.addWidget(titreLabel)
        entete.addStretch()

        principal.addLayout(entete)

        ####################################################
        # Barre d'outils (carte séparée, plus lisible)
        ####################################################

        carteBarre = QFrame()
        carteBarre.setObjectName("barreOutils")

        barre = QHBoxLayout(carteBarre)
        barre.setContentsMargins(14, 10, 14, 10)
        barre.setSpacing(10)

        self.recherche = QLineEdit()
        self.recherche.setPlaceholderText("🔍  Rechercher...")

        self.btnAjouter = QPushButton("➕ Nouveau")
        self.btnModifier = QPushButton("✏ Modifier")
        self.btnModifier.setObjectName("btnSecondaire")
        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnSupprimer.setObjectName("btnSupprimer")
        self.btnImporter = QPushButton("📥 Import")
        self.btnImporter.setObjectName("btnSecondaire")
        self.btnExporter = QPushButton("📤 Export")
        self.btnExporter.setObjectName("btnSecondaire")

        barre.addWidget(self.recherche)
        barre.addStretch()

        barre.addWidget(self.btnAjouter)
        barre.addWidget(self.btnModifier)
        barre.addWidget(self.btnSupprimer)
        barre.addWidget(self.btnImporter)
        barre.addWidget(self.btnExporter)

        principal.addWidget(carteBarre)

        ####################################################
        # Tableau (dans sa propre carte, pour un vrai relief
        # visuel par rapport au fond de la page)
        ####################################################

        carteTable = QFrame()
        carteTable.setObjectName("carteTable")

        layoutTable = QVBoxLayout(carteTable)
        layoutTable.setContentsMargins(2, 2, 2, 2)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layoutTable.addWidget(self.table)

        principal.addWidget(carteTable)