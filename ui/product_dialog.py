from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
)


class ProductDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nouveau produit")
        self.resize(700, 650)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.ean = QLineEdit()
        self.sku = QLineEdit()
        self.nom = QLineEdit()
        self.licence = QLineEdit()
        self.categorie = QLineEdit()
        self.fournisseur = QLineEdit()

        self.prixAchat = QDoubleSpinBox()
        self.prixAchat.setMaximum(999999)

        self.prixVente = QDoubleSpinBox()
        self.prixVente.setMaximum(999999)

        self.stock = QSpinBox()
        self.stock.setMaximum(999999)

        self.poids = QDoubleSpinBox()
        self.poids.setMaximum(999)

        self.amazon = QCheckBox("Publié sur Amazon")
        self.wizishop = QCheckBox("Publié sur WiziShop")

        form.addRow("EAN", self.ean)
        form.addRow("SKU", self.sku)
        form.addRow("Nom", self.nom)
        form.addRow("Licence", self.licence)
        form.addRow("Catégorie", self.categorie)
        form.addRow("Fournisseur", self.fournisseur)
        form.addRow("Prix achat HT", self.prixAchat)
        form.addRow("Prix vente HT", self.prixVente)
        form.addRow("Stock", self.stock)
        form.addRow("Poids", self.poids)
        form.addRow("", self.amazon)
        form.addRow("", self.wizishop)

        layout.addLayout(form)

        boutons = QHBoxLayout()

        self.btnEnregistrer = QPushButton("Enregistrer")
        self.btnAnnuler = QPushButton("Annuler")

        boutons.addStretch()
        boutons.addWidget(self.btnEnregistrer)
        boutons.addWidget(self.btnAnnuler)

        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)