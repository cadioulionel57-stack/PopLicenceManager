"""
Thème visuel unique de PopLicenceManager.

Tout le style du logiciel est défini ici, et appliqué une
seule fois au démarrage dans main.py. Les écrans n'ont plus à
redéfinir leurs couleurs : ils héritent d'ici.

Pour changer l'apparence de tout le logiciel — une couleur,
un arrondi, une taille de police — il suffit de modifier ce
fichier. Rien d'autre.
"""


# ==========================================================
# PALETTE
#
# Reprend l'identité Pop Licence : bleu marine et bleu roi,
# avec le jaune du site en couleur d'accent.
# ==========================================================

MARINE = "#0f2f5c"      # titres, en-têtes de tableau
BLEU = "#144b8b"        # boutons principaux, focus
BLEU_CLAIR = "#1d61b4"  # survol
BLEU_FONCE = "#0d3a6e"  # bouton enfoncé

OR = "#f0a500"          # accent : sélection, badges
OR_CLAIR = "#fbbf24"

VERT = "#1e7d32"
ORANGE = "#e67e22"
ROUGE = "#c0392b"

FOND = "#eef2f8"        # fond général de l'application
CARTE = "#ffffff"       # cartes, tableaux, formulaires
CHAMP = "#f7f9fc"       # champs de saisie au repos

BORDURE = "#dbe3ee"
BORDURE_DOUCE = "#eef1f6"

TEXTE = "#1c2b3a"
TEXTE_DOUX = "#64748b"
TEXTE_INVERSE = "#ffffff"

POLICE = "'Segoe UI', 'Inter', Arial"


