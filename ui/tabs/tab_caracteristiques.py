from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QLineEdit,
)

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.canal_manager import CanalManager


class CaracteristiquesTab(QWidget):

    def __init__(self, type_produit=None):

        super().__init__()

        self.type_produit = type_produit

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

        layout.addStretch()

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

        self.matiere.setText(produit["matiere"] or "")
        self.couleur.setText(produit["couleur"] or "")
        self.age.setValue(produit["age_minimum"] or 0)
        self.fabrication.setText(produit["pays_fabrication"] or "")