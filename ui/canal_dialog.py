from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QFrame,
)


class CanalDialog(QDialog):

    def __init__(
        self,
        titre,
        nom="",
        type_canal="marketplace",
        commission_pourcentage=0.0,
        frais_fixe_ht=0.0,
        port_inclus=False,
        ordre=0,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(500, 480)

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

            QLabel{
                color:#2d3436;
                font-size:11pt;
            }

            QLineEdit,
            QComboBox,
            QDoubleSpinBox{
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
                min-width:120px;
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

        layout.addWidget(QLabel("Nom du canal (ex : Amazon FBM, Cdiscount, WiziShop...)"))

        self.nom = QLineEdit()
        self.nom.setText(nom)
        layout.addWidget(self.nom)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Type"))

        self.type = QComboBox()
        self.type.addItem("Site (boutique en propre)", "site")
        self.type.addItem("Marketplace", "marketplace")

        index = self.type.findData(type_canal)
        if index != -1:
            self.type.setCurrentIndex(index)

        layout.addWidget(self.type)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Commission de vente (%)"))

        self.commission = QDoubleSpinBox()
        self.commission.setDecimals(2)
        self.commission.setMaximum(100)
        self.commission.setSuffix(" %")
        self.commission.setValue(commission_pourcentage)
        layout.addWidget(self.commission)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Frais fixe par vente (HT)"))

        self.fraisFixe = QDoubleSpinBox()
        self.fraisFixe.setDecimals(2)
        self.fraisFixe.setMaximum(9999)
        self.fraisFixe.setSuffix(" €")
        self.fraisFixe.setValue(frais_fixe_ht)
        layout.addWidget(self.fraisFixe)

        layout.addSpacing(10)

        self.portInclus = QCheckBox(
            "Frais de port inclus dans le prix affiché "
            "(le client voit \"livraison gratuite\")"
        )
        self.portInclus.setChecked(port_inclus)
        layout.addWidget(self.portInclus)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Ordre d'affichage"))

        self.ordre = QDoubleSpinBox()
        self.ordre.setDecimals(0)
        self.ordre.setMaximum(999)
        self.ordre.setValue(ordre)
        layout.addWidget(self.ordre)

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

    def type_canal(self):
        return self.type.currentData()

    def valeur_ordre(self):
        return int(self.ordre.value())