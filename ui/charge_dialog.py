from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QFrame,
    QFormLayout,
)
from PySide6.QtCore import QDate


class ChargeDialog(QDialog):
    """
    Fenêtre de création/modification d'une charge récurrente
    (loyer, abonnement, prêt, crédit TVA...).
    """

    CATEGORIES = {
        "loyer": "🏠 Loyer",
        "electricite": "💡 Électricité",
        "eau": "💧 Eau",
        "abonnement": "📱 Abonnement",
        "pret": "🏦 Prêt bancaire",
        "credit_tva": "🧾 Crédit TVA",
        "autre": "📌 Autre",
    }

    def __init__(
        self, titre, nom="", categorie="autre", montant_mensuel=0.0,
        mois_debut=None, nombre_occurrences=None, frequence="mensuelle",
        tva_applicable=True,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(550, 500)

        self.setStyleSheet("""
            QDialog{ background:#f4f7fb; font-family:"Segoe UI"; }
            QFrame#card{ background:white; border:1px solid #e1e8f0; border-radius:12px; }
            QLabel#titre{ font-size:22px; font-weight:600; color:#0f2f5c; }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox{
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
        self.nom.setText(nom)
        form.addRow("Nom", self.nom)

        self.categorie = QComboBox()

        for cle, libelle in self.CATEGORIES.items():
            self.categorie.addItem(libelle, cle)

        index = self.categorie.findData(categorie)
        if index >= 0:
            self.categorie.setCurrentIndex(index)

        form.addRow("Catégorie", self.categorie)

        self.frequence = QComboBox()
        self.frequence.addItem("📅 Mensuelle (payée chaque mois)", "mensuelle")
        self.frequence.addItem("📆 Annuelle (payée une fois par an)", "annuelle")

        index_freq = self.frequence.findData(frequence)
        if index_freq >= 0:
            self.frequence.setCurrentIndex(index_freq)

        form.addRow("Fréquence", self.frequence)

        self.montantMensuel = QDoubleSpinBox()
        self.montantMensuel.setDecimals(2)
        self.montantMensuel.setMaximum(999999)
        self.montantMensuel.setSuffix(" €")
        self.montantMensuel.setValue(montant_mensuel or 0)
        form.addRow("Montant (par échéance)", self.montantMensuel)

        self.tvaApplicable = QCheckBox(
            "Cette charge porte de la TVA récupérable (décoche "
            "pour un remboursement de prêt ou un crédit relais "
            "TVA, qui n'en portent pas)"
        )
        self.tvaApplicable.setChecked(tva_applicable)
        form.addRow("", self.tvaApplicable)

        self.moisDebut = QLineEdit()
        self.moisDebut.setPlaceholderText("AAAA-MM, ex : 2026-07")
        self.moisDebut.setText(
            mois_debut or QDate.currentDate().toString("yyyy-MM")
        )
        form.addRow("Mois de première échéance", self.moisDebut)

        self.dureeLimitee = QCheckBox(
            "Durée limitée (prêt, crédit TVA...) — décoché = "
            "récurrent sans fin (loyer, abonnement...)"
        )
        self.dureeLimitee.setChecked(nombre_occurrences is not None)
        self.dureeLimitee.toggled.connect(self._basculerDuree)
        form.addRow("", self.dureeLimitee)

        self.nombreOccurrences = QSpinBox()
        self.nombreOccurrences.setMinimum(1)
        self.nombreOccurrences.setMaximum(999)
        self.nombreOccurrences.setValue(nombre_occurrences or 1)
        self.nombreOccurrences.setEnabled(nombre_occurrences is not None)
        form.addRow("Nombre d'échéances", self.nombreOccurrences)

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

    def _basculerDuree(self, actif):

        self.nombreOccurrences.setEnabled(actif)

    def nombre_occurrences_choisi(self):

        return (
            self.nombreOccurrences.value()
            if self.dureeLimitee.isChecked()
            else None
        )