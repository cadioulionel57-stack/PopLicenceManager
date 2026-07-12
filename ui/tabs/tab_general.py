from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
)
from PySide6.QtGui import QColor

from ui.widgets.reference_combobox import ReferenceComboBox


class GeneralTab(QWidget):

    STATUTS = {
        "actif": ("✅ Actif", "#1e7d32"),
        "rupture": ("⚠ En rupture", "#e67e22"),
        "fin_de_vie": ("⛔ Fin de vie", "#c0392b"),
    }

    def __init__(self):
        super().__init__()

        exterieur = QVBoxLayout(self)
        exterieur.setContentsMargins(0, 0, 0, 0)

        zoneDefilement = QScrollArea()
        zoneDefilement.setWidgetResizable(True)
        zoneDefilement.setStyleSheet(
            "QScrollArea{border:none; background:transparent;}"
        )

        contenuDefilant = QWidget()
        principal = QVBoxLayout(contenuDefilant)

        zoneDefilement.setWidget(contenuDefilant)
        exterieur.addWidget(zoneDefilement)

        origine = QGroupBox("📦 Origine")
        formOrigine = QFormLayout(origine)

        self.typeProduit = QLineEdit()
        self.typeProduit.setReadOnly(True)
        formOrigine.addRow("Type de produit", self.typeProduit)

        self.statutStock = QComboBox()

        for cle, (libelle, couleur) in self.STATUTS.items():
            self.statutStock.addItem(libelle, cle)

        self.statutStock.currentIndexChanged.connect(
            self._majCouleurStatut
        )
        self._majCouleurStatut()

        formOrigine.addRow("Statut du produit", self.statutStock)

        self.quantiteStock = QSpinBox()
        self.quantiteStock.setMaximum(99999)
        self.quantiteStock.setToolTip(
            "Quantité réellement en stock — distincte du statut "
            "ci-dessus. Sert de base au \"Nombre de produits en "
            "stock\" exporté vers WiziShop, et reste juste même si "
            "ce produit est un jour réimporté puis réexporté."
        )
        formOrigine.addRow("Quantité en stock", self.quantiteStock)

        self.ficheATerminer = QCheckBox(
            "⚠ Fiche à compléter (créée rapidement, infos "
            "manquantes — décoche une fois terminée)"
        )
        self.ficheATerminer.setStyleSheet(
            "color:#c0392b; font-weight:600;"
        )
        formOrigine.addRow("", self.ficheATerminer)

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

    def _majCouleurStatut(self):

        cle = self.statutStock.currentData() or "actif"

        _libelle, couleur = self.STATUTS.get(
            cle, self.STATUTS["actif"]
        )

        self.statutStock.setStyleSheet(
            f"color:{couleur}; font-weight:600;"
        )

    def statut_stock(self):

        return self.statutStock.currentData()

    def selectionner_statut_stock(self, statut):

        index = self.statutStock.findData(statut or "actif")

        if index >= 0:
            self.statutStock.setCurrentIndex(index)