FEUILLE_DE_STYLE = f"""

/* ====================================================== */
/* BASE                                                    */
/* ====================================================== */

QWidget {{
    background: {FOND};
    color: {TEXTE};
    font-family: {POLICE};
    font-size: 10pt;
}}

QMainWindow, QDialog {{
    background: {FOND};
}}

/* ====================================================== */
/* TITRES ET CARTES                                        */
/* ====================================================== */

QLabel#titre {{
    font-size: 23px;
    font-weight: 700;
    color: {MARINE};
    padding: 2px 0px;
}}

QLabel#sousTitre {{
    font-size: 12px;
    color: {TEXTE_DOUX};
}}

QFrame#barreOutils {{
    background: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 12px;
}}

QFrame#carteTable, QFrame#card {{
    background: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 14px;
}}

/* ====================================================== */
/* BOUTONS                                                 */
/* ====================================================== */

QPushButton {{
    background: {BLEU};
    color: {TEXTE_INVERSE};
    border: none;
    border-radius: 9px;
    padding: 9px 14px;
    font-size: 9.5pt;
    font-weight: 600;
}}

QPushButton:hover {{
    background: {BLEU_CLAIR};
}}

QPushButton:pressed {{
    background: {BLEU_FONCE};
    padding-top: 11px;
    padding-bottom: 9px;
}}

QPushButton:disabled {{
    background: #c7d2e0;
    color: #eef2f8;
}}

QPushButton#btnSupprimer {{
    background: {ROUGE};
}}

QPushButton#btnSupprimer:hover {{
    background: #d9483a;
}}

QPushButton#btnSecondaire {{
    background: {CARTE};
    color: {BLEU};
    border: 1.5px solid {BORDURE};
}}

QPushButton#btnSecondaire:hover {{
    background: #e8effa;
    border-color: {BLEU};
}}

QPushButton#btnAccent {{
    background: {OR};
    color: {MARINE};
}}

QPushButton#btnAccent:hover {{
    background: {OR_CLAIR};
}}

/* ====================================================== */
/* CHAMPS DE SAISIE                                        */
/* ====================================================== */

QLineEdit, QTextEdit, QPlainTextEdit,
QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background: {CHAMP};
    border: 1.5px solid {BORDURE};
    border-radius: 9px;
    padding: 9px 12px;
    color: {TEXTE};
    selection-background-color: {BLEU};
    selection-color: {TEXTE_INVERSE};
}}

QLineEdit:hover, QComboBox:hover, QDateEdit:hover,
QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: #c3d2e6;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QComboBox:focus, QDateEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {BLEU};
    background: {CARTE};
}}

QLineEdit:disabled, QComboBox:disabled,
QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background: #f0f2f6;
    color: #9aa7b5;
}}

QLineEdit[readOnly="true"] {{
    background: #f0f2f6;
    color: {TEXTE_DOUX};
}}

/* Listes déroulantes */

QComboBox::drop-down {{
    border: none;
    width: 26px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {BLEU};
    width: 0;
    height: 0;
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #e8effa;
    selection-color: {MARINE};
    outline: none;
}}

/* Compteurs numériques et dates */

QSpinBox::up-button, QDoubleSpinBox::up-button,
QDateEdit::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {BORDURE};
    border-top-right-radius: 8px;
    background: #e8eef7;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button,
QDateEdit::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid {BORDURE};
    border-bottom-right-radius: 8px;
    background: #e8eef7;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QDateEdit::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover,
QDateEdit::down-button:hover {{
    background: #d5e2f4;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow,
QDateEdit::up-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {BLEU};
    width: 0; height: 0;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow,
QDateEdit::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {BLEU};
    width: 0; height: 0;
}}

/* ====================================================== */
/* TABLEAUX                                                */
/* ====================================================== */

QTableWidget, QTableView {{
    background: {CARTE};
    border: none;
    border-radius: 12px;
    gridline-color: {BORDURE_DOUCE};
    selection-background-color: #dbe7f7;
    selection-color: {MARINE};
    alternate-background-color: #f8fafc;
    padding: 2px;
}}

/* IMPORTANT — aucune règle sur ::item ici.
   Dès qu'une feuille de style touche à QTableWidget::item,
   Qt dessine les cellules lui-même et IGNORE les couleurs
   posées dans le code par setBackground()/setForeground().
   Des colonnes comme « Décision » dans l'onglet Tarification,
   qui écrivent en blanc sur fond vert, rouge ou orange,
   deviennent alors illisibles : le texte blanc reste, le fond
   coloré disparaît.
   La hauteur des lignes est réglée dans le code
   (setDefaultSectionSize), pas ici. */

/* Champs de saisie posés DANS une cellule de tableau
   (setCellWidget) : sans cette règle ils héritent de la
   palette du tableau et leur texte ressort délavé, presque
   illisible — cas des colonnes « Marge » et « Prix marché
   constaté » de l'onglet Tarification. */

QTableWidget QLineEdit, QTableWidget QSpinBox,
QTableWidget QDoubleSpinBox, QTableWidget QComboBox,
QTableView QLineEdit, QTableView QSpinBox,
QTableView QDoubleSpinBox, QTableView QComboBox {{
    background: {CARTE};
    color: {TEXTE};
    border: 1.5px solid {BORDURE};
    border-radius: 7px;
    padding: 4px 8px;
    font-weight: 600;
}}

QTableWidget QLineEdit:focus, QTableWidget QSpinBox:focus,
QTableWidget QDoubleSpinBox:focus, QTableWidget QComboBox:focus {{
    border: 1.5px solid {BLEU};
}}

QHeaderView::section {{
    background: {MARINE};
    color: {TEXTE_INVERSE};
    border: none;
    border-right: 1px solid #24467a;
    padding: 14px 10px;
    font-weight: 700;
    font-size: 9.5pt;
    letter-spacing: 0.3px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 12px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 12px;
    border-right: none;
}}

QTableCornerButton::section {{
    background: {MARINE};
    border: none;
}}

/* ====================================================== */
/* BARRES DE DÉFILEMENT                                    */
/* ====================================================== */

QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 4px 2px;
}}

QScrollBar::handle:vertical {{
    background: #c3d0e0;
    border-radius: 5px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background: {BLEU};
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 12px;
    margin: 2px 4px;
}}

QScrollBar::handle:horizontal {{
    background: #c3d0e0;
    border-radius: 5px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {BLEU};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0; width: 0; border: none; background: none;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

/* ====================================================== */
/* CASES À COCHER                                          */
/* ====================================================== */

QCheckBox {{
    spacing: 9px;
    color: {TEXTE};
}}

QCheckBox::indicator {{
    width: 19px;
    height: 19px;
    border: 1.5px solid {BORDURE};
    border-radius: 6px;
    background: {CARTE};
}}

QCheckBox::indicator:hover {{
    border-color: {BLEU};
}}

QCheckBox::indicator:checked {{
    background: {BLEU};
    border-color: {BLEU};
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid {BORDURE};
    border-radius: 9px;
    background: {CARTE};
}}

QRadioButton::indicator:checked {{
    background: {BLEU};
    border: 5px solid {CARTE};
}}

/* ====================================================== */
/* ENCADRÉS ET ONGLETS                                     */
/* ====================================================== */

QGroupBox {{
    background: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px 14px 12px 14px;
    font-weight: 700;
    color: {MARINE};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    background: {CARTE};
}}

QTabWidget::pane {{
    background: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 12px;
    top: -1px;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXTE_DOUX};
    padding: 10px 20px;
    margin-right: 4px;
    border: none;
    border-bottom: 3px solid transparent;
    font-weight: 600;
}}

QTabBar::tab:hover {{
    color: {BLEU};
}}

QTabBar::tab:selected {{
    color: {MARINE};
    border-bottom: 3px solid {OR};
}}

/* ====================================================== */
/* DIVERS                                                  */
/* ====================================================== */

QToolTip {{
    background: {MARINE};
    color: {TEXTE_INVERSE};
    border: none;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 9.5pt;
}}

QMessageBox {{
    background: {CARTE};
}}

QMessageBox QPushButton {{
    min-width: 92px;
}}

QProgressBar {{
    background: {CHAMP};
    border: 1px solid {BORDURE};
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {MARINE};
    font-weight: 600;
}}

QProgressBar::chunk {{
    background: {BLEU};
    border-radius: 7px;
}}

QSplitter::handle {{
    background: {BORDURE};
}}

QMenu {{
    background: {CARTE};
    border: 1px solid {BORDURE};
    border-radius: 10px;
    padding: 6px;
}}

QMenu::item {{
    padding: 8px 24px 8px 14px;
    border-radius: 7px;
}}

QMenu::item:selected {{
    background: #e8effa;
    color: {MARINE};
}}
"""


