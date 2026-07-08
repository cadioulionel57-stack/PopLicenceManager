from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QFrame,
)

from modules.canal_manager import CanalManager


class DupliquerCategoriesDialog(QDialog):
    """
    Permet de recopier toutes les catégories (et leurs
    commissions/paliers) d'un canal source vers un canal
    cible — utile par exemple pour dupliquer Amazon FBM
    vers Amazon FBA sans tout ressaisir.
    """

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Dupliquer les catégories vers un autre canal")
        self.resize(480, 320)

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
                font-size:20px;
                font-weight:bold;
                color:#144b8b;
            }

            QLabel{
                color:#2d3436;
                font-size:11pt;
            }

            QComboBox{
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

        titre = QLabel("Dupliquer les catégories vers un autre canal")
        titre.setObjectName("titre")
        titre.setWordWrap(True)
        layout.addWidget(titre)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Toutes les catégories actives du canal source "
            "(avec leur commission et leurs éventuels "
            "paliers de prix) seront recopiées vers le "
            "canal cible."
        ))

        layout.addSpacing(15)

        canaux = CanalManager().tous()

        layout.addWidget(QLabel("Canal source (à copier)"))
        self.canalSource = QComboBox()
        for canal in canaux:
            self.canalSource.addItem(canal["nom"], canal["id"])
        layout.addWidget(self.canalSource)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Canal cible (destination)"))
        self.canalCible = QComboBox()
        for canal in canaux:
            self.canalCible.addItem(canal["nom"], canal["id"])
        layout.addWidget(self.canalCible)

        layout.addStretch()

        boutons = QHBoxLayout()
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnDupliquer = QPushButton("Dupliquer")

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnDupliquer)

        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnDupliquer.clicked.connect(self.accept)

    def canal_source_id(self):
        return self.canalSource.currentData()

    def canal_cible_id(self):
        return self.canalCible.currentData()