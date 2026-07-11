from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

from modules.politique_transport_manager import (
    PolitiqueTransportManager
)


class PolitiqueTransportPage(QWidget):
    """
    Pense-bête en lecture seule : résume, canal par canal,
    la politique de frais de port mise en place (mécanisme,
    tarifs, seuils, frais de gestion).

    Pour modifier un réglage, ça reste l'écran "Canaux de
    vente" — cette page-ci ne fait que relire et présenter
    ce qui y est déjà configuré, en langage clair.
    """

    def __init__(self):

        super().__init__()

        self.manager = PolitiqueTransportManager()

        self.setStyleSheet("""
        QWidget{
            background:#edf3fa;
            font-family:'Segoe UI';
        }

        QLabel#titre{
            font-size:26px;
            font-weight:bold;
            color:#144b8b;
        }

        QGroupBox{
            background:white;
            border:1px solid #d7e3ef;
            border-radius:10px;
            margin-top:14px;
            font-weight:bold;
            font-size:13pt;
            color:#144b8b;
            padding-top:14px;
        }

        QGroupBox::title{
            subcontrol-origin:margin;
            left:14px;
            padding:0 6px;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px 20px;
        }

        QPushButton:hover{
            background:#1d61b4;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        entete = QHBoxLayout()

        titre = QLabel("🚚 Politique de frais de port par canal")
        titre.setObjectName("titre")
        entete.addWidget(titre)

        entete.addStretch()

        self.btnActualiser = QPushButton("🔄 Actualiser")
        self.btnActualiser.clicked.connect(self.charger)
        entete.addWidget(self.btnActualiser)

        layout.addLayout(entete)

        sousTitre = QLabel(
            "Résumé en lecture seule de ce qui est configuré "
            "pour chaque canal. Pour modifier un réglage, "
            "va dans \"Canaux de vente\"."
        )
        sousTitre.setStyleSheet("color:#5a6b7d;")
        sousTitre.setWordWrap(True)
        layout.addWidget(sousTitre)

        self.zoneDefilement = QScrollArea()
        self.zoneDefilement.setWidgetResizable(True)
        self.zoneDefilement.setStyleSheet("border:none;")

        self.conteneur = QWidget()
        self.layoutConteneur = QVBoxLayout(self.conteneur)
        self.layoutConteneur.setSpacing(14)

        self.zoneDefilement.setWidget(self.conteneur)

        layout.addWidget(self.zoneDefilement)

        self.charger()

    def charger(self):
        """
        Recharge et réaffiche la politique de tous les
        canaux — à appeler à chaque affichage de la page,
        car les réglages ont pu changer entre-temps.
        """

        # Vide le contenu précédent avant de le reconstruire
        while self.layoutConteneur.count():

            item = self.layoutConteneur.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        canaux = self.manager.tous()

        if not canaux:

            self.layoutConteneur.addWidget(
                QLabel("Aucun canal de vente configuré.")
            )
            return

        for canal in canaux:

            groupe = QGroupBox(
                f"{canal['nom']}  —  commission {canal['commission']:.1f}%"
            )

            layoutGroupe = QVBoxLayout(groupe)

            for ligne in canal["lignes"]:

                etiquette = QLabel(ligne)
                etiquette.setWordWrap(True)
                etiquette.setStyleSheet(
                    "font-weight:normal; font-size:11pt; "
                    "color:#2c3e50;"
                )
                layoutGroupe.addWidget(etiquette)

            self.layoutConteneur.addWidget(groupe)

        self.layoutConteneur.addStretch()