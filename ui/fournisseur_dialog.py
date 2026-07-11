from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QScrollArea,
    QWidget,
)


class FournisseurDialog(QDialog):
    """
    Fenêtre de création/modification d'un fournisseur :
    coordonnées + conditions commerciales (seuil minimum de
    commande, franco de port, frais de port, conditions de
    règlement, délai de livraison).
    """

    def __init__(
        self,
        titre,
        nom="",
        contact="",
        telephone="",
        email="",
        site="",
        seuil_minimum_commande=None,
        franco_port=None,
        frais_port=None,
        conditions_reglement="",
        delai_livraison="",
        actif=True
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(750, 720)

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
                font-size:24px;
                font-weight:bold;
                color:#144b8b;
            }

            QLabel{
                color:#2d3436;
                font-size:11pt;
            }

            QGroupBox{
                font-weight:bold;
                color:#144b8b;
                border:1px solid #d8e1ed;
                border-radius:8px;
                margin-top:10px;
                padding-top:10px;
            }

            QGroupBox::title{
                subcontrol-origin:margin;
                left:10px;
                padding:0 6px;
            }

            QLineEdit,
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

        layoutCarte = QVBoxLayout(carte)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")

        layoutCarte.addWidget(titreLabel)

        ####################################################
        # Zone défilante (formulaire assez long)
        ####################################################

        zoneDefilement = QScrollArea()
        zoneDefilement.setWidgetResizable(True)
        zoneDefilement.setStyleSheet("border:none;")

        contenu = QWidget()
        layout = QVBoxLayout(contenu)

        ####################################################
        # Coordonnées
        ####################################################

        groupeCoordonnees = QGroupBox("Coordonnées")
        formCoordonnees = QFormLayout(groupeCoordonnees)

        self.nom = QLineEdit()
        self.nom.setText(nom)
        formCoordonnees.addRow("Nom du fournisseur", self.nom)

        self.contact = QLineEdit()
        self.contact.setText(contact)
        formCoordonnees.addRow("Contact", self.contact)

        self.telephone = QLineEdit()
        self.telephone.setText(telephone)
        formCoordonnees.addRow("Téléphone", self.telephone)

        self.email = QLineEdit()
        self.email.setText(email)
        formCoordonnees.addRow("Email", self.email)

        self.site = QLineEdit()
        self.site.setText(site)
        formCoordonnees.addRow("Site web", self.site)

        layout.addWidget(groupeCoordonnees)

        ####################################################
        # Conditions commerciales
        ####################################################

        groupeConditions = QGroupBox("Conditions commerciales")
        formConditions = QFormLayout(groupeConditions)

        self.seuilMinimumCommande = QDoubleSpinBox()
        self.seuilMinimumCommande.setDecimals(2)
        self.seuilMinimumCommande.setMaximum(99999)
        self.seuilMinimumCommande.setSuffix(" € HT")
        self.seuilMinimumCommande.setValue(
            seuil_minimum_commande or 0
        )
        formConditions.addRow(
            "Seuil minimum de commande", self.seuilMinimumCommande
        )

        self.francoPort = QDoubleSpinBox()
        self.francoPort.setDecimals(2)
        self.francoPort.setMaximum(99999)
        self.francoPort.setSuffix(" € HT")
        self.francoPort.setValue(franco_port or 0)
        formConditions.addRow(
            "Franco de port à partir de", self.francoPort
        )

        self.fraisPort = QDoubleSpinBox()
        self.fraisPort.setDecimals(2)
        self.fraisPort.setMaximum(9999)
        self.fraisPort.setSuffix(" € HT")
        self.fraisPort.setValue(frais_port or 0)
        formConditions.addRow(
            "Frais de port si sous le franco", self.fraisPort
        )

        self.conditionsReglement = QLineEdit()
        self.conditionsReglement.setPlaceholderText(
            "Ex : 30 jours fin de mois, comptant, 50% acompte..."
        )
        self.conditionsReglement.setText(conditions_reglement)
        formConditions.addRow(
            "Conditions de règlement", self.conditionsReglement
        )

        self.delaiLivraison = QLineEdit()
        self.delaiLivraison.setPlaceholderText(
            "Ex : 15-20 jours, 3 semaines..."
        )
        self.delaiLivraison.setText(delai_livraison)
        formConditions.addRow(
            "Délai de livraison", self.delaiLivraison
        )

        layout.addWidget(groupeConditions)

        self.actif = QCheckBox("Fournisseur actif")
        self.actif.setChecked(actif)

        layout.addWidget(self.actif)

        layout.addStretch()

        zoneDefilement.setWidget(contenu)

        layoutCarte.addWidget(zoneDefilement)

        ####################################################
        # Boutons
        ####################################################

        boutons = QHBoxLayout()

        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layoutCarte.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)