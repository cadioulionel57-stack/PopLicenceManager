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


class BudgetPubDepenseDialog(QDialog):
    """
    Fenêtre de saisie d'une dépense publicitaire réelle,
    pour un mois donné — saisie libre, aucune répartition
    imposée d'un mois à l'autre.
    """

    def __init__(self, titre, nom_ligne, mois=None, montant=0.0):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(450, 320)

        self.setStyleSheet("""
            QDialog{ background:#f4f7fb; font-family:"Segoe UI"; }
            QFrame#card{ background:white; border:1px solid #e1e8f0; border-radius:12px; }
            QLabel#titre{ font-size:20px; font-weight:600; color:#0f2f5c; }
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

        titreLabel = QLabel(f"{titre} — {nom_ligne}")
        titreLabel.setObjectName("titre")
        titreLabel.setWordWrap(True)
        layout.addWidget(titreLabel)
        layout.addSpacing(10)

        form = QFormLayout()

        self.mois = QLineEdit()
        self.mois.setPlaceholderText("AAAA-MM")
        self.mois.setText(mois or QDate.currentDate().toString("yyyy-MM"))
        form.addRow("Mois", self.mois)

        self.montant = QDoubleSpinBox()
        self.montant.setDecimals(2)
        self.montant.setMaximum(999999)
        self.montant.setSuffix(" € HT")
        self.montant.setValue(montant or 0)
        form.addRow("Montant dépensé", self.montant)

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