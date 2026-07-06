from ui.product_dialog_v2 import ProductDialogV2
from ui.product_type_dialog import ProductTypeDialog

from modules.product_manager import ProductManager

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
)

class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = ProductManager()
        self.setStyleSheet("""QWidget{background:#edf3fa;font-family:Segoe UI;}QLabel#titre{font-size:26px;font-weight:bold;color:#144b8b;}QPushButton{background:#144b8b;color:white;border:none;border-radius:8px;padding:10px 18px;font-size:11pt;}QPushButton:hover{background:#1d61b4;}QLineEdit{background:white;border:1px solid #cfd8e3;border-radius:8px;padding:8px;font-size:11pt;}QTableWidget{background:white;border:none;border-radius:10px;gridline-color:#e8edf5;}QHeaderView::section{background:#144b8b;color:white;font-weight:bold;border:none;padding:8px;}""")
        layout=QVBoxLayout(self)
        t=QLabel("Gestion des produits"); t.setObjectName("titre"); layout.addWidget(t)
        barre=QHBoxLayout()
        self.recherche=QLineEdit(); self.recherche.setPlaceholderText("Rechercher un produit...")
        self.btnAjouter=QPushButton("➕ Nouveau produit")
        self.btnModifier=QPushButton("✏ Ouvrir")
        self.btnSupprimer=QPushButton("🗑 Supprimer")
        barre.addWidget(self.recherche); barre.addStretch(); barre.addWidget(self.btnAjouter); barre.addWidget(self.btnModifier); barre.addWidget(self.btnSupprimer)
        layout.addLayout(barre)
        self.table=QTableWidget(); self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID","","SKU","Produit","Licence","Marque","Fournisseur","EAN"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(0,True)
        layout.addWidget(self.table)
        self.btnAjouter.clicked.connect(self.nouveauProduit)
        self.btnModifier.clicked.connect(self.ouvrirProduit)
        self.table.doubleClicked.connect(self.ouvrirProduit)
        self.charger()
    def charger(self):
        self.table.setRowCount(0)
        ic={"stock":"📦","dropshipping":"🚚","precommande":"⏳","bundle":"🎁"}
        for r,p in enumerate(self.manager.tous()):
            self.table.insertRow(r)
            vals=[str(p["id"]),ic.get(p["type_produit"],"❓"),p["sku"] or "",p["nom"] or "",p["licence"] or "",p["marque"] or "",p["fournisseur"] or "",p["ean"] or ""]
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(v))
    def nouveauProduit(self):
        choix=ProductTypeDialog()
        if choix.exec()!=choix.DialogCode.Accepted: return
        d=ProductDialogV2(choix.typeProduit())
        if d.exec()==d.DialogCode.Accepted: self.charger()
    def ouvrirProduit(self):
        ligne=self.table.currentRow()
        if ligne<0: return
        print("Produit sélectionné :", int(self.table.item(ligne,0).text()))