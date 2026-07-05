from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QCheckBox,
)


class EntityDialog(QDialog):

    def __init__(
        self,
        titre,
        nom="",
        description="",
        actif=True
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(700, 500)

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

            QLineEdit,
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

        layout.addSpacing(15)

        layout.addWidget(QLabel("Nom"))

        self.nom = QLineEdit()
        self.nom.setText(nom)

        layout.addWidget(self.nom)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Description"))

        self.description = QTextEdit()
        self.description.setPlainText(description)
        self.description.setFixedHeight(120)

        layout.addWidget(self.description)

        layout.addSpacing(10)

        self.actif = QCheckBox("Élément actif")
        self.actif.setChecked(actif)

        layout.addWidget(self.actif)

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