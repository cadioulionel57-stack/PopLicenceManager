from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QLineEdit,
    QComboBox,
    QLabel,
    QCheckBox,
)

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.canal_manager import CanalManager
from modules.emballage_manager import EmballageManager


class CaracteristiquesTab(QWidget):

    def __init__(self, type_produit=None):

        super().__init__()

        self.type_produit = type_produit

        self.emballageManager = EmballageManager()

        exterieur = QVBoxLayout(self)
        exterieur.setContentsMargins(0, 0, 0, 0)

        zoneDefilement = QScrollArea()
        zoneDefilement.setWidgetResizable(True)
        zoneDefilement.setStyleSheet(
            "QScrollArea{border:none; background:transparent;}"
        )

        contenuDefilant = QWidget()
        layout = QVBoxLayout(contenuDefilant)

        zoneDefilement.setWidget(contenuDefilant)
        exterieur.addWidget(zoneDefilement)

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
        # Informations
        ####################################################

        infos = QGroupBox("ℹ Informations")

        form3 = QFormLayout(infos)

        self.matiere = QLineEdit()
        self.couleur = QLineEdit()
        self.age = QSpinBox()

        self.age.setMaximum(99)

        self.fabrication = QLineEdit()

        form3.addRow("Matière", self.matiere)
        form3.addRow("Couleur", self.couleur)
        form3.addRow("Âge minimum", self.age)
        form3.addRow("Pays de fabrication", self.fabrication)

        layout.addWidget(infos)

        ####################################################
        # Emballage cadeau (site uniquement, produits stock)
        ####################################################

        self.eligiblePapierCadeau = QCheckBox(
            "🎁 Proposer l'emballage cadeau sur le site pour "
            "ce produit"
        )

        # Prestation uniquement disponible sur le site, pour
        # les produits en stock — inutile de l'afficher sur
        # les autres types de produits.
        self.eligiblePapierCadeau.setVisible(
            self.type_produit == "stock"
        )

        layout.addWidget(self.eligiblePapierCadeau)

        layout.addStretch()

    def _dimensionsEffectives(self):
        """
        Renvoie (longueur, largeur, hauteur) à utiliser pour
        la sélection d'emballage : les dimensions d'expédition
        si elles sont renseignées (>0), sinon les dimensions
        du produit — même règle que celle déjà utilisée pour
        le calcul du transport.
        """

        if (
            self.longueurExpedition.value() > 0
            and self.largeurExpedition.value() > 0
            and self.hauteurExpedition.value() > 0
        ):
            return (
                self.longueurExpedition.value(),
                self.largeurExpedition.value(),
                self.hauteurExpedition.value(),
            )

        return (
            self.longueur.value(),
            self.largeur.value(),
            self.hauteur.value(),
        )

    def _rafraichirEmballagesCompatibles(self):
        """
        Recalcule la liste des emballages compatibles à
        chaque changement de dimension ou de poids, et met
        à jour le menu déroulant + l'alerte en conséquence.
        """

        longueur, largeur, hauteur = self._dimensionsEffectives()
        poids_g = self.poids.value() * 1000

        emballage_id_actuel = self.emballageCombo.currentData()

        self.emballageCombo.blockSignals(True)
        self.emballageCombo.clear()

        compatibles = self.emballageManager.compatibles(
            longueur, largeur, hauteur, poids_g
        )

        for emballage in compatibles:
            self.emballageCombo.addItem(
                f"{emballage['code']} — {emballage['nom']}",
                emballage["id"]
            )

        if compatibles:

            self.emballageCombo.setEnabled(True)
            self.emballageAlerte.setVisible(False)

            index_a_selectionner = self.emballageCombo.findData(
                emballage_id_actuel
            )

            if index_a_selectionner >= 0:
                self.emballageCombo.setCurrentIndex(
                    index_a_selectionner
                )

        else:

            self.emballageCombo.setEnabled(False)
            self.emballageAlerte.setVisible(True)

        self.emballageCombo.blockSignals(False)

    def emballage_id(self):
        """
        Renvoie l'id de l'emballage actuellement sélectionné,
        ou None si aucun n'est disponible/sélectionné.
        """

        return self.emballageCombo.currentData()

    def emballage_valide(self):
        """
        Renvoie False si aucun emballage compatible n'est
        disponible pour les dimensions/poids actuels — utilisé
        pour bloquer l'enregistrement du produit avec une
        alerte explicite.
        """

        return self.emballageCombo.count() > 0

    def _chargerCategoriesCanaux(self):
        """
        Ajoute une ligne "Catégorie <nom du canal>" pour
        chaque canal de vente actif (WiziShop, Amazon FBM,
        Cdiscount, eBay, Leclerc, Rakuten, Fnac...).

        Comme la liste vient entièrement de la table
        canaux_vente, ajouter ou retirer un canal dans
        l'écran "Canaux de vente" change automatiquement
        ce qui s'affiche ici, sans toucher au code.

        Règle métier : les catégories des canaux de type
        "marketplace" ne sont proposées que pour les
        produits de type "stock" (même règle que l'onglet
        Publication).
        """

        canaux = CanalManager().tous()

        for canal in canaux:

            compatible = (
                canal["type"] != "marketplace"
                or self.type_produit == "stock"
            )

            combo = ReferenceComboBox(
                "categories",
                filtre_colonne="canal_id",
                filtre_valeur=canal["id"]
            )

            libelle = f"Catégorie {canal['nom']}"

            if not compatible:
                combo.setEnabled(False)
                libelle += " (produits en stock uniquement)"

            self.categoriesCanaux[canal["id"]] = combo

            self.formCategories.addRow(
                libelle,
                combo
            )

    def categories_canaux_selectionnees(self):
        """
        Renvoie {canal_id: categorie_id} pour tous les
        canaux où une catégorie a été choisie.
        """

        resultat = {}

        for canal_id, combo in self.categoriesCanaux.items():

            categorie_id = combo.id()

            if categorie_id is not None:
                resultat[canal_id] = categorie_id

        return resultat

    def charger(self, produit, categories_canaux=None):
        """
        Pré-remplit l'onglet à partir d'un produit existant
        (mode modification).

        categories_canaux : {canal_id: categorie_id} déjà
        enregistrés pour ce produit.
        """

        self.familleProduit.selectionner(
            produit["famille_produit_id"]
        )

        if categories_canaux:

            for canal_id, combo in self.categoriesCanaux.items():

                combo.selectionner(
                    categories_canaux.get(canal_id)
                )

        self.longueur.setValue(produit["longueur"] or 0)
        self.largeur.setValue(produit["largeur"] or 0)
        self.hauteur.setValue(produit["hauteur"] or 0)
        self.poids.setValue(produit["poids"] or 0)

        self.longueurExpedition.setValue(
            produit["longueur_expedition"] or 0
        )
        self.largeurExpedition.setValue(
            produit["largeur_expedition"] or 0
        )
        self.hauteurExpedition.setValue(
            produit["hauteur_expedition"] or 0
        )

        self.matiere.setText(produit["matiere"] or "")
        self.couleur.setText(produit["couleur"] or "")
        self.age.setValue(produit["age_minimum"] or 0)
        self.fabrication.setText(produit["pays_fabrication"] or "")

        self.eligiblePapierCadeau.setChecked(
            bool(produit["eligible_papier_cadeau"])
        )

        self._rafraichirEmballagesCompatibles()

        emballage_enregistre = produit["emballage_id"]

        if emballage_enregistre is not None:

            index = self.emballageCombo.findData(emballage_enregistre)

            if index >= 0:
                self.emballageCombo.setCurrentIndex(index)