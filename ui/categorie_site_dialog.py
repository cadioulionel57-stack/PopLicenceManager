from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFrame,
    QFormLayout,
)


class CategorieSiteDialog(QDialog):
    """
    Fenêtre de création/modification d'une catégorie ou
    sous-catégorie du site (WiziShop) — nom exact + ID
    WiziShop, et éventuellement une catégorie principale de
    rattachement pour en faire une sous-catégorie.
    """

    def __init__(
        self, titre, categories_principales, nom="", id_wizishop="",
        categorie_parente_id=None,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(550, 450)

        self.setStyleSheet("""
            QDialog{ background:#f4f7fb; font-family:"Segoe UI"; }
            QFrame#card{ background:white; border:1px solid #e1e8f0; border-radius:12px; }
            QLabel#titre{ font-size:20px; font-weight:600; color:#0f2f5c; }
            QLineEdit, QComboBox{
                background:#f7f9fc; border:1px solid #d7e0ec;
                border-radius:7px; padding:8px; font-size:10.5pt;
            }
            QPushButton{
                background:#144b8b; color:white; border:none;
                border-radius:8px; padding:10px 18px; min-width:110px;
            }
            QPushButton:hover{ background:#1d61b4; }
        """)

        principal = QVBoxLayout(self)
        carte = QFrame()
        carte.setObjectName("card")
        principal.addWidget(carte)
        layout = QVBoxLayout(carte)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")
        layout.addWidget(titreLabel)
        layout.addSpacing(10)

        form = QFormLayout()

        self.typeCategorie = QComboBox()
        self.typeCategorie.addItem(
            "Catégorie principale", None
        )
        self.typeCategorie.addItem(
            "Sous-catégorie (rattachée à une principale)", "sous"
        )
        self.typeCategorie.currentIndexChanged.connect(
            self._basculerParent
        )
        form.addRow("Type", self.typeCategorie)

        self.categorieParente = QComboBox()

        for cat in categories_principales:
            self.categorieParente.addItem(cat["nom"], cat["id"])

        self.categorieParente.setEnabled(False)
        form.addRow("Catégorie principale", self.categorieParente)

        self.nom = QLineEdit()
        self.nom.setPlaceholderText(
            "Nom exact tel que sur WiziShop"
        )
        self.nom.setText(nom)
        form.addRow("Nom", self.nom)

        self.idWizishop = QLineEdit()
        self.idWizishop.setPlaceholderText("Ex : 12 (sans le #)")
        self.idWizishop.setText(id_wizishop or "")
        form.addRow("ID WiziShop", self.idWizishop)

        layout.addLayout(form)
        layout.addStretch()

        boutons = QHBoxLayout()
        boutons.addStretch()
        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")
        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)
        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)

        if categorie_parente_id is not None:

            index_type = self.typeCategorie.findData("sous")
            self.typeCategorie.setCurrentIndex(index_type)

            index_parent = self.categorieParente.findData(
                categorie_parente_id
            )
            if index_parent >= 0:
                self.categorieParente.setCurrentIndex(index_parent)

    def _basculerParent(self):

        est_sous_categorie = self.typeCategorie.currentData() == "sous"
        self.categorieParente.setEnabled(est_sous_categorie)

    def categorie_parente_choisie(self):

        if self.typeCategorie.currentData() != "sous":
            return None

        return self.categorieParente.currentData()