from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QHeaderView,
)


class ListPage(QWidget):

    def __init__(self, titre):

        super().__init__()

        self.setStyleSheet("""
        QWidget{
            background:#edf3fa;
            font-family:'Segoe UI';
        }

        QLabel#titre{
            font-size:26px;
            font-weight:bold;
            color:#144b8b;
        }

        QLineEdit{
            background:white;
            border:1px solid #cfd8e3;
            border-radius:8px;
            padding:8px;
            font-size:11pt;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px 18px;
            min-width:110px;
        }

        QPushButton:hover{
            background:#1d61b4;
        }

        QTableWidget{
            background:white;
            border:none;
            border-radius:10px;
            gridline-color:#e8edf5;
        }

        QHeaderView::section{
            background:#144b8b;
            color:white;
            font-weight:bold;
            border:none;
            padding:8px;
        }
        """)

        principal = QVBoxLayout(self)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")

        principal.addWidget(titreLabel)

        barre = QHBoxLayout()

        self.recherche = QLineEdit()
        self.recherche.setPlaceholderText("Rechercher...")

        self.btnAjouter = QPushButton("➕ Nouveau")
        self.btnModifier = QPushButton("✏ Modifier")
        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnImporter = QPushButton("📥 Import")
        self.btnExporter = QPushButton("📤 Export")

        barre.addWidget(self.recherche)
        barre.addStretch()

        barre.addWidget(self.btnAjouter)
        barre.addWidget(self.btnModifier)
        barre.addWidget(self.btnSupprimer)
        barre.addWidget(self.btnImporter)
        barre.addWidget(self.btnExporter)

        principal.addLayout(barre)

        self.table = QTableWidget()

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        principal.addWidget(self.table)