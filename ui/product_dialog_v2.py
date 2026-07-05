from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QPushButton,
)


class ProductDialogV2(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("***** PRODUCT DIALOG V2 *****")
        self.resize(1100, 750)

        self.setStyleSheet("""
        QDialog{
            background:#edf3fa;
            font-family:"Segoe UI";
        }

        QTabWidget::pane{
            background:white;
            border:1px solid #d7e3ef;
            border-radius:10px;
        }

        QTabBar::tab{
            background:#dfeaf6;
            padding:12px 24px;
            margin-right:2px;
            border-top-left-radius:8px;
            border-top-right-radius:8px;
        }

        QTabBar::tab:selected{
            background:white;
            font-weight:bold;
            color:#144b8b;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px 20px;
            min-width:140px;
        }

        QPushButton:hover{
            background:#1d61b4;
        }
        """)

        layout = QVBoxLayout(self)

        ####################################################
        # Onglets
        ####################################################

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        ####################################################
        # Général
        ####################################################

        self.pageGeneral = QWidget()

        self.tabs.addTab(
            self.pageGeneral,
            "📦 Général"
        )

        ####################################################
        # Caractéristiques
        ####################################################

        self.pageCaracteristiques = QWidget()

        self.tabs.addTab(
            self.pageCaracteristiques,
            "📏 Caractéristiques"
        )

        ####################################################
        # Tarification
        ####################################################

        self.pageTarification = QWidget()

        self.tabs.addTab(
            self.pageTarification,
            "💰 Tarification"
        )

        ####################################################
        # SEO
        ####################################################

        self.pageSEO = QWidget()

        self.tabs.addTab(
            self.pageSEO,
            "🌐 SEO"
        )

        ####################################################
        # Images
        ####################################################

        self.pageImages = QWidget()

        self.tabs.addTab(
            self.pageImages,
            "🖼 Images"
        )

        ####################################################
        # Publication
        ####################################################

        self.pagePublication = QWidget()

        self.tabs.addTab(
            self.pagePublication,
            "🚀 Publication"
        )

        ####################################################
        # Historique
        ####################################################

        self.pageHistorique = QWidget()

        self.tabs.addTab(
            self.pageHistorique,
            "📜 Historique"
        )

        ####################################################
        # Boutons
        ####################################################

        boutons = QHBoxLayout()

        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)