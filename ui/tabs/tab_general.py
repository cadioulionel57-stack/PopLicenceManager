from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
)

from ui.widgets.reference_combobox import ReferenceComboBox


class GeneralTab(QWidget):

    def __init__(self):
        super().__init__()

        principal = QVBoxLayout(self)

        origine = QGroupBox("📦 Origine")
        formOrigine = QFormLayout(origine)

        self.typeProduit = QLineEdit()
        self.typeProduit.setReadOnly(True)
        formOrigine.addRow("Type de produit", self.typeProduit)

        ligneFournisseur = QHBoxLayout()
        self.cboFournisseur = ReferenceComboBox("fournisseurs")
        self.btnAjouterFournisseur = QPushButton("+")
        self.btnAjouterFournisseur.setFixedWidth(35)
        ligneFournisseur.addWidget(self.cboFournisseur)
        ligneFournisseur.addWidget(self.btnAjouterFournisseur)
        formOrigine.addRow("Fournisseur", ligneFournisseur)

        self.referenceFournisseur = QLineEdit()
        formOrigine.addRow("Référence fournisseur", self.referenceFournisseur)

        self.prixAchatHt = QDoubleSpinBox()
        self.prixAchatHt.setDecimals(2)
        self.prixAchatHt.setMaximum(99999)
        self.prixAchatHt.setSuffix(" €")
        formOrigine.addRow("Prix d'achat fournisseur (HT)", self.prixAchatHt)

        self.commandeFournisseur = QComboBox()
        formOrigine.addRow("Commande fournisseur", self.commandeFournisseur)

        principal.addWidget(origine)

        classification = QGroupBox("🏷 Classification")
        formClassification = QFormLayout(classification)

        ligneLicence = QHBoxLayout()
        self.cboLicence = ReferenceComboBox("licences")
        self.btnAjouterLicence = QPushButton("+")
        self.btnAjouterLicence.setFixedWidth(35)
        ligneLicence.addWidget(self.cboLicence)
        ligneLicence.addWidget(self.btnAjouterLicence)
        formClassification.addRow("Licence", ligneLicence)

        ligneMarque = QHBoxLayout()
        self.cboMarque = ReferenceComboBox("marques")
        self.btnAjouterMarque = QPushButton("+")
        self.btnAjouterMarque.setFixedWidth(35)
        ligneMarque.addWidget(self.cboMarque)
        ligneMarque.addWidget(self.btnAjouterMarque)
        formClassification.addRow("Marque", ligneMarque)

        principal.addWidget(classification)

        identification = QGroupBox("📝 Identification")
        formIdentification = QFormLayout(identification)

        self.nom = QLineEdit()
        self.ean = QLineEdit()
        self.sku = QLineEdit()
        self.sku.setReadOnly(True)

        formIdentification.addRow("Nom", self.nom)
        formIdentification.addRow("EAN", self.ean)
        formIdentification.addRow("SKU", self.sku)

        principal.addWidget(identification)
        principal.addStretch()