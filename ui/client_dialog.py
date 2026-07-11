from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QFormLayout,
)


class ClientDialog(QDialog):
    """
    Fenêtre de création/modification d'un client.
    """

    def __init__(
        self,
        titre,
        nom="",
        prenom="",
        societe="",
        email="",
        telephone="",
        adresse="",
        code_postal="",
        ville="",
        pays="France"
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(600, 580)

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

            QLineEdit{
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

        self.nom = QLineEdit()
        self.nom.setText(nom)
        form.addRow("Nom", self.nom)

        self.prenom = QLineEdit()
        self.prenom.setText(prenom)
        form.addRow("Prénom", self.prenom)

        self.societe = QLineEdit()
        self.societe.setText(societe)
        form.addRow("Société", self.societe)

        self.email = QLineEdit()
        self.email.setText(email)
        form.addRow("Email", self.email)

        self.telephone = QLineEdit()
        self.telephone.setText(telephone)
        form.addRow("Téléphone", self.telephone)

        self.adresse = QLineEdit()
        self.adresse.setText(adresse)
        form.addRow("Adresse", self.adresse)

        self.codePostal = QLineEdit()
        self.codePostal.setText(code_postal)
        form.addRow("Code postal", self.codePostal)

        self.ville = QLineEdit()
        self.ville.setText(ville)
        form.addRow("Ville", self.ville)

        self.pays = QLineEdit()
        self.pays.setText(pays)
        form.addRow("Pays", self.pays)

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