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

from modules.emballage_manager import EmballageManager


class FamilleProduitDialog(QDialog):

    def __init__(
        self,
        titre,
        nom="",
        cout_emballage_ht=0.0,
        taux_retour=0.0,
        emballage_id=None,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(480, 480)

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

        layout.addWidget(QLabel(
            "Nom de la famille (ex : Textile & Mode, "
            "Chaussures, Jeux & Jouets...)"
        ))

        self.nom = QLineEdit()
        self.nom.setText(nom)
        layout.addWidget(self.nom)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Emballage utilisé (le coût est calculé "
            "automatiquement depuis la grille d'emballage)"
        ))

        self.emballage = QComboBox()
        self.emballage.addItem(
            "— Aucun (saisir un coût manuel ci-dessous) —",
            None
        )

        for emb in EmballageManager().tous():
            self.emballage.addItem(
                f"{emb['code']} — {emb['nom']}",
                emb["id"]
            )

        index = self.emballage.findData(emballage_id)
        if index != -1:
            self.emballage.setCurrentIndex(index)

        self.emballage.currentIndexChanged.connect(
            self._actualiserDisponibiliteCoutManuel
        )

        layout.addWidget(self.emballage)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Coût d'emballage manuel (HT) — utilisé "
            "uniquement si aucun emballage n'est sélectionné"
        ))

        self.coutEmballage = QDoubleSpinBox()
        self.coutEmballage.setDecimals(2)
        self.coutEmballage.setMaximum(999)
        self.coutEmballage.setSuffix(" €")
        self.coutEmballage.setValue(cout_emballage_ht)
        layout.addWidget(self.coutEmballage)

        self._actualiserDisponibiliteCoutManuel()

        layout.addSpacing(10)

        layout.addWidget(QLabel("Taux de retour"))

        self.tauxRetour = QDoubleSpinBox()
        self.tauxRetour.setDecimals(2)
        self.tauxRetour.setMaximum(100)
        self.tauxRetour.setSuffix(" %")
        self.tauxRetour.setValue(taux_retour * 100)
        layout.addWidget(self.tauxRetour)

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

    def _actualiserDisponibiliteCoutManuel(self):
        """
        Le coût manuel ne sert que si aucun emballage
        n'est sélectionné dans la grille.
        """

        self.coutEmballage.setEnabled(
            self.emballage.currentData() is None
        )

    def emballage_id_selectionne(self):
        return self.emballage.currentData()

    def taux_retour_decimal(self):
        """
        Le champ affiche un pourcentage (ex : 18), mais
        on stocke et on calcule avec une valeur décimale
        (ex : 0.18).
        """
        return self.tauxRetour.value() / 100