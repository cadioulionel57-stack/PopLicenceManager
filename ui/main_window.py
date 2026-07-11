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
from ui.familles_produit import FamillesProduitPage
from ui.grille_transport import GrilleTransportPage
from ui.grille_fba import GrilleFbaPage
from ui.emballages import EmballagesPage
from ui.emballages_cadeau import EmballagesCadeauPage
from ui.achats_stocks import AchatsStocksPage
from ui.tresorerie import TresoreriePage
from ui.politique_transport import PolitiqueTransportPage
from ui.fournisseurs import FournisseursPage
from ui.commandes import CommandesPage
from ui.sav import SavPage
from modules.commande_manager import CommandeManager

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
            "🏭  Familles de produit",
            "🚚  Grille de transport",
            "📦  Grille FBA",
            "📮  Grille d'emballage",
            "🎁  Emballages Cadeau",
            "🚚  Politique frais de port",
            "🚚  Fournisseurs",
            "🛒  Commandes",
            "🔧  SAV / Retours",
            "🧾  Achats Stocks",
            "🏦  Trésorerie",
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

        def carte(titre, valeur, couleur="#144b8b"):

            cadre = QFrame()
            cadre.setObjectName("card")
            cadre.setMinimumHeight(120)

            layout = QVBoxLayout(cadre)

            t = QLabel(titre)
            t.setStyleSheet("font-size:13px;color:#888;")

            v = QLabel(valeur)
            v.setStyleSheet(f"""
                font-size:28px;
                font-weight:bold;
                color:{couleur};
            """)

            layout.addWidget(t)
            layout.addWidget(v)
            layout.addStretch()

            cadre.labelValeur = v

            return cadre

        self.carteCaJour = carte("💰 CA du jour", "0 €", "#000000")
        self.carteCaMois = carte("📅 CA du mois", "0 €", "#000000")
        self.carteCaPrestations = carte("🎁 CA Prestations (mois)", "0 €", "#000000")
        self.carteBenefice = carte("📈 Bénéfice", "0 €", "#1e7d32")
        self.carteTresorerieKpi = carte("🏦 Trésorerie", "0 €", "#000000")
        self.carteSav = carte("🔧 Coûts SAV", "0 €", "#7b241c")
        self.carteTvaCollectee = carte("🧾 TVA collectée (mois)", "0 €", "#e67e22")
        self.carteTvaDeductible = carte("🧾 TVA déductible (mois)", "0 €", "#8e44ad")
        self.carteTvaNette = carte("🧾 TVA nette à payer (mois)", "0 €", "#c0392b")

        kpiLayout.addWidget(self.carteCaJour)
        kpiLayout.addWidget(self.carteCaMois)
        kpiLayout.addWidget(self.carteCaPrestations)
        kpiLayout.addWidget(self.carteBenefice)
        kpiLayout.addWidget(self.carteTresorerieKpi)
        kpiLayout.addWidget(self.carteSav)

        dashboardLayout.addLayout(kpiLayout)

        kpiLayoutTva = QHBoxLayout()
        kpiLayoutTva.addWidget(self.carteTvaCollectee)
        kpiLayoutTva.addWidget(self.carteTvaDeductible)
        kpiLayoutTva.addWidget(self.carteTvaNette)

        dashboardLayout.addLayout(kpiLayoutTva)

        self._rafraichirKpiSav()
        self._rafraichirKpiCa()
        self._rafraichirKpiTva()
        self._rafraichirKpiTresorerie()

        self.pages.addWidget(dashboard)

        #################################################
        # PAGE PRODUITS
        #################################################

        self.pageProduits = ProductsPage()
        self.pageLicences = LicencesPage()
        self.pageMarques = MarquesPage()
        self.pageCanaux = CanauxPage()
        self.pageCategories = CategoriesPage()
        self.pageFamillesProduit = FamillesProduitPage()
        self.pageGrilleTransport = GrilleTransportPage()
        self.pageGrilleFba = GrilleFbaPage()
        self.pageEmballages = EmballagesPage()
        self.pagePolitiqueTransport = PolitiqueTransportPage()
        self.pageFournisseurs = FournisseursPage()
        self.pageCommandes = CommandesPage()

        self.pageSav = SavPage(
            ouvrir_commande_callback=self._ouvrirCommandeDepuisSav
        )

        self.pageEmballagesCadeau = EmballagesCadeauPage()
        self.pageAchatsStocks = AchatsStocksPage()
        self.pageTresorerie = TresoreriePage()
        self.pageTresorerie.alimenter_fonds_croissance_si_nouveau_mois()

        self.pages.addWidget(self.pageProduits)
        self.pages.addWidget(self.pageLicences)
        self.pages.addWidget(self.pageMarques)
        self.pages.addWidget(self.pageCanaux)
        self.pages.addWidget(self.pageCategories)
        self.pages.addWidget(self.pageFamillesProduit)
        self.pages.addWidget(self.pageGrilleTransport)
        self.pages.addWidget(self.pageGrilleFba)
        self.pages.addWidget(self.pageEmballages)
        self.pages.addWidget(self.pagePolitiqueTransport)
        self.pages.addWidget(self.pageFournisseurs)
        self.pages.addWidget(self.pageCommandes)
        self.pages.addWidget(self.pageSav)
        self.pages.addWidget(self.pageEmballagesCadeau)
        self.pages.addWidget(self.pageAchatsStocks)
        self.pages.addWidget(self.pageTresorerie)

                #################################################
        # CONNEXIONS
        #################################################

        self.boutons["🏠  Tableau de bord"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(0),
                self._rafraichirKpiSav(),
                self._rafraichirKpiCa(),
                self._rafraichirKpiTva(),
                self._rafraichirKpiTresorerie()
            )
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
        self.boutons["🏭  Familles de produit"].clicked.connect(
            lambda: self.pages.setCurrentIndex(6)
        )
        self.boutons["🚚  Grille de transport"].clicked.connect(
            lambda: self.pages.setCurrentIndex(7)
        )
        self.boutons["📦  Grille FBA"].clicked.connect(
            lambda: self.pages.setCurrentIndex(8)
        )
        self.boutons["📮  Grille d'emballage"].clicked.connect(
            lambda: self.pages.setCurrentIndex(9)
        )
        self.boutons["🚚  Politique frais de port"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(10),
                self.pagePolitiqueTransport.charger()
            )
        )
        self.boutons["🚚  Fournisseurs"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(11),
                self.pageFournisseurs.charger()
            )
        )
        self.boutons["🛒  Commandes"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(12),
                self.pageCommandes.charger()
            )
        )
        self.boutons["🔧  SAV / Retours"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(13),
                self.pageSav.charger()
            )
        )
        self.boutons["🎁  Emballages Cadeau"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(14),
                self.pageEmballagesCadeau.charger()
            )
        )
        self.boutons["🧾  Achats Stocks"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(15),
                self.pageAchatsStocks.charger()
            )
        )
        self.boutons["🏦  Trésorerie"].clicked.connect(
            lambda: (
                self.pages.setCurrentIndex(16),
                self.pageTresorerie.charger()
            )
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

    def _rafraichirKpiSav(self):
        """
        Recalcule et réaffiche le coût SAV total (tous
        retours actifs, toutes commandes confondues) — à
        chaque fois qu'on revient sur le tableau de bord,
        puisque les commandes peuvent avoir changé entre-
        temps.
        """

        total = CommandeManager().total_sav()

        self.carteSav.labelValeur.setText(f"{total:.2f} €")

    def _rafraichirKpiCa(self):
        """
        Recalcule et réaffiche le CA du jour, le CA du mois,
        et le Bénéfice du mois (gain net réel cumulé de
        toutes les commandes du mois).
        """

        manager = CommandeManager()

        self.carteCaJour.labelValeur.setText(
            f"{manager.ca_jour():.2f} €"
        )
        self.carteCaMois.labelValeur.setText(
            f"{manager.ca_mois():.2f} €"
        )
        self.carteCaPrestations.labelValeur.setText(
            f"{manager.ca_prestations_mois():.2f} €"
        )
        self.carteBenefice.labelValeur.setText(
            f"{manager.benefice_mois():.2f} €"
        )

    def _rafraichirKpiTva(self):
        """
        Recalcule et réaffiche la TVA collectée, déductible
        et nette du mois — approximation au taux standard
        20%, basée sur les commandes ET sur les charges
        récurrentes réellement payées ce mois (loyer,
        électricité, abonnements... hors prêt et crédit
        relais TVA, qui n'en portent pas).
        """

        from modules.tresorerie_manager import TresorerieManager

        tva = CommandeManager().tva_mois()

        tva_deductible_charges = (
            TresorerieManager().tva_deductible_charges()
        )

        tva_collectee = tva["tva_collectee"]
        tva_deductible = (
            tva["tva_deductible"] + tva_deductible_charges
        )
        tva_nette = round(tva_collectee - tva_deductible, 2)

        self.carteTvaCollectee.labelValeur.setText(
            f"{tva_collectee:.2f} €"
        )
        self.carteTvaDeductible.labelValeur.setText(
            f"{tva_deductible:.2f} €"
        )
        self.carteTvaNette.labelValeur.setText(
            f"{tva_nette:.2f} €"
        )

    def _rafraichirKpiTresorerie(self):
        """
        Recalcule et réaffiche le solde de trésorerie actuel
        sur le tableau de bord.
        """

        from modules.tresorerie_manager import TresorerieManager

        solde = TresorerieManager().solde_actuel()

        self.carteTresorerieKpi.labelValeur.setText(
            f"{solde:.2f} €" if solde is not None else "Non renseigné"
        )

    def _ouvrirCommandeDepuisSav(self, commande_id):
        """
        Bascule sur l'écran Commandes et ouvre directement
        la fiche de la commande concernée — appelé depuis
        l'écran SAV quand on double-clique sur un retour.
        """

        self.pages.setCurrentIndex(12)
        self.pageCommandes.ouvrirCommandeParId(commande_id)
        self.pageSav.charger()