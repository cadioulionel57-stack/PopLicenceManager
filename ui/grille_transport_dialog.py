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
)

from modules.reference_manager import ReferenceManager


class GrilleTransportDialog(QDialog):

    def __init__(
        self,
        titre,
        transporteur_id=None,
        offre="",
        poids_max_kg=0.0,
        prix_ht=0.0,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(480, 400)

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

        layout.addWidget(QLabel("Transporteur"))

        self.transporteur = QComboBox()

        for t in ReferenceManager().tous("transporteurs"):
            self.transporteur.addItem(t["nom"], t["id"])

        index = self.transporteur.findData(transporteur_id)
        if index != -1:
            self.transporteur.setCurrentIndex(index)

        layout.addWidget(self.transporteur)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Offre (ex : Point Relais, Domicile Sans "
            "Signature, Chrono 13, Chrono 18...)"
        ))

        self.offre = QLineEdit()
        self.offre.setText(offre)
        layout.addWidget(self.offre)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Poids maximum pour ce tarif (kg)"))

        self.poidsMax = QDoubleSpinBox()
        self.poidsMax.setDecimals(2)
        self.poidsMax.setMaximum(999)
        self.poidsMax.setValue(poids_max_kg)
        layout.addWidget(self.poidsMax)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Prix HT"))

        self.prixHt = QDoubleSpinBox()
        self.prixHt.setDecimals(2)
        self.prixHt.setMaximum(9999)
        self.prixHt.setSuffix(" €")
        self.prixHt.setValue(prix_ht)
        layout.addWidget(self.prixHt)

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

    def transporteur_id(self):
        return self.transporteur.currentData()
