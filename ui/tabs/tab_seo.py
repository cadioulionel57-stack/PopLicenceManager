from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtGui import QFont

from modules.seo_generator import SeoGenerator


class SeoTab(QWidget):
    """
    Onglet SEO de la fiche produit : titre, descriptions,
    meta description, mots-clés, URL et données structurées
    Schema.org.

    Rempli automatiquement à la création du produit (voir
    product_dialog_v2.py), et régénérable à tout moment via
    le bouton "Régénérer", par exemple après avoir changé le
    nom ou la licence du produit. Tous les champs restent
    modifiables à la main ensuite.
    """

    def __init__(self):

        super().__init__()

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
        # Bouton de génération/régénération
        ####################################################

        ligneBouton = QHBoxLayout()

        self.btnRegenerer = QPushButton(
            "🪄 Régénérer le contenu SEO à partir de la fiche produit"
        )
        ligneBouton.addWidget(self.btnRegenerer)

        layout.addLayout(ligneBouton)

        self.avertissement = QLabel(
            "⚠ La régénération remplace tout le contenu "
            "actuel de cet onglet — pense à sauvegarder tes "
            "modifications manuelles ailleurs si besoin."
        )
        self.avertissement.setStyleSheet("color: #b9770e;")
        self.avertissement.setWordWrap(True)
        layout.addWidget(self.avertissement)

        ####################################################
        # Titre SEO
        ####################################################

        groupeTitre = QGroupBox("Titre SEO")
        formTitre = QFormLayout(groupeTitre)

        self.titreSeo = QLineEdit()
        self.titreSeo.textChanged.connect(self._majCompteurTitre)
        formTitre.addRow("Titre", self.titreSeo)

        self.compteurTitre = QLabel()
        self._appliquerStyleCompteur(self.compteurTitre)
        formTitre.addRow("", self.compteurTitre)

        layout.addWidget(groupeTitre)

        ####################################################
        # Descriptions
        ####################################################

        groupeDescriptions = QGroupBox("Descriptions")
        formDescriptions = QFormLayout(groupeDescriptions)

        self.descriptionCourte = QTextEdit()
        self.descriptionCourte.setMaximumHeight(70)
        self.descriptionCourte.textChanged.connect(
            self._majCompteurDescriptionCourte
        )
        formDescriptions.addRow(
            "Description courte", self.descriptionCourte
        )

        self.compteurDescriptionCourte = QLabel()
        self._appliquerStyleCompteur(self.compteurDescriptionCourte)
        formDescriptions.addRow("", self.compteurDescriptionCourte)

        self.descriptionLongue = QTextEdit()
        self.descriptionLongue.setMinimumHeight(140)
        formDescriptions.addRow(
            "Description longue", self.descriptionLongue
        )

        noteDescriptionLongue = QLabel(
            "💡 Brouillon généré automatiquement — à enrichir "
            "toi-même sur tes produits les plus importants, "
            "pour éviter un texte trop similaire d'une fiche "
            "à l'autre."
        )
        noteDescriptionLongue.setWordWrap(True)
        noteDescriptionLongue.setStyleSheet("color: #7f8c8d;")
        formDescriptions.addRow("", noteDescriptionLongue)

        layout.addWidget(groupeDescriptions)

        ####################################################
        # Référencement
        ####################################################

        groupeReferencement = QGroupBox("Référencement")
        formReferencement = QFormLayout(groupeReferencement)

        self.metaDescription = QTextEdit()
        self.metaDescription.setMaximumHeight(70)
        self.metaDescription.textChanged.connect(
            self._majCompteurMetaDescription
        )
        formReferencement.addRow(
            "Meta description", self.metaDescription
        )

        self.compteurMetaDescription = QLabel()
        self._appliquerStyleCompteur(self.compteurMetaDescription)
        formReferencement.addRow("", self.compteurMetaDescription)

        self.motsCles = QLineEdit()
        formReferencement.addRow("Mots-clés", self.motsCles)

        self.urlSlug = QLineEdit()
        formReferencement.addRow("URL / slug", self.urlSlug)

        layout.addWidget(groupeReferencement)

        ####################################################
        # Données structurées (Schema.org)
        ####################################################

        groupeSchema = QGroupBox(
            "Données structurées Schema.org (technique, "
            "pour Google)"
        )
        layoutSchema = QVBoxLayout(groupeSchema)

        noteSchema = QLabel(
            "Code invisible pour le client, lu par Google — "
            "permet d'afficher le prix et la disponibilité "
            "directement dans les résultats de recherche. "
            "Régénéré automatiquement, non modifiable "
            "manuellement (dépend du prix de vente réel)."
        )
        noteSchema.setWordWrap(True)
        noteSchema.setStyleSheet("color: #7f8c8d;")
        layoutSchema.addWidget(noteSchema)

        self.schemaOrg = QTextEdit()
        self.schemaOrg.setReadOnly(True)
        self.schemaOrg.setMinimumHeight(160)

        policeMonospace = QFont("Courier New")
        self.schemaOrg.setFont(policeMonospace)

        layoutSchema.addWidget(self.schemaOrg)

        layout.addWidget(groupeSchema)

        layout.addStretch()

        self.btnRegenerer.clicked.connect(self.regenerer)

        # Ces attributs sont branchés depuis
        # product_dialog_v2.py, comme pour l'onglet
        # Tarification — ils donnent accès en direct aux
        # valeurs saisies dans les autres onglets.
        self._nom = lambda: ""
        self._licence_nom = lambda: None
        self._marque_nom = lambda: None
        self._matiere = lambda: None
        self._couleur = lambda: None
        self._age_minimum = lambda: None
        self._pays_fabrication = lambda: None
        self._ean = lambda: None
        self._sku = lambda: None
        self._prix_ttc_site = lambda: None

    def _appliquerStyleCompteur(self, label):

        police = QFont()
        police.setPointSize(police.pointSize() - 1)
        label.setFont(police)
        label.setStyleSheet("color: #7f8c8d;")

    def _majCompteurTitre(self):

        longueur = len(self.titreSeo.text())
        limite = SeoGenerator.LONGUEUR_MAX_TITRE

        self.compteurTitre.setText(f"{longueur} / {limite} caractères")
        self.compteurTitre.setStyleSheet(
            "color: #c0392b;" if longueur > limite else "color: #7f8c8d;"
        )

    def _majCompteurDescriptionCourte(self):

        longueur = len(self.descriptionCourte.toPlainText())
        limite = SeoGenerator.LONGUEUR_MAX_DESCRIPTION_COURTE

        self.compteurDescriptionCourte.setText(
            f"{longueur} / {limite} caractères"
        )
        self.compteurDescriptionCourte.setStyleSheet(
            "color: #c0392b;" if longueur > limite else "color: #7f8c8d;"
        )

    def _majCompteurMetaDescription(self):

        longueur = len(self.metaDescription.toPlainText())
        limite = SeoGenerator.LONGUEUR_MAX_META_DESCRIPTION

        self.compteurMetaDescription.setText(
            f"{longueur} / {limite} caractères"
        )
        self.compteurMetaDescription.setStyleSheet(
            "color: #c0392b;" if longueur > limite else "color: #7f8c8d;"
        )

    def regenerer(self):
        """
        Regénère les 7 champs à partir des valeurs
        actuellement saisies dans les autres onglets de la
        fiche produit.
        """

        resultat = SeoGenerator.generer(
            nom_produit=self._nom(),
            licence_nom=self._licence_nom(),
            marque_nom=self._marque_nom(),
            categorie_nom=None,
            famille_nom=None,
            matiere=self._matiere(),
            couleur=self._couleur(),
            age_minimum=self._age_minimum(),
            pays_fabrication=self._pays_fabrication(),
            ean=self._ean(),
            sku=self._sku(),
            prix_ttc=self._prix_ttc_site(),
        )

        self.charger_depuis_dict(resultat)

    def charger_depuis_dict(self, valeurs):

        self.titreSeo.setText(valeurs.get("titre_seo") or "")
        self.descriptionCourte.setPlainText(
            valeurs.get("description_courte") or ""
        )
        self.descriptionLongue.setPlainText(
            valeurs.get("description_longue") or ""
        )
        self.metaDescription.setPlainText(
            valeurs.get("meta_description") or ""
        )
        self.motsCles.setText(valeurs.get("mots_cles") or "")
        self.urlSlug.setText(valeurs.get("url_slug") or "")
        self.schemaOrg.setPlainText(
            valeurs.get("schema_org_json") or ""
        )

    def charger(self, produit):
        """
        Charge les champs SEO déjà enregistrés pour ce
        produit (mode modification).
        """

        self.titreSeo.setText(produit["titre_seo"] or "")
        self.descriptionCourte.setPlainText(
            produit["description_courte"] or ""
        )
        self.descriptionLongue.setPlainText(
            produit["description_longue"] or ""
        )
        self.metaDescription.setPlainText(
            produit["meta_description"] or ""
        )
        self.motsCles.setText(produit["mots_cles"] or "")
        self.urlSlug.setText(produit["url_slug"] or "")

    def est_vide(self):
        """
        Renvoie True si aucun champ SEO n'a encore été
        rempli — utilisé pour déclencher la génération
        automatique à la toute première sauvegarde d'un
        nouveau produit, sans écraser un contenu déjà saisi.
        """

        return not self.titreSeo.text().strip()