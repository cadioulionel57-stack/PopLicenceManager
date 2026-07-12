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
    URL de l'image principale du produit — nécessaire pour
    l'export du catalogue vers WiziShop (colonne "Photo 1",
    obligatoire). Les photos sont hébergées ailleurs (sur
    WiziShop ou un autre service) ; on ne stocke ici que le
    lien vers l'image.
    """

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        groupe = QGroupBox("🖼 Image principale")
        form = QFormLayout(groupe)

        info = QLabel(
            "Colle ici l'URL d'une image déjà hébergée (WiziShop "
            "ou ailleurs) — c'est ce lien qui sera utilisé comme "
            "\"Photo 1\" lors de l'export du catalogue."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#5a6b7d; font-size:9pt;")
        form.addRow(info)

        self.imagePrincipale = QLineEdit()
        self.imagePrincipale.setPlaceholderText(
            "https://..."
        )
        form.addRow("URL de l'image", self.imagePrincipale)

        layout.addWidget(groupe)
        layout.addStretch()

    def image_principale(self):

        return self.imagePrincipale.text().strip() or None

    def charger(self, image_principale):

        self.imagePrincipale.setText(image_principale or "")