# ==========================================================
# UNE COULEUR PAR MODULE
#
# Chaque écran a sa teinte : titre, en-tête de tableau,
# bouton principal et repère dans le menu. On reconnaît donc
# l'écran où l'on se trouve d'un simple coup d'œil, sans
# lire le titre.
#
# La liste est ORDONNÉE : le premier mot-clé trouvé gagne.
# « Achats Stocks » doit donc passer avant « Stock », et
# « Familles de produit » avant « Produits ».
# ==========================================================

ACCENTS = [
    (("tableau de bord", "accueil"), "#4f46e5"),
    (("famille",),                    "#0e7490"),
    (("achats stock",),               "#15803d"),
    (("stock",),                      "#16a34a"),
    (("produit",),                    "#1d4ed8"),
    (("licence",),                    "#7c3aed"),
    (("marque",),                     "#9333ea"),
    (("catégorie", "categorie"),      "#0891b2"),
    (("fba",),                        "#d97706"),
    (("emballages cadeau", "cadeau"), "#db2777"),
    (("emballage",),                  "#a16207"),
    (("frais de port", "politique"),  "#c2410c"),
    (("transport",),                  "#ea580c"),
    (("fournisseur",),                "#475569"),
    (("commande",),                   "#2563eb"),
    (("sav", "retour"),               "#dc2626"),
    (("trésorerie", "tresorerie"),    "#059669"),
    (("publicité", "publicite", "budget"), "#c026d3"),
    (("statistique",),                "#4338ca"),
    (("canaux", "canal"),             "#0284c7"),
    (("paramètre", "parametre"),      "#64748b"),
]

ACCENT_DEFAUT = BLEU


def accent_pour(titre):
    """
    Couleur du module, déduite de son titre. Aucun écran n'a
    besoin de la déclarer : il suffit qu'il porte son nom.
    """

    minuscules = (titre or "").lower()

    for mots, couleur in ACCENTS:
        for mot in mots:
            if mot in minuscules:
                return couleur

    return ACCENT_DEFAUT


def _eclaircir(couleur, taux=0.18):
    """
    Version plus claire d'une couleur, pour les survols.
    """

    couleur = couleur.lstrip("#")

    composantes = [
        int(couleur[i:i + 2], 16) for i in (0, 2, 4)
    ]

    composantes = [
        min(255, int(c + (255 - c) * taux)) for c in composantes
    ]

    return "#%02x%02x%02x" % tuple(composantes)


def _assombrir(couleur, taux=0.20):

    couleur = couleur.lstrip("#")

    composantes = [
        int(couleur[i:i + 2], 16) for i in (0, 2, 4)
    ]

    composantes = [max(0, int(c * (1 - taux))) for c in composantes]

    return "#%02x%02x%02x" % tuple(composantes)


def feuille_accent(accent):
    """
    Petite feuille de style à poser sur un écran pour le
    teinter de sa couleur. Le reste (champs, cases, barres de
    défilement) continue de venir du thème global.
    """

    clair = _eclaircir(accent)
    fonce = _assombrir(accent)

    return f"""

    QLabel#titre {{
        color: {accent};
    }}

    QFrame#bandeauAccent {{
        background: {accent};
        border: none;
        border-radius: 3px;
    }}

    QHeaderView::section {{
        background: {accent};
        border-right: 1px solid {clair};
    }}

    QTableCornerButton::section {{
        background: {accent};
    }}

    QTableWidget, QTableView {{
        selection-background-color: {_eclaircir(accent, 0.82)};
        selection-color: {fonce};
    }}

    QPushButton {{
        background: {accent};
    }}

    QPushButton:hover {{
        background: {clair};
    }}

    QPushButton:pressed {{
        background: {fonce};
    }}

    QPushButton#btnSecondaire {{
        background: {CARTE};
        color: {accent};
        border: 1.5px solid {BORDURE};
    }}

    QPushButton#btnSecondaire:hover {{
        background: {_eclaircir(accent, 0.9)};
        border-color: {accent};
    }}

    QPushButton#btnSupprimer {{
        background: {ROUGE};
    }}

    QPushButton#btnSupprimer:hover {{
        background: #d9483a;
    }}

    QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1.5px solid {accent};
    }}
    """


def appliquer(application):
    """
    Applique le thème à toute l'application. À appeler une
    seule fois, juste après la création du QApplication.
    """

    application.setStyleSheet(FEUILLE_DE_STYLE)