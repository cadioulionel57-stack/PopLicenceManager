from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QTextEdit,
    QPushButton,
    QFrame,
    QFormLayout,
)
from PySide6.QtCore import QDate


class RetourDialog(QDialog):
    """
    Fenêtre de signalement d'un retour, lié à un produit
    précis de la commande (pas à toute la commande).
    """

    def __init__(self, titre, produits, donnees_existantes=None):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(550, 600)

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

            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
            QTextEdit{
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

        self.produit = QComboBox()
        self.produit.addItems(produits)
        form.addRow("Produit concerné", self.produit)

        self.dateRetour = QDateEdit()
        self.dateRetour.setCalendarPopup(True)
        self.dateRetour.setDate(QDate.currentDate())
        form.addRow("Date du retour", self.dateRetour)

        self.motif = QLineEdit()
        self.motif.setPlaceholderText(
            "Ex : produit endommagé, ne convient pas..."
        )
        form.addRow("Motif", self.motif)

        self.statut = QComboBox()
        self.statut.addItems([
            "Demandé", "Reçu", "Remboursé", "Refusé"
        ])
        form.addRow("Statut", self.statut)

        self.montantRembourse = QDoubleSpinBox()
        self.montantRembourse.setDecimals(2)
        self.montantRembourse.setMaximum(99999)
        self.montantRembourse.setSuffix(" € TTC")
        form.addRow("Montant remboursé", self.montantRembourse)

        self.fraisReexpedition = QDoubleSpinBox()
        self.fraisReexpedition.setDecimals(2)
        self.fraisReexpedition.setMaximum(9999)
        self.fraisReexpedition.setSuffix(" € HT")
        form.addRow(
            "Frais de réexpédition (si remplacement)",
            self.fraisReexpedition
        )

        self.coutRetour = QDoubleSpinBox()
        self.coutRetour.setDecimals(2)
        self.coutRetour.setMaximum(9999)
        self.coutRetour.setSuffix(" € HT")
        form.addRow(
            "Coût du retour (étiquette, perte produit...)",
            self.coutRetour
        )

        layout.addLayout(form)

        layout.addWidget(QLabel("Notes"))

        self.notes = QTextEdit()
        self.notes.setFixedHeight(80)
        layout.addWidget(self.notes)

        if donnees_existantes:

            index = self.produit.findText(
                donnees_existantes.get("produit_nom", "")
            )
            if index >= 0:
                self.produit.setCurrentIndex(index)

            if donnees_existantes.get("date_retour"):
                self.dateRetour.setDate(
                    QDate.fromString(
                        donnees_existantes["date_retour"], "yyyy-MM-dd"
                    )
                )

            self.motif.setText(donnees_existantes.get("motif", ""))

            index_statut = self.statut.findText(
                donnees_existantes.get("statut", "Demandé")
            )
            if index_statut >= 0:
                self.statut.setCurrentIndex(index_statut)

            self.montantRembourse.setValue(
                donnees_existantes.get("montant_rembourse_ttc", 0)
            )
            self.fraisReexpedition.setValue(
                donnees_existantes.get("frais_reexpedition_ht", 0)
            )
            self.coutRetour.setValue(
                donnees_existantes.get("cout_retour_ht", 0)
            )
            self.notes.setPlainText(donnees_existantes.get("notes", ""))

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