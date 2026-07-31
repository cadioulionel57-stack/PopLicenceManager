from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QHeaderView,
    QFrame,
)

from ui import theme


class ListPage(QWidget):
    """
    Base commune à tous les écrans de liste (Canaux, Grille
    de transport, Emballages, Fournisseurs, Commandes, SAV,
    Marques, Licences...) — un seul style à entretenir pour
    que tout le logiciel ait un rendu cohérent et pro.
    """

    def __init__(self, titre):

        super().__init__()

        # Le style de base vient du thème global
        # (ui/theme.py), appliqué au démarrage dans main.py.
        #
        # On y ajoute ici la couleur du module, déduite
        # automatiquement du titre de l'écran : titre,
        # en-tête de tableau, boutons et surlignage prennent
        # cette teinte. Aucun écran n'a besoin de déclarer
        # quoi que ce soit — il suffit qu'il porte son nom.
        self.accent = theme.accent_pour(titre)
        self.setStyleSheet(theme.feuille_accent(self.accent))

        principal = QVBoxLayout(self)
        principal.setContentsMargins(24, 20, 24, 20)
        principal.setSpacing(14)

        ####################################################
        # Titre
        ####################################################

        entete = QHBoxLayout()
        entete.setSpacing(12)

        # Repère coloré du module, à gauche du titre.
        bandeau = QFrame()
        bandeau.setObjectName("bandeauAccent")
        bandeau.setFixedWidth(6)
        bandeau.setMinimumHeight(34)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")

        entete.addWidget(bandeau)
        entete.addWidget(titreLabel)
        entete.addStretch()

        principal.addLayout(entete)

        ####################################################
        # Barre d'outils (carte séparée, plus lisible)
        ####################################################

        carteBarre = QFrame()
        carteBarre.setObjectName("barreOutils")

        barre = QHBoxLayout(carteBarre)
        barre.setContentsMargins(14, 10, 14, 10)
        barre.setSpacing(10)

        self.recherche = QLineEdit()
        self.recherche.setPlaceholderText("🔍  Rechercher...")

        # Sans largeur maximale, le champ de recherche prend
        # toute la place disponible et comprime les boutons :
        # Qt coupe alors leur libellé et il ne reste que
        # l'icône, illisible.
        self.recherche.setMinimumWidth(240)
        self.recherche.setMaximumWidth(360)

        self.btnAjouter = QPushButton("➕ Nouveau")
        self.btnModifier = QPushButton("✏ Modifier")
        self.btnModifier.setObjectName("btnSecondaire")
        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnSupprimer.setObjectName("btnSupprimer")
        self.btnImporter = QPushButton("📥 Import")
        self.btnImporter.setObjectName("btnSecondaire")
        self.btnExporter = QPushButton("📤 Export")
        self.btnExporter.setObjectName("btnSecondaire")

        # Les boutons gardent toujours leur largeur naturelle :
        # leur libellé ne sera jamais tronqué, même dans une
        # fenêtre étroite. C'est la barre qui défile plutôt que
        # le texte qui disparaît.
        for bouton in (
            self.btnAjouter,
            self.btnModifier,
            self.btnSupprimer,
            self.btnImporter,
            self.btnExporter,
        ):
            bouton.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed,
            )

        barre.addWidget(self.recherche)
        barre.addStretch()

        barre.addWidget(self.btnAjouter)
        barre.addWidget(self.btnModifier)
        barre.addWidget(self.btnSupprimer)
        barre.addWidget(self.btnImporter)
        barre.addWidget(self.btnExporter)

        principal.addWidget(carteBarre)

        ####################################################
        # Tableau (dans sa propre carte, pour un vrai relief
        # visuel par rapport au fond de la page)
        ####################################################

        carteTable = QFrame()
        carteTable.setObjectName("carteTable")

        layoutTable = QVBoxLayout(carteTable)
        layoutTable.setContentsMargins(2, 2, 2, 2)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        # Affichage aéré : des lignes hautes, plus lisibles
        # qu'un tableau dense où tout se touche.
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layoutTable.addWidget(self.table)

        principal.addWidget(carteTable)