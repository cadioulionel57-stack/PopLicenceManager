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

        # Un produit Direct Fournisseur est expédié par le
        # fournisseur lui-même, jamais par toi — aucun
        # emballage de ta grille ne s'applique donc ici. Le
        # champ est masqué entièrement plutôt que de forcer
        # un choix qui n'a pas de sens (le coût d'emballage
        # retombera à 0€, ou sur celui de la famille si elle
        # en a un).
        emballageGroupe.setVisible(self.type_produit != "dropshipping")


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
        # Champs façon Amazon (textile) — génériques, à
        # laisser vides si non pertinents pour ce type
        # d'article (ex: pas de "manche" pour un pantalon).
        ####################################################

        groupeTextile = QGroupBox("👕 Détails textile (facultatif)")
        formTextile = QFormLayout(groupeTextile)

        self.compositionMatiere = QLineEdit()
        self.compositionMatiere.setPlaceholderText(
            "Ex : 100% Coton, ou 90% Coton / 10% Polyester"
        )
        formTextile.addRow("Composition", self.compositionMatiere)

        self.instructionsEntretien = QLineEdit()
        self.instructionsEntretien.setPlaceholderText(
            "Ex : Lavage machine à froid, séchage basse température"
        )
        formTextile.addRow(
            "Instructions d'entretien", self.instructionsEntretien
        )

        self.coupeType = QLineEdit()
        self.coupeType.setPlaceholderText("Ex : À capuche, Regular fit...")
        formTextile.addRow("Style de coupe", self.coupeType)

        self.typeManche = QLineEdit()
        self.typeManche.setPlaceholderText(
            "Ex : Manche longue, Sans manche..."
        )
        formTextile.addRow("Type de manche", self.typeManche)

        layout.addWidget(groupeTextile)

        ####################################################
        # Champs Jeux & Jouets — génériques, à laisser vides
        # si non pertinents pour ce type d'article. Si un
        # champ reste vide, la section correspondante
        # disparaît automatiquement de la fiche publiée
        # (voir generateur_fiche_html.py).
        ####################################################

        groupeJeuxJouets = QGroupBox("🧩 Détails Jeux & Jouets (facultatif)")
        formJeuxJouets = QFormLayout(groupeJeuxJouets)

        self.ageConseille = QLineEdit()
        self.ageConseille.setPlaceholderText("Ex : 3 ans et +, 8-12 ans...")
        formJeuxJouets.addRow("Âge conseillé", self.ageConseille)

        self.nombreJoueurs = QLineEdit()
        self.nombreJoueurs.setPlaceholderText("Ex : 2 à 4 joueurs, 1 joueur...")
        formJeuxJouets.addRow("Nombre de joueurs", self.nombreJoueurs)

        self.dureePartie = QLineEdit()
        self.dureePartie.setPlaceholderText("Ex : 15-30 minutes, 1 heure...")
        formJeuxJouets.addRow("Durée d'une partie", self.dureePartie)

        self.contenuBoite = QLineEdit()
        self.contenuBoite.setPlaceholderText(
            "Ex : 1 plateau, 54 cartes, 4 pions, règle du jeu"
        )
        formJeuxJouets.addRow("Contenu de la boîte", self.contenuBoite)

        self.nombrePieces = QLineEdit()
        self.nombrePieces.setPlaceholderText("Ex : 234 pièces, 1200 pièces...")
        formJeuxJouets.addRow("Nombre de pièces", self.nombrePieces)

        layout.addWidget(groupeJeuxJouets)

        ####################################################
        # Champ Linge de Maison — générique, à laisser vide
        # si non pertinent. Même principe que les champs
        # Jeux & Jouets ci-dessus : la section correspondante
        # disparaît automatiquement de la fiche publiée si le
        # champ reste vide (voir generateur_fiche_html.py).
        ####################################################

        groupeLingeMaison = QGroupBox("🛏️ Détails Linge de Maison / Mugs & Vaisselle (facultatif)")
        formLingeMaison = QFormLayout(groupeLingeMaison)

        self.tailleLiterie = QLineEdit()
        self.tailleLiterie.setPlaceholderText(
            "Ex : 140x200 cm, 220x240 cm, 65x65 cm..."
        )
        formLingeMaison.addRow("Taille/dimensions literie", self.tailleLiterie)

        self.contenance = QLineEdit()
        self.contenance.setPlaceholderText("Ex : 325 ml, 500 ml, 1 L...")
        formLingeMaison.addRow("Contenance", self.contenance)

        self.compatibleLaveVaisselle = QCheckBox(
            "🍽️ Compatible lave-vaisselle"
        )
        formLingeMaison.addRow("", self.compatibleLaveVaisselle)

        layout.addWidget(groupeLingeMaison)

        ####################################################
        # Champ Électronique — générique, à laisser vide si
        # non pertinent. Même principe que les groupes
        # ci-dessus : la section correspondante disparaît
        # automatiquement de la fiche publiée si le champ
        # reste vide (voir generateur_fiche_html.py).
        ####################################################

        groupeElectronique = QGroupBox("🔌 Détails Électronique (facultatif)")
        formElectronique = QFormLayout(groupeElectronique)

        self.typeAlimentation = QLineEdit()
        self.typeAlimentation.setPlaceholderText(
            "Ex : Pile (incluse), Secteur, USB..."
        )
        formElectronique.addRow("Type d'alimentation", self.typeAlimentation)

        layout.addWidget(groupeElectronique)

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

        self.compositionMatiere.setText(
            produit["composition_matiere"] or ""
        )
        self.instructionsEntretien.setText(
            produit["instructions_entretien"] or ""
        )
        self.coupeType.setText(produit["coupe_type"] or "")
        self.typeManche.setText(produit["type_manche"] or "")

        self.ageConseille.setText(produit["age_conseille"] or "")
        self.nombreJoueurs.setText(produit["nombre_joueurs"] or "")
        self.dureePartie.setText(produit["duree_partie"] or "")
        self.contenuBoite.setText(produit["contenu_boite"] or "")
        self.nombrePieces.setText(produit["nombre_pieces"] or "")

        self.tailleLiterie.setText(produit["taille_literie"] or "")

        self.contenance.setText(produit["contenance"] or "")

        self.compatibleLaveVaisselle.setChecked(
            bool(produit["compatible_lave_vaisselle"])
        )

        self.typeAlimentation.setText(produit["type_alimentation"] or "")

        self.eligiblePapierCadeau.setChecked(
            bool(produit["eligible_papier_cadeau"])
        )

        self._rafraichirEmballagesCompatibles()

        emballage_enregistre = produit["emballage_id"]

        if emballage_enregistre is not None:

            index = self.emballageCombo.findData(emballage_enregistre)

            if index >= 0:
                self.emballageCombo.setCurrentIndex(index)