from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QFormLayout,
)


class EmballageCadeauDialog(QDialog):
    """
    Fenêtre de création/modification d'un code d'emballage
    cadeau.
    """

    def __init__(
        self,
        titre,
        code="",
        nom="",
        cout_ht=0.0,
        type_emballage="principal",
        tarif_facture_ht=2.42,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(500, 420)

        self.setStyleSheet("""
            QDialog{
                background:#edf3fa;
                font-family:"Segoe UI";
            }

            QFrame#card{
                background:white;
                border:1px solid #d8e1ed;
                border-radius:12px;
            }

            QLabel#titre{
                font-size:22px;
                font-weight:bold;
                color:#144b8b;
            }

            QLineEdit, QComboBox, QDoubleSpinBox{
                background:white;
                border:1px solid #cfd8e3;
                border-radius:8px;
                padding:8px;
                font-size:11pt;
            }

            QPushButton{
                background:#144b8b;
                color:white;
                border:none;
                border-radius:8px;
                padding:10px 18px;
                min-width:110px;
            }

            QPushButton:hover{
                background:#1d61b4;
            }
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

        self.code = QLineEdit()
        self.code.setText(code)
        form.addRow("Code", self.code)

        self.nom = QLineEdit()
        self.nom.setText(nom)
        form.addRow("Nom / catégorie", self.nom)

        self.coutHt = QDoubleSpinBox()
        self.coutHt.setDecimals(2)
        self.coutHt.setMaximum(999)
        self.coutHt.setSuffix(" € HT")
        self.coutHt.setValue(cout_ht or 0)
        form.addRow("Coût d'achat", self.coutHt)

        self.type = QComboBox()
        self.type.addItem(
            "Principal — facturé au client (choix visible)",
            "principal"
        )
        self.type.addItem(
            "Supplément — jamais facturé (coût en plus)",
            "supplement"
        )

        index = self.type.findData(type_emballage)
        if index >= 0:
            self.type.setCurrentIndex(index)

        self.type.currentIndexChanged.connect(self._majVisibiliteTarif)

        form.addRow("Type", self.type)

        self.tarifFacture = QDoubleSpinBox()
        self.tarifFacture.setDecimals(2)
        self.tarifFacture.setMaximum(999)
        self.tarifFacture.setSuffix(" € HT")
        self.tarifFacture.setValue(tarif_facture_ht or 2.42)

        self.labelTarif = QLabel("Tarif facturé au client")
        form.addRow(self.labelTarif, self.tarifFacture)

        layout.addLayout(form)

        self._majVisibiliteTarif()

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

    def _majVisibiliteTarif(self):

        est_principal = self.type.currentData() == "principal"

        self.tarifFacture.setVisible(est_principal)
        self.labelTarif.setVisible(est_principal)

    def type_selectionne(self):

        return self.type.currentData()