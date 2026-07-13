from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QScrollArea,
    QWidget,
    QGroupBox,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt


class WizishopExportDialog(QDialog):
    """
    Fenêtre affichée en cliquant sur "Export" dans la liste
    Produits — laisse choisir quelles colonnes facultatives de
    la nomenclature CSV WiziShop inclure dans l'export, en plus
    des colonnes obligatoires (toujours incluses, non
    désactivables).

    Ne s'occupe QUE des produits passés en paramètre (ceux
    cochés/sélectionnés dans la liste au moment du clic sur
    Export) — jamais de tout le catalogue.
    """

    # Colonnes facultatives proposées — la clé est le nom
    # utilisé en interne (repris tel quel par le générateur CSV
    # du fichier suivant), la valeur affichée est le libellé
    # exact de la nomenclature WiziShop.
    COLONNES_FACULTATIVES = [
        ("reference_fournisseur", "Référence fournisseur"),
        ("nom_fournisseur", "Nom du fournisseur"),
        ("ean13", "EAN 13"),
        ("isbn", "ISBN"),
        ("mots_cles", "Mots clés"),
        ("caracteristiques", "Caractéristiques"),
        ("titre_page", "Titre de la page (max 65 caractères)"),
        ("url", "URL (sans .html)"),
        ("meta_description", "Méta description"),
        ("photo_2", "Photo 2"),
        ("photo_3", "Photo 3"),
        ("date_debut", "Date de début"),
        ("date_fin", "Date de fin"),
        ("produit_en_selection", "Produit dans la sélection (TRUE/FALSE)"),
    ]

    def __init__(self, identifiants_produits, parent=None):

        super().__init__(parent)

        self.identifiants_produits = identifiants_produits
        self.cases_facultatives = {}

        self.setWindowTitle("Export vers WiziShop")
        self.setMinimumWidth(520)
        self.setMinimumHeight(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        ####################################################
        # Résumé
        ####################################################

        nombre = len(self.identifiants_produits)

        resume = QLabel(
            f"📤 <b>{nombre} produit(s)</b> sélectionné(s) seront "
            f"exportés."
        )
        resume.setStyleSheet("font-size:11pt;")
        layout.addWidget(resume)

        ####################################################
        # Colonnes obligatoires — informatif, non modifiable
        ####################################################

        groupeObligatoire = QGroupBox(
            "✔ Colonnes obligatoires (toujours incluses)"
        )
        layoutObligatoire = QVBoxLayout(groupeObligatoire)

        texteObligatoire = QLabel(
            "ID Produit, Référence produit, Nom du produit, "
            "Description courte, Description longue, Poids, "
            "Nombre de produits en stock, Photo 1, État, "
            "ID Marque, Nom Marque, ID Catégorie principale "
            "parente, Catégorie principale parente, ID "
            "Sous-catégorie principale, Sous-catégorie "
            "principale, Prix TTC."
        )
        texteObligatoire.setWordWrap(True)
        texteObligatoire.setStyleSheet("color:#475569; font-size:9.5pt;")

        layoutObligatoire.addWidget(texteObligatoire)

        avertissementPrix = QLabel(
            "⚠️ Le nom exact de la colonne prix n'est pas garanti "
            "à 100% (non confirmé par un export réel WiziShop) — "
            "vérifie le résultat après un premier essai avec un "
            "petit lot de produits."
        )
        avertissementPrix.setWordWrap(True)
        avertissementPrix.setStyleSheet(
            "color:#b45309; font-size:9pt; font-style:italic;"
        )
        layoutObligatoire.addWidget(avertissementPrix)

        layout.addWidget(groupeObligatoire)

        ####################################################
        # Colonnes facultatives — cases à cocher
        ####################################################

        groupeFacultatif = QGroupBox("☐ Colonnes facultatives à inclure")
        layoutFacultatifExterieur = QVBoxLayout(groupeFacultatif)

        barreOutilsFacultatif = QHBoxLayout()

        btnToutCocher = QPushButton("Tout cocher")
        btnToutDecocher = QPushButton("Tout décocher")

        btnToutCocher.clicked.connect(self._toutCocher)
        btnToutDecocher.clicked.connect(self._toutDecocher)

        barreOutilsFacultatif.addWidget(btnToutCocher)
        barreOutilsFacultatif.addWidget(btnToutDecocher)
        barreOutilsFacultatif.addStretch()

        layoutFacultatifExterieur.addLayout(barreOutilsFacultatif)

        zoneDefilante = QScrollArea()
        zoneDefilante.setWidgetResizable(True)

        contenuDefilant = QWidget()
        layoutFacultatif = QVBoxLayout(contenuDefilant)
        layoutFacultatif.setSpacing(6)

        for cle, libelle in self.COLONNES_FACULTATIVES:

            case = QCheckBox(libelle)
            case.setChecked(True)

            self.cases_facultatives[cle] = case
            layoutFacultatif.addWidget(case)

        layoutFacultatif.addStretch()

        zoneDefilante.setWidget(contenuDefilant)
        layoutFacultatifExterieur.addWidget(zoneDefilante)

        layout.addWidget(groupeFacultatif, stretch=1)

        ####################################################
        # Boutons d'action
        ####################################################

        barreBoutons = QHBoxLayout()

        btnAnnuler = QPushButton("Annuler")
        btnAnnuler.setObjectName("btnSecondaire")
        btnAnnuler.clicked.connect(self.reject)

        btnExporter = QPushButton("📤 Générer le fichier CSV")
        btnExporter.clicked.connect(self._genererExport)

        barreBoutons.addStretch()
        barreBoutons.addWidget(btnAnnuler)
        barreBoutons.addWidget(btnExporter)

        layout.addLayout(barreBoutons)

    def _toutCocher(self):

        for case in self.cases_facultatives.values():
            case.setChecked(True)

    def _toutDecocher(self):

        for case in self.cases_facultatives.values():
            case.setChecked(False)

    def _colonnesFacultativesChoisies(self):
        """
        Renvoie la liste des clés internes des colonnes
        facultatives actuellement cochées.
        """

        return [
            cle for cle, case in self.cases_facultatives.items()
            if case.isChecked()
        ]

    def _genererExport(self):

        chemin, _filtre = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'export WiziShop",
            "export_wizishop.csv",
            "Fichiers CSV (*.csv)"
        )

        if not chemin:
            return

        # Le générateur CSV lui-même (lecture des produits,
        # respect de la nomenclature WiziShop — séparateur
        # point-virgule, encodage, en-têtes) est construit dans
        # le fichier suivant de ce chantier. Import local
        # volontaire : tant que ce fichier n'existe pas encore,
        # ce bouton affichera une erreur — normal à ce stade.
        from modules.wizishop_export_manager import WizishopExportManager

        gestionnaire = WizishopExportManager()

        try:

            resultat = gestionnaire.exporter(
                identifiants_produits=self.identifiants_produits,
                colonnes_facultatives=self._colonnesFacultativesChoisies(),
                chemin_fichier=chemin,
            )

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur d'export",
                f"L'export a échoué :\n{erreur}"
            )
            return

        message = (
            f"{resultat['nombre_lignes']} produit(s) exporté(s) avec "
            f"succès vers :\n{chemin}"
        )

        if resultat["produits_sans_gabarit"]:

            liste = "\n".join(
                f"• {nom}" for nom in resultat["produits_sans_gabarit"]
            )
            message += (
                f"\n\n⚠️ Attention : {len(resultat['produits_sans_gabarit'])} "
                f"produit(s) n'ont aucun modèle de fiche actif pour leur "
                f"thème — leur Description longue utilise le texte de "
                f"secours au lieu du HTML mis en forme :\n{liste}"
            )

        QMessageBox.information(
            self,
            "Export terminé",
            message
        )

        self.accept()