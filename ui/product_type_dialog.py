from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
)


class ProductTypeDialog(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Nouveau produit")
        self.resize(500, 350)

        layout = QVBoxLayout(self)

        titre = QLabel(
            "Quel type de produit souhaitez-vous créer ?"
        )

        titre.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
            color:#144b8b;
            padding-bottom:15px;
        """)

        layout.addWidget(titre)

        self.groupe = QButtonGroup(self)

        self.stock = QRadioButton("📦 Produit en stock")
        self.drop = QRadioButton("🚚 Direct fournisseur")
        self.preco = QRadioButton("⏳ Précommande")
        self.bundle = QRadioButton("🎁 Bundle")

        self.stock.setChecked(True)

        self.groupe.addButton(self.stock)
        self.groupe.addButton(self.drop)
        self.groupe.addButton(self.preco)
        self.groupe.addButton(self.bundle)

        layout.addWidget(self.stock)
        layout.addWidget(self.drop)
        layout.addWidget(self.preco)
        layout.addWidget(self.bundle)

        layout.addStretch()

        self.btnContinuer = QPushButton("Continuer")

        layout.addWidget(self.btnContinuer)

        self.btnContinuer.clicked.connect(self.accept)

    def typeProduit(self):

        if self.stock.isChecked():
            return "stock"

        if self.drop.isChecked():
            return "dropshipping"

        if self.preco.isChecked():
            return "precommande"

        return "bundle"