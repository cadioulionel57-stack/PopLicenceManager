from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ui.products import ProductsPage
from ui.licences import LicencesPage
from ui.marques import MarquesPage
from ui.canaux import CanauxPage
from ui.categories import CategoriesPage

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pop Licence Manager")
        self.resize(1600, 900)

        self.setStyleSheet("""
        QMainWindow{
            background:#edf3fa;
        }

        QWidget{
            font-family:Segoe UI;
            font-size:11pt;
        }

        QLabel{
            color:#2d3436;
        }

        QPushButton{
            border:none;
            border-radius:10px;
            background:transparent;
            color:white;
            padding:12px;
            font-size:12pt;
            text-align:left;
        }

        QPushButton:hover{
            background:rgba(255,255,255,0.12);
        }

        QPushButton:pressed{
            background:rgba(255,255,255,0.22);
        }

        QFrame#menu{
            background:#144b8b;
        }

        QFrame#card{
            background:white;
            border-radius:15px;
        }

        QFrame#content{
            background:#edf3fa;
        }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        principal = QHBoxLayout(central)
        principal.setContentsMargins(0,0,0,0)
        principal.setSpacing(0)

        #################################################
        # MENU
        #################################################

        menu = QFrame()
        menu.setObjectName("menu")
        menu.setFixedWidth(260)

        principal.addWidget(menu)

        menuLayout = QVBoxLayout(menu)
        menuLayout.setContentsMargins(20,20,20,20)

        logo = QLabel()

        pix = QPixmap("resources/images/logo.png")

        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(170))

        logo.setAlignment(Qt.AlignCenter)
        menuLayout.addWidget(logo)

        titre = QLabel("POP LICENCE\nMANAGER")
        titre.setAlignment(Qt.AlignCenter)

        titre.setStyleSheet("""
            color:white;
            font-size:20pt;
            font-weight:bold;
            padding-bottom:20px;
        """)

        menuLayout.addWidget(titre)

        boutons = [
            "🏠  Tableau de bord",
            "📦  Produits",
            "🏷️  Licences",
            "™️  Marques",
            "📂  Catégories",
            "🚚  Fournisseurs",
            "🛒  Commandes",
            "📦  Stock",
            "💰  Tarification",
            "📈  Ventes",
            "📊  Statistiques",
            "🌐  Canaux de vente",
            "⚙️  Paramètres",
        ]

        self.boutons = {}

        for texte in boutons:

            bouton = QPushButton(texte)
            bouton.setMinimumHeight(48)

            self.boutons[texte] = bouton

            menuLayout.addWidget(bouton)

        menuLayout.addStretch()

        #################################################
        # CONTENU
        #################################################

        self.pages = QStackedWidget()

        principal.addWidget(self.pages)
                #################################################
        # TABLEAU DE BORD
        #################################################

        dashboard = QWidget()

        dashboardLayout = QVBoxLayout(dashboard)
        dashboardLayout.setContentsMargins(20,20,20,20)
        dashboardLayout.setSpacing(20)

        header = QFrame()
        header.setObjectName("card")
        header.setFixedHeight(80)

        headerLayout = QHBoxLayout(header)

        titre = QLabel("Tableau de bord")

        titre.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
            color:#144b8b;
        """)

        headerLayout.addWidget(titre)
        headerLayout.addStretch()

        utilisateur = QLabel("👤 Administrateur")

        utilisateur.setStyleSheet("""
            font-size:14px;
            font-weight:bold;
        """)

        headerLayout.addWidget(utilisateur)

        dashboardLayout.addWidget(header)

        kpiLayout = QHBoxLayout()

        def carte(titre, valeur):

            cadre = QFrame()
            cadre.setObjectName("card")
            cadre.setMinimumHeight(120)

            layout = QVBoxLayout(cadre)

            t = QLabel(titre)
            t.setStyleSheet("font-size:13px;color:#888;")

            v = QLabel(valeur)
            v.setStyleSheet("""
                font-size:28px;
                font-weight:bold;
                color:#144b8b;
            """)

            layout.addWidget(t)
            layout.addWidget(v)
            layout.addStretch()

            return cadre

        kpiLayout.addWidget(carte("💰 CA du jour","0 €"))
        kpiLayout.addWidget(carte("📅 CA du mois","0 €"))
        kpiLayout.addWidget(carte("📈 Bénéfice","0 €"))
        kpiLayout.addWidget(carte("🏦 Trésorerie","0 €"))

        dashboardLayout.addLayout(kpiLayout)

        self.pages.addWidget(dashboard)

        #################################################
        # PAGE PRODUITS
        #################################################

        self.pageProduits = ProductsPage()
        self.pageLicences = LicencesPage()
        self.pageMarques = MarquesPage()
        self.pageCanaux = CanauxPage()
        self.pageCategories = CategoriesPage()

        self.pages.addWidget(self.pageProduits)
        self.pages.addWidget(self.pageLicences)
        self.pages.addWidget(self.pageMarques)
        self.pages.addWidget(self.pageCanaux)
        self.pages.addWidget(self.pageCategories)

                #################################################
        # CONNEXIONS
        #################################################

        self.boutons["🏠  Tableau de bord"].clicked.connect(
            lambda: self.pages.setCurrentIndex(0)
        )

        self.boutons["📦  Produits"].clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )
        self.boutons["🏷️  Licences"].clicked.connect(
            lambda: self.pages.setCurrentIndex(2)
        )
        self.boutons["™️  Marques"].clicked.connect(
            lambda: self.pages.setCurrentIndex(3)
        )
        self.boutons["🌐  Canaux de vente"].clicked.connect(
            lambda: self.pages.setCurrentIndex(4)
        )
        self.boutons["📂  Catégories"].clicked.connect(
            lambda: self.pages.setCurrentIndex(5)
        )
        #################################################
        # BARRE D'ETAT
        #################################################

        status = self.statusBar()

        status.showMessage("Prêt")

        version = QLabel("Version 1.0")
        version.setStyleSheet("""
            padding-right:10px;
            color:#666666;
        """)

        status.addPermanentWidget(version)