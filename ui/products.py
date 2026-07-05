from ui.product_dialog_v2 import ProductDialogV2
from ui.product_type_dialog import ProductTypeDialog

from modules.product_manager import ProductManager

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


class ProductsPage(QWidget):

    def __init__(self):

        super().__init__()

        self.manager = ProductManager()

        self.setStyleSheet("""
        QWidget{
            background:#edf3fa;
            font-family:Segoe UI;
        }

        QLabel#titre{
            font-size:26px;
            font-weight:bold;
            color:#144b8b;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px 18px;
            font-size:11pt;
        }

        QPushButton:hover{
            background:#1d61b4;
        }

        QLineEdit{
            background:white;
            border:1px solid #cfd8e3;
            border-radius:8px;
            padding:8px;
            font-size:11pt;
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

        layout = QVBoxLayout(self)

        titre = QLabel("Gestion des produits")
        titre.setObjectName("titre")

        layout.addWidget(titre)

        barre = QHBoxLayout()

        self.recherche = QLineEdit()
        self.recherche.setPlaceholderText("Rechercher un produit...")

        self.btnAjouter = QPushButton("➕ Nouveau produit")
        self.btnModifier = QPushButton("✏ Modifier")
        self.btnSupprimer = QPushButton("🗑 Supprimer")

        barre.addWidget(self.recherche)
        barre.addStretch()
        barre.addWidget(self.btnAjouter)
        barre.addWidget(self.btnModifier)
        barre.addWidget(self.btnSupprimer)

        layout.addLayout(barre)

        self.table = QTableWidget()

        self.table.setColumnCount(12)

        self.table.setHorizontalHeaderLabels([
            "EAN",
            "SKU",
            "Produit",
            "Licence",
            "Catégorie",
            "Fournisseur",
            "PA HT",
            "PV HT",
            "Stock",
            "Poids",
            "Amazon",
            "WiziShop"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.table)

        self.btnAjouter.clicked.connect(self.nouveauProduit)

    def nouveauProduit(self):

        choix = ProductTypeDialog()

        if choix.exec() != choix.DialogCode.Accepted:
            return

        type_produit = choix.typeProduit()

        print("Type choisi :", type_produit)

        dialog = ProductDialogV2()

        dialog.exec()