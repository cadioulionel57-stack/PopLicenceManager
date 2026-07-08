from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
)


class GrilleFbaDialog(QDialog):

    def __init__(
        self,
        titre,
        format_colis="",
        categorie_speciale="",
        longueur_max_cm=0.0,
        largeur_max_cm=0.0,
        hauteur_max_cm=0.0,
        poids_seuil_g=100.0,
        prix_base_ht=0.0,
        prix_supplement_ht=0.0,
        supplement_pas_g=100.0,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(480, 620)

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
            "Nom du format (ex : Petit colis 1, Colis "
            "moyen 2, Grand colis 1...)"
        ))
        self.formatColis = QLineEdit()
        self.formatColis.setText(format_colis)
        layout.addWidget(self.formatColis)

        layout.addSpacing(8)

        layout.addWidget(QLabel(
            "Catégorie spéciale (laisser vide = grille "
            "standard, valable pour toutes les catégories "
            "sans tarif dédié)"
        ))
        self.categorieSpeciale = QLineEdit()
        self.categorieSpeciale.setText(categorie_speciale or "")
        layout.addWidget(self.categorieSpeciale)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Dimensions maximales de la boîte (cm)"))

        dims = QHBoxLayout()

        self.longueurMax = QDoubleSpinBox()
        self.longueurMax.setMaximum(999)
        self.longueurMax.setPrefix("L: ")
        self.longueurMax.setValue(longueur_max_cm)

        self.largeurMax = QDoubleSpinBox()
        self.largeurMax.setMaximum(999)
        self.largeurMax.setPrefix("l: ")
        self.largeurMax.setValue(largeur_max_cm)

        self.hauteurMax = QDoubleSpinBox()
        self.hauteurMax.setMaximum(999)
        self.hauteurMax.setPrefix("h: ")
        self.hauteurMax.setValue(hauteur_max_cm)

        dims.addWidget(self.longueurMax)
        dims.addWidget(self.largeurMax)
        dims.addWidget(self.hauteurMax)

        layout.addLayout(dims)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Poids inclus dans le prix de base (g)"))
        self.poidsSeuil = QDoubleSpinBox()
        self.poidsSeuil.setMaximum(99999)
        self.poidsSeuil.setSuffix(" g")
        self.poidsSeuil.setValue(poids_seuil_g)
        layout.addWidget(self.poidsSeuil)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Prix de base HT (pour ce poids inclus)"))
        self.prixBase = QDoubleSpinBox()
        self.prixBase.setDecimals(2)
        self.prixBase.setMaximum(999)
        self.prixBase.setSuffix(" €")
        self.prixBase.setValue(prix_base_ht)
        layout.addWidget(self.prixBase)

        layout.addSpacing(8)

        layout.addWidget(QLabel(
            "Supplément HT par tranche de poids au-delà du seuil"
        ))
        self.prixSupplement = QDoubleSpinBox()
        self.prixSupplement.setDecimals(2)
        self.prixSupplement.setMaximum(99)
        self.prixSupplement.setSuffix(" €")
        self.prixSupplement.setValue(prix_supplement_ht)
        layout.addWidget(self.prixSupplement)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Taille de la tranche de poids (g)"))
        self.supplementPas = QDoubleSpinBox()
        self.supplementPas.setMaximum(9999)
        self.supplementPas.setSuffix(" g")
        self.supplementPas.setValue(supplement_pas_g)
        layout.addWidget(self.supplementPas)

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

    def categorie_speciale_texte(self):

        texte = self.categorieSpeciale.text().strip()

        return texte if texte != "" else None