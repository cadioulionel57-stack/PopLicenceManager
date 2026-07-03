from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pop Licence Manager")
        self.resize(1600, 900)

        self.setStyleSheet("""
        QMainWindow{
            background:#edf3fa;
        }

        QWidget{
            font-family:Segoe UI;
            font-size:11pt;
        }

        QFrame{
            background:white;
            border-radius:12px;
        }

        QPushButton{
            background:#1d5ea8;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px;
            font-weight:bold;
        }

        QPushButton:hover{
            background:#2f78cc;
        }

        QLineEdit{
            border:1px solid #cccccc;
            border-radius:8px;
            padding:8px;
            background:white;
        }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        principal = QHBoxLayout(central)
        principal.setContentsMargins(15,15,15,15)
        principal.setSpacing(15)

        # MENU

        menu = QFrame()
        menu.setFixedWidth(250)

        menu_layout = QVBoxLayout(menu)

        logo = QLabel()
        pix = QPixmap("resources/images/logo.png")

        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(180))

        logo.setAlignment(Qt.AlignCenter)

        menu_layout.addWidget(logo)

        titre = QLabel("POP LICENCE\nMANAGER")
        titre.setAlignment(Qt.AlignCenter)

        titre.setStyleSheet("""
        font-size:18pt;
        font-weight:bold;
        color:#1d5ea8;
        """)

        menu_layout.addWidget(titre)

        boutons = [
    ("🏠", "Accueil"),
    ("📦", "Produits"),
    ("🚚", "Fournisseurs"),
    ("🛒", "Commandes"),
    ("📦", "Stock"),
    ("💰", "Tarification"),
    ("📈", "Ventes"),
    ("📊", "Statistiques"),
    ("💬", "SAV"),
    ("📣", "Marketing"),
    ("⚙", "Paramètres"),
]

        for icone, texte in boutons:

            b = QPushButton(f"  {icone}   {texte}")

            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(52)

            b.setStyleSheet("""
                QPushButton{
                    background:#1E5AA8;
                    color:white;
                    border:none;
                    border-radius:12px;
                    font-size:13pt;
                    font-weight:bold;
                    text-align:left;
                    padding-left:18px;
                }

                QPushButton:hover{
                    background:#2E73C8;
                }

                QPushButton:pressed{
                    background:#174C8C;
                }
            """)

        menu_layout.addWidget(b)

        menu_layout.addStretch()

        principal.addWidget(menu)
                # ZONE PRINCIPALE

        contenu = QWidget()
        contenu_layout = QVBoxLayout(contenu)
        contenu_layout.setSpacing(15)

        # BARRE DU HAUT

        haut = QFrame()
        haut_layout = QHBoxLayout(haut)

        titre = QLabel("Tableau de bord")
        titre.setStyleSheet("""
            font-size:24pt;
            font-weight:bold;
            color:#1d5ea8;
        """)

        recherche = QLineEdit()
        recherche.setPlaceholderText("🔍 Rechercher un produit, une commande, un fournisseur...")

        utilisateur = QLabel("👤 Yoon")

        haut_layout.addWidget(titre)
        haut_layout.addStretch()
        haut_layout.addWidget(recherche)
        haut_layout.addSpacing(15)
        haut_layout.addWidget(utilisateur)

        contenu_layout.addWidget(haut)

        # KPI

        grille = QGridLayout()

        def carte(titre, valeur):

            cadre = QFrame()

            v = QVBoxLayout(cadre)

            t = QLabel(titre)
            t.setStyleSheet("""
                color:#777777;
                font-size:12pt;
            """)

            val = QLabel(valeur)
            val.setStyleSheet("""
                font-size:22pt;
                font-weight:bold;
                color:#1d5ea8;
            """)

            v.addWidget(t)
            v.addWidget(val)

            return cadre

        grille.addWidget(carte("💰 CA du jour", "0 €"),0,0)
        grille.addWidget(carte("📅 CA du mois", "0 €"),0,1)
        grille.addWidget(carte("📈 Bénéfice", "0 €"),0,2)
        grille.addWidget(carte("🏦 Trésorerie", "0 €"),0,3)

        contenu_layout.addLayout(grille)
                # BAS DE PAGE

        bas = QHBoxLayout()

        # ALERTES

        alertes = QFrame()
        alertes_layout = QVBoxLayout(alertes)

        titre_alertes = QLabel("🚨 Alertes")
        titre_alertes.setStyleSheet("""
            font-size:18pt;
            font-weight:bold;
            color:#d35400;
        """)

        alertes_layout.addWidget(titre_alertes)

        liste = [
            "🟢 5 commandes à préparer",
            "🟠 3 produits à publier",
            "🔴 2 produits sous la marge minimum",
            "🔴 1 commande fournisseur en retard",
            "🟠 4 SAV à traiter",
        ]

        for ligne in liste:
            l = QLabel(ligne)
            l.setStyleSheet("font-size:12pt;padding:4px;")
            alertes_layout.addWidget(l)

        alertes_layout.addStretch()

        # ACTIVITÉ

        activite = QFrame()
        activite_layout = QVBoxLayout(activite)

        titre_act = QLabel("📅 Activité récente")
        titre_act.setStyleSheet("""
            font-size:18pt;
            font-weight:bold;
            color:#1d5ea8;
        """)

        activite_layout.addWidget(titre_act)

        historique = [
            "• Dernière vente : ---",
            "• Dernier achat : ---",
            "• Dernière synchronisation : ---",
            "• Dernière sauvegarde : ---",
        ]

        for ligne in historique:
            l = QLabel(ligne)
            l.setStyleSheet("font-size:12pt;padding:4px;")
            activite_layout.addWidget(l)

        activite_layout.addStretch()

        bas.addWidget(alertes,1)
        bas.addWidget(activite,1)

        contenu_layout.addLayout(bas)
        principal.addWidget(contenu, 1)