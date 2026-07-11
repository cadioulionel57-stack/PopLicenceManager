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


class PeriodeCommercialeDialog(QDialog):
    """
    Fenêtre de création/modification d'une période
    commerciale (Noël, Rentrée scolaire...).
    """

    def __init__(
        self, titre, nom="", date_debut="", date_fin="",
        budget_supplementaire_ht=0.0,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(500, 400)

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

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")
        layout.addWidget(titreLabel)
        layout.addSpacing(10)

        form = QFormLayout()

        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Ex : Noël, Rentrée scolaire...")
        self.nom.setText(nom)
        form.addRow("Nom de la période", self.nom)

        self.dateDebut = QLineEdit()
        self.dateDebut.setPlaceholderText("AAAA-MM-JJ")
        self.dateDebut.setText(date_debut)
        form.addRow("Date de début", self.dateDebut)

        self.dateFin = QLineEdit()
        self.dateFin.setPlaceholderText("AAAA-MM-JJ")
        self.dateFin.setText(date_fin)
        form.addRow("Date de fin", self.dateFin)

        self.budgetSupplementaire = QDoubleSpinBox()
        self.budgetSupplementaire.setDecimals(2)
        self.budgetSupplementaire.setMaximum(999999)
        self.budgetSupplementaire.setSuffix(" € HT")
        self.budgetSupplementaire.setValue(budget_supplementaire_ht or 0)
        form.addRow(
            "Budget en plus (optionnel)", self.budgetSupplementaire
        )

        layout.addLayout(form)

        info = QLabel(
            "Le budget de cette période reprend automatiquement ce "
            "que tu as déjà saisi sur les lignes habituelles pendant "
            "ces dates, plus le montant en plus indiqué ci-dessus."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#5a6b7d; font-size:9pt;")
        layout.addWidget(info)

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