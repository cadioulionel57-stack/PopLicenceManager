from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QLineEdit,
    QComboBox,
    QLabel,
)

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.canal_manager import CanalManager
from modules.emballage_manager import EmballageManager


class CaracteristiquesTab(QWidget):

    def __init__(self, type_produit=None):

        super().__init__()

        self.type_produit = type_produit

        self.emballageManager = EmballageManager()

        layout = QVBoxLayout(self)

        ####################################################
        # Famille de produit (coût)
        ####################################################
        #
        # Détermine le coût d'emballage et le taux de
        # retour utilisés pour calculer le coût de revient
        # (identique quel que soit le canal de vente).
        #
        ####################################################

        familleGroupe = QGroupBox("🏭 Famille de produit (coût)")

        formFamille = QFormLayout(familleGroupe)

        self.familleProduit = ReferenceComboBox("familles_produit")

        formFamille.addRow(
            "Famille de produit",
            self.familleProduit
        )

        layout.addWidget(familleGroupe)

        ####################################################
        # Catégories
        ####################################################
        #
        # Une ligne par canal de vente actif (dynamique,
        # dépend entièrement de ce qui existe dans
        # "Canaux de vente" : rien n'est codé en dur ici).
        #
        ####################################################

        categorie = QGroupBox("📂 Catégories")

        self.formCategories = QFormLayout(categorie)

        # Une ligne par canal de vente actif, créée
        # automatiquement. self.categoriesCanaux garde
        # le lien {canal_id: menu déroulant} pour pouvoir
        # ensuite lire/enregistrer les choix faits.
        self.categoriesCanaux = {}

        self._chargerCategoriesCanaux()

        layout.addWidget(categorie)

        ####################################################
        # Dimensions
        ####################################################

        dimensions = QGroupBox("📦 Dimensions")

        form2 = QFormLayout(dimensions)

        self.longueur = QDoubleSpinBox()
        self.largeur = QDoubleSpinBox()
        self.hauteur = QDoubleSpinBox()
        self.poids = QDoubleSpinBox()

        for champ in (
            self.longueur,
            self.largeur,
            self.hauteur,
            self.poids,
        ):
            champ.setDecimals(2)
            champ.setMaximum(9999)

        form2.addRow("Longueur (cm)", self.longueur)
        form2.addRow("Largeur (cm)", self.largeur)
        form2.addRow("Hauteur (cm)", self.hauteur)
        form2.addRow("Poids (kg)", self.poids)

        layout.addWidget(dimensions)

        ####################################################
        # Dimensions d'expédition (carton plié)
        ####################################################
        #
        # Pour les articles pliables (textile...), la taille
        # du carton d'expédition est différente de la taille
        # du produit déplié ci-dessus. Laisser à 0 pour les
        # objets rigides : les dimensions du produit seront
        # utilisées telles quelles.
        #
        ####################################################

        expedition = QGroupBox(
            "🚚 Dimensions d'expédition (carton plié/emballé "
            "— laisser à 0 si identique au produit)"
        )

        formExpedition = QFormLayout(expedition)

        self.longueurExpedition = QDoubleSpinBox()
        self.largeurExpedition = QDoubleSpinBox()
        self.hauteurExpedition = QDoubleSpinBox()

        for champ in (
            self.longueurExpedition,
            self.largeurExpedition,
            self.hauteurExpedition,
        ):
            champ.setDecimals(2)
            champ.setMaximum(9999)

        formExpedition.addRow("Longueur carton (cm)", self.longueurExpedition)
        formExpedition.addRow("Largeur carton (cm)", self.largeurExpedition)
        formExpedition.addRow("Hauteur carton (cm)", self.hauteurExpedition)

        layout.addWidget(expedition)

        ####################################################
        # Emballage
        ####################################################
        #
        # Liste automatiquement mise à jour selon les
        # dimensions et le poids saisis ci-dessus : ne
        # propose que les emballages de la grille qui
        # conviennent réellement (dimensions + poids max
        # supporté). Pré-sélectionne le plus petit compatible
        # si un seul convient, sinon laisse le choix. Si
        # aucun ne convient, la création est bloquée à
        # l'enregistrement avec une alerte.
        #
        ####################################################

        emballageGroupe = QGroupBox("📦 Emballage")

        formEmballage = QFormLayout(emballageGroupe)

        self.emballageCombo = QComboBox()

        self.emballageAlerte = QLabel(
            "⚠ Aucun emballage compatible avec ces dimensions/poids. "
            "Ajoutez-en un dans la grille d'emballages."
        )
        self.emballageAlerte.setStyleSheet("color: red;")
        self.emballageAlerte.setWordWrap(True)
        self.emballageAlerte.setVisible(False)

        formEmballage.addRow("Emballage", self.emballageCombo)
        formEmballage.addRow("", self.emballageAlerte)

        layout.addWidget(emballageGroupe)

        for champ in (
            self.longueur,
            self.largeur,
            self.hauteur,
            self.poids,
            self.longueurExpedition,
            self.largeurExpedition,
            self.hauteurExpedition,
        ):
            champ.valueChanged.connect(
                self._rafraichirEmballagesCompatibles
            )

        ####################################################