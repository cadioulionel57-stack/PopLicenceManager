from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QPushButton,
    QMessageBox,
)

from ui.tabs.tab_general import GeneralTab

from modules.numerotation_manager import NumerotationManager
from modules.product_manager import ProductManager


class ProductDialogV2(QDialog):

    def __init__(self, type_produit):

        super().__init__()

        self.type_produit = type_produit

        self.productManager = ProductManager()
        self.numerotation = NumerotationManager()

        self.setWindowTitle("📦 Nouveau produit")
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

        ####################################################
        # Layout principal
        ####################################################

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        ####################################################
        # Onglet Général
        ####################################################

        self.pageGeneral = GeneralTab()

        self.tabs.addTab(
            self.pageGeneral,
            "📦 Général"
        )

        ####################################################
        # Type de produit
        ####################################################

        libelles = {
            "stock": "📦 Produit en stock",
            "dropshipping": "🚚 Direct fournisseur",
            "precommande": "⏳ Précommande",
            "bundle": "🎁 Bundle",
        }

        self.pageGeneral.typeProduit.setText(
            libelles[self.type_produit]
        )

        ####################################################
        # Aperçu du SKU
        ####################################################

        codes = {
            "stock": "SKU_STOCK",
            "dropshipping": "SKU_DROP",
            "precommande": "SKU_PRECO",
            "bundle": "SKU_BUNDLE",
        }

        self.codeNumerotation = codes[self.type_produit]

        self.pageGeneral.sku.setText(
            self.numerotation.apercu(self.codeNumerotation)
        )

        ####################################################
        # Autres onglets
        ####################################################

        self.tabs.addTab(QWidget(), "📏 Caractéristiques")
        self.tabs.addTab(QWidget(), "💰 Tarification")
        self.tabs.addTab(QWidget(), "🌐 SEO")
        self.tabs.addTab(QWidget(), "🖼 Images")
        self.tabs.addTab(QWidget(), "🚀 Publication")
        self.tabs.addTab(QWidget(), "📜 Historique")

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
        self.btnEnregistrer.clicked.connect(self.enregistrer)

    def enregistrer(self):

        sku = self.numerotation.generer(
            self.codeNumerotation
        )

        self.productManager.ajouter(

            type_produit=self.type_produit,

            ean=self.pageGeneral.ean.text(),

            sku=sku,

            nom=self.pageGeneral.nom.text(),

            licence_id=self.pageGeneral.cboLicence.id(),

            marque_id=self.pageGeneral.cboMarque.id(),

            fournisseur_id=self.pageGeneral.cboFournisseur.id(),

            reference_fournisseur=self.pageGeneral.referenceFournisseur.text()

        )

        QMessageBox.information(
            self,
            "Produit",
            "Produit enregistré avec succès."
        )

        self.accept()