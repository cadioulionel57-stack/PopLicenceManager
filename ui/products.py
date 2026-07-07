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
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
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
        self.btnModifier = QPushButton("✏ Ouvrir")
        self.btnSupprimer = QPushButton("🗑 Supprimer")

        barre.addWidget(self.recherche)
        barre.addStretch()
        barre.addWidget(self.btnAjouter)
        barre.addWidget(self.btnModifier)
        barre.addWidget(self.btnSupprimer)

        layout.addLayout(barre)

        self.table = QTableWidget()
        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "",
            "SKU",
            "Produit",
            "Licence",
            "Marque",
            "Fournisseur",
            "EAN"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setColumnHidden(0, True)


        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.table.clearSelection()
        layout.addWidget(self.table)
        

        self.recherche.textChanged.connect(
            self.rechercher
        )

        self.btnAjouter.clicked.connect(self.nouveauProduit)
        self.btnModifier.clicked.connect(self.ouvrirProduit)
        self.btnSupprimer.clicked.connect(self.supprimerProduit)

        self.table.doubleClicked.connect(self.ouvrirProduit)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        icones = {
            "stock": "📦",
            "dropshipping": "🚚",
            "precommande": "⏳",
            "bundle": "🎁",
        }

        produits = self.manager.tous()

        for ligne, produit in enumerate(produits):

            self.table.insertRow(ligne)

            valeurs = [
                str(produit["id"]),
                icones.get(produit["type_produit"], "❓"),
                produit["sku"] or "",
                produit["nom"] or "",
                produit["licence"] or "",
                produit["marque"] or "",
                produit["fournisseur"] or "",
                produit["ean"] or "",
            ]

            for colonne, valeur in enumerate(valeurs):

                self.table.setItem(
                    ligne,
                    colonne,
                    QTableWidgetItem(valeur)
                )

        self.table.clearSelection()

    def nouveauProduit(self):

        choix = ProductTypeDialog()

        if choix.exec() != choix.DialogCode.Accepted:
            return

        dialog = ProductDialogV2(
            choix.typeProduit()
        )

        if dialog.exec() == dialog.DialogCode.Accepted:
                self.charger()

    def ouvrirProduit(self):

        print("ouvrirProduit appelée")

        ligne = self.table.currentRow()

        print("Ligne sélectionnée :", ligne)

        if ligne < 0:
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        print("ID :", identifiant)

        produit = self.manager.obtenir(identifiant)

        dialog = ProductDialogV2(
            produit=produit
)

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.charger()


    def supprimerProduit(self):

        ligne = self.table.currentRow()

        if ligne < 0:
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        from PySide6.QtWidgets import QMessageBox

        reponse = QMessageBox.question(
            self,
            "Suppression",
            "Voulez-vous vraiment supprimer ce produit ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reponse != QMessageBox.Yes:
            return

        self.manager.supprimer(identifiant)

        self.charger()

    def rechercher(self, texte):

        texte = texte.lower()

        for ligne in range(self.table.rowCount()):

            visible = False

            for colonne in range(self.table.columnCount()):

                item = self.table.item(ligne, colonne)

                if item is not None and texte in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(
                ligne,
                not visible
            )