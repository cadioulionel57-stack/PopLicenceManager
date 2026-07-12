from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QPushButton,
    QFrame,
    QFormLayout,
)


class ModeleFicheDialog(QDialog):
    """
    Fenêtre de création/modification d'un modèle de fiche
    produit (charte HTML) — colle le code HTML tel quel,
    avec les variables {{nom_produit}}, {{avec_licence}},
    {{prix_emballage_cadeau}}, {{tarif_livraison_df}},
    {{seuil_livraison_gratuite_stock}},
    {{seuil_livraison_gratuite_df}}.
    """

    TYPES_PRODUIT = [
        ("Produit en stock", "stock"),
        ("Direct Fournisseur", "dropshipping"),
    ]

    def __init__(
        self, titre, themes, nom="", theme_id=None,
        type_produit="stock", html_template="",
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(900, 700)

        self.setStyleSheet("""
            QDialog{ background:#f4f7fb; font-family:"Segoe UI"; }
            QFrame#card{ background:white; border:1px solid #e1e8f0; border-radius:12px; }
            QLabel#titre{ font-size:20px; font-weight:600; color:#0f2f5c; }
            QLineEdit, QComboBox, QTextEdit{
                background:#f7f9fc; border:1px solid #d7e0ec;
                border-radius:7px; padding:8px; font-size:10.5pt;
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
        self.nom.setPlaceholderText(
            "Ex : Textile Stock — Normal, Textile Stock — Noël..."
        )
        self.nom.setText(nom)
        form.addRow("Nom du modèle", self.nom)

        self.themeTemplate = QComboBox()
        for theme in themes:
            self.themeTemplate.addItem(theme["nom"], theme["id"])

        index = self.themeTemplate.findData(theme_id)
        if index != -1:
            self.themeTemplate.setCurrentIndex(index)

        form.addRow("Thème", self.themeTemplate)

        self.typeProduit = QComboBox()
        for libelle, valeur in self.TYPES_PRODUIT:
            self.typeProduit.addItem(libelle, valeur)

        index_type = self.typeProduit.findData(type_produit)
        if index_type != -1:
            self.typeProduit.setCurrentIndex(index_type)

        form.addRow("Type de produit", self.typeProduit)

        layout.addLayout(form)

        info = QLabel(
            "Variables disponibles : {{nom_produit}}, {{avec_licence}} "
            "(ajoute automatiquement \" sous licence X\" si le produit "
            "a une licence, sinon rien), {{prix_emballage_cadeau}}, "
            "{{tarif_livraison_df}}, {{seuil_livraison_gratuite_stock}}, "
            "{{seuil_livraison_gratuite_df}}."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#5a6b7d; font-size:9pt;")
        layout.addWidget(info)

        layout.addWidget(QLabel("Code HTML"))

        self.htmlTemplate = QTextEdit()
        self.htmlTemplate.setPlainText(html_template)
        self.htmlTemplate.setStyleSheet(
            "font-family:Consolas,monospace; font-size:9.5pt;"
        )
        layout.addWidget(self.htmlTemplate)

        boutons = QHBoxLayout()
        boutons.addStretch()
        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")
        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)
        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)