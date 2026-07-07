from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
)

from modules.canal_manager import CanalManager


class CategorieDialog(QDialog):

    def __init__(
        self,
        titre,
        nom="",
        canal_id=None,
        commission_pourcentage=None,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(480, 420)

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

        layout.addWidget(QLabel("Nom de la catégorie"))

        self.nom = QLineEdit()
        self.nom.setText(nom)
        layout.addWidget(self.nom)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Rattachée à (laisser vide = catégorie "
            "interne Pop Licence)"
        ))

        self.canal = QComboBox()
        self.canal.addItem(
            "— Catégorie interne Pop Licence —",
            None
        )

        self.canaux = CanalManager().tous()

        for canal in self.canaux:
            self.canal.addItem(canal["nom"], canal["id"])

        index = self.canal.findData(canal_id)
        if index != -1:
            self.canal.setCurrentIndex(index)

        layout.addWidget(self.canal)

        layout.addSpacing(10)

        ####################################################
        # Commission spécifique à cette catégorie
        ####################################################
        #
        # Ne concerne que les catégories rattachées à un
        # canal (une catégorie interne Pop Licence n'a pas
        # de commission de vente). Si la case n'est pas
        # cochée, c'est la commission par défaut du canal
        # qui s'applique automatiquement.
        #
        ####################################################

        self.commissionSpecifique = QCheckBox(
            "Commission spécifique à cette catégorie "
            "(sinon, celle du canal s'applique)"
        )

        layout.addWidget(self.commissionSpecifique)

        self.commission = QDoubleSpinBox()
        self.commission.setDecimals(2)
        self.commission.setMaximum(100)
        self.commission.setSuffix(" %")

        layout.addWidget(self.commission)

        if commission_pourcentage is not None:
            self.commissionSpecifique.setChecked(True)
            self.commission.setValue(commission_pourcentage)

        self.commissionSpecifique.toggled.connect(
            self.commission.setEnabled
        )

        self.canal.currentIndexChanged.connect(
            self._actualiserDisponibiliteCommission
        )

        self._actualiserDisponibiliteCommission()

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

    def _actualiserDisponibiliteCommission(self):
        """
        Désactive le réglage de commission si la
        catégorie est interne à Pop Licence (aucun
        canal sélectionné) : une commission n'a de
        sens que pour une catégorie de canal de vente.
        """

        est_liee_a_un_canal = self.canal.currentData() is not None

        self.commissionSpecifique.setEnabled(est_liee_a_un_canal)

        if not est_liee_a_un_canal:
            self.commissionSpecifique.setChecked(False)

        self.commission.setEnabled(
            est_liee_a_un_canal
            and self.commissionSpecifique.isChecked()
        )

    def canal_id(self):
        return self.canal.currentData()

    def commission_pourcentage(self):

        if not self.commissionSpecifique.isChecked():
            return None

        return self.commission.value()