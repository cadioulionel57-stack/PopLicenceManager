from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QLineEdit,
)


class CaracteristiquesTab(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        ####################################################
        # Catégories
        ####################################################

        categorie = QGroupBox("📂 Catégories")

        form = QFormLayout(categorie)

        self.categoriePop = QComboBox()
        self.categorieAmazon = QComboBox()
        self.categorieWizi = QComboBox()

        form.addRow("Catégorie Pop Licence", self.categoriePop)
        form.addRow("Catégorie Amazon", self.categorieAmazon)
        form.addRow("Catégorie WiziShop", self.categorieWizi)

        layout.addWidget(categorie)

        ####################################################
        # Dimensions
        ####################################################

        dimensions = QGroupBox("📦 Dimensions")

        form2 = QFormLayout(dimensions)

        self.longueur = QDoubleSpinBox()
        self.largeur = QDoubleSpinBox()
        self.hauteur = QDoubleSpinBox()
        self.poids = QDoubleSpinBox()

        for champ in (
            self.longueur,
            self.largeur,
            self.hauteur,
            self.poids,
        ):
            champ.setDecimals(2)
            champ.setMaximum(9999)

        form2.addRow("Longueur (cm)", self.longueur)
        form2.addRow("Largeur (cm)", self.largeur)
        form2.addRow("Hauteur (cm)", self.hauteur)
        form2.addRow("Poids (kg)", self.poids)

        layout.addWidget(dimensions)

        ####################################################
        # Informations
        ####################################################

        infos = QGroupBox("ℹ Informations")

        form3 = QFormLayout(infos)

        self.matiere = QLineEdit()
        self.couleur = QLineEdit()
        self.age = QSpinBox()

        self.age.setMaximum(99)

        self.fabrication = QLineEdit()

        form3.addRow("Matière", self.matiere)
        form3.addRow("Couleur", self.couleur)
        form3.addRow("Âge minimum", self.age)
        form3.addRow("Pays de fabrication", self.fabrication)

        layout.addWidget(infos)

        layout.addStretch()