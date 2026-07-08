from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
)


class EmballageDialog(QDialog):

    def __init__(
        self,
        titre,
        code="",
        nom="",
        longueur_ext_cm=0.0,
        largeur_ext_cm=0.0,
        hauteur_ext_cm=0.0,
        poids_g=0.0,
        cout_ht=0.0,
        calage_ht=0.0,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(480, 620)

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

        layout.addWidget(QLabel("Code (ex : P1, C1, C2...)"))
        self.code = QLineEdit()
        self.code.setText(code)
        layout.addWidget(self.code)

        layout.addSpacing(8)

        layout.addWidget(QLabel(
            "Nom (ex : Petit carton simple cannelure)"
        ))
        self.nom = QLineEdit()
        self.nom.setText(nom)
        layout.addWidget(self.nom)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Dimensions extérieures (cm)"))

        dims = QHBoxLayout()

        self.longueurExt = QDoubleSpinBox()
        self.longueurExt.setMaximum(999)
        self.longueurExt.setPrefix("L: ")
        self.longueurExt.setValue(longueur_ext_cm)

        self.largeurExt = QDoubleSpinBox()
        self.largeurExt.setMaximum(999)
        self.largeurExt.setPrefix("l: ")
        self.largeurExt.setValue(largeur_ext_cm)

        self.hauteurExt = QDoubleSpinBox()
        self.hauteurExt.setMaximum(999)
        self.hauteurExt.setPrefix("h: ")
        self.hauteurExt.setValue(hauteur_ext_cm)

        dims.addWidget(self.longueurExt)
        dims.addWidget(self.largeurExt)
        dims.addWidget(self.hauteurExt)

        layout.addLayout(dims)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Poids de l'emballage vide (g)"))
        self.poids = QDoubleSpinBox()
        self.poids.setMaximum(9999)
        self.poids.setSuffix(" g")
        self.poids.setValue(poids_g)
        layout.addWidget(self.poids)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Coût HT de l'emballage"))
        self.coutHt = QDoubleSpinBox()
        self.coutHt.setDecimals(2)
        self.coutHt.setMaximum(999)
        self.coutHt.setSuffix(" €")
        self.coutHt.setValue(cout_ht)
        layout.addWidget(self.coutHt)

        layout.addSpacing(8)

        layout.addWidget(QLabel(
            "Calage moyen HT (papier bulle, kraft, chips...)"
        ))
        self.calageHt = QDoubleSpinBox()
        self.calageHt.setDecimals(2)
        self.calageHt.setMaximum(999)
        self.calageHt.setSuffix(" €")
        self.calageHt.setValue(calage_ht)
        layout.addWidget(self.calageHt)

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