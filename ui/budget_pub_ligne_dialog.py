from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QFormLayout,
)
from PySide6.QtCore import QDate


class BudgetPubLigneDialog(QDialog):
    """
    Fenêtre de création/modification d'une ligne de budget
    publicitaire (Google Shopping, Amazon Ads, Agence
    SEA...).
    """

    def __init__(
        self, titre, nom="", enveloppe_totale_ht=0.0,
        date_debut=None, date_fin=None,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(500, 400)

        self.setStyleSheet("""
            QDialog{ background:#f4f7fb; font-family:"Segoe UI"; }
            QFrame#card{ background:white; border:1px solid #e1e8f0; border-radius:12px; }
            QLabel#titre{ font-size:22px; font-weight:600; color:#0f2f5c; }
            QLineEdit, QDoubleSpinBox{
                background:#f7f9fc; border:1px solid #d7e0ec;
                border-radius:7px; padding:6px 8px; font-size:10.5pt;
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

        self.nom = QLineEdit()
        self.nom.setPlaceholderText(
            "Ex : Google Shopping, Google Search, Amazon Ads, "
            "Agence SEA..."
        )
        self.nom.setText(nom)
        form.addRow("Nom", self.nom)

        self.enveloppeTotale = QDoubleSpinBox()
        self.enveloppeTotale.setDecimals(2)
        self.enveloppeTotale.setMaximum(9999999)
        self.enveloppeTotale.setSuffix(" € HT")
        self.enveloppeTotale.setValue(enveloppe_totale_ht or 0)
        form.addRow("Enveloppe totale de la période", self.enveloppeTotale)

        self.dateDebut = QLineEdit()
        self.dateDebut.setPlaceholderText("AAAA-MM")
        self.dateDebut.setText(
            date_debut or QDate.currentDate().toString("yyyy-MM")
        )
        form.addRow("Mois de début", self.dateDebut)

        self.dateFin = QLineEdit()
        self.dateFin.setPlaceholderText("AAAA-MM")
        self.dateFin.setText(date_fin or "")
        form.addRow("Mois de fin", self.dateFin)

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