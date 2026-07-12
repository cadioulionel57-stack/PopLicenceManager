from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QLabel,
)


class ImagesTab(QWidget):
    """
    URLs des images du produit (jusqu'à 3) — nécessaires
    pour l'export du catalogue vers WiziShop (colonnes
    "Photo 1", "Photo 2", "Photo 3"). Les photos sont
    hébergées ailleurs (WiziShop ou un autre service) ; on
    ne stocke ici que les liens vers les images.
    """

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        groupe = QGroupBox("🖼 Images")
        form = QFormLayout(groupe)

        info = QLabel(
            "Colle ici les URLs d'images déjà hébergées (WiziShop "
            "ou ailleurs) — ces liens seront utilisés comme "
            "\"Photo 1/2/3\" lors de l'export du catalogue."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#5a6b7d; font-size:9pt;")
        form.addRow(info)

        self.imagePrincipale = QLineEdit()
        self.imagePrincipale.setPlaceholderText("https://...")
        form.addRow("Photo 1 (principale)", self.imagePrincipale)

        self.image2 = QLineEdit()
        self.image2.setPlaceholderText("https://...")
        form.addRow("Photo 2", self.image2)

        self.image3 = QLineEdit()
        self.image3.setPlaceholderText("https://...")
        form.addRow("Photo 3", self.image3)

        layout.addWidget(groupe)
        layout.addStretch()

    def image_principale(self):

        return self.imagePrincipale.text().strip() or None

    def image_2(self):

        return self.image2.text().strip() or None

    def image_3(self):

        return self.image3.text().strip() or None

    def charger(self, image_principale, image_2, image_3):

        self.imagePrincipale.setText(image_principale or "")
        self.image2.setText(image_2 or "")
        self.image3.setText(image_3 or "")