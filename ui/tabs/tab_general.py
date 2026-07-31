from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QInputDialog,
    QMessageBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtGui import QColor

from ui.widgets.reference_combobox import ReferenceComboBox
from database.database import Database
from modules.product_manager import ProductManager
from modules.stock_manager import StockManager


class GeneralTab(QWidget):

    STATUTS = {
        "actif": ("✅ Actif", "#1e7d32"),
        "rupture": ("⚠ En rupture", "#b35c10"),
        "fin_de_vie": ("⛔ Fin de vie", "#c0392b"),
    }

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
        principal = QVBoxLayout(contenuDefilant)

        zoneDefilement.setWidget(contenuDefilant)
        exterieur.addWidget(zoneDefilement)

        origine = QGroupBox("📦 Origine")
        formOrigine = QFormLayout(origine)

        self.typeProduit = QLineEdit()
        self.typeProduit.setReadOnly(True)
        formOrigine.addRow("Type de produit", self.typeProduit)

        self.statutStock = QComboBox()

        for cle, (libelle, couleur) in self.STATUTS.items():
            self.statutStock.addItem(libelle, cle)

        self.statutStock.currentIndexChanged.connect(
            self._majCouleurStatut
        )
        self._majCouleurStatut()

        formOrigine.addRow("Statut du produit", self.statutStock)

        self.quantiteStock = QSpinBox()
        self.quantiteStock.setMaximum(99999)
        self.quantiteStock.setToolTip(
            "Quantité réellement en stock — distincte du statut "
            "ci-dessus. Sert de base au \"Nombre de produits en "
            "stock\" exporté vers WiziShop, et reste juste même si "
            "ce produit est un jour réimporté puis réexporté."
        )
        formOrigine.addRow("Quantité en stock", self.quantiteStock)

        self.ficheATerminer = QCheckBox(
            "⚠ Fiche à compléter (créée rapidement, infos "
            "manquantes — décoche une fois terminée)"
        )
        self.ficheATerminer.setStyleSheet(
            "color:#c0392b; font-weight:600;"
        )
        formOrigine.addRow("", self.ficheATerminer)


        # La fiche produit impose min-width:140px à tous les
        # boutons : sans cette surcharge, le « + » s'étale sur
        # 180 px, déborde de sa case et on ne clique plus là
        # où on croit.
        STYLE_PLUS = (
            "QPushButton{min-width:0px; max-width:35px;"
            "padding:4px 0px; font-weight:700;}"
        )

        ligneFournisseur = QHBoxLayout()
        self.cboFournisseur = ReferenceComboBox("fournisseurs")
        self.btnAjouterFournisseur = QPushButton("+")
        self.btnAjouterFournisseur.setFixedWidth(35)
        self.btnAjouterFournisseur.setStyleSheet(STYLE_PLUS)
        self.btnAjouterFournisseur.setToolTip(
            "Créer un fournisseur qui n'existe pas encore"
        )
        ligneFournisseur.addWidget(self.cboFournisseur)
        ligneFournisseur.addWidget(self.btnAjouterFournisseur)
        formOrigine.addRow("Fournisseur", ligneFournisseur)

        self.referenceFournisseur = QLineEdit()
        formOrigine.addRow("Référence fournisseur", self.referenceFournisseur)

        self.prixAchatHt = QDoubleSpinBox()
        self.prixAchatHt.setDecimals(2)
        self.prixAchatHt.setMaximum(99999)
        self.prixAchatHt.setSuffix(" €")
        formOrigine.addRow("Prix d'achat fournisseur (HT)", self.prixAchatHt)

        self.commandeFournisseur = QComboBox()
        formOrigine.addRow("Commande fournisseur", self.commandeFournisseur)

        principal.addWidget(origine)

        classification = QGroupBox("🏷 Classification")
        formClassification = QFormLayout(classification)

        ligneLicence = QHBoxLayout()
        self.cboLicence = ReferenceComboBox("licences")
        self.btnAjouterLicence = QPushButton("+")
        self.btnAjouterLicence.setFixedWidth(35)
        self.btnAjouterLicence.setStyleSheet(STYLE_PLUS)
        self.btnAjouterLicence.setToolTip(
            "Créer une licence qui n'existe pas encore"
        )
        ligneLicence.addWidget(self.cboLicence)
        ligneLicence.addWidget(self.btnAjouterLicence)
        formClassification.addRow("Licence", ligneLicence)

        ligneMarque = QHBoxLayout()
        self.cboMarque = ReferenceComboBox("marques")
        self.btnAjouterMarque = QPushButton("+")
        self.btnAjouterMarque.setFixedWidth(35)
        self.btnAjouterMarque.setStyleSheet(STYLE_PLUS)
        self.btnAjouterMarque.setToolTip(
            "Créer une marque qui n'existe pas encore"
        )
        ligneMarque.addWidget(self.cboMarque)
        ligneMarque.addWidget(self.btnAjouterMarque)
        formClassification.addRow("Marque", ligneMarque)

        principal.addWidget(classification)

        ####################################################
        # Composition du bundle
        #
        # Un bundle n'a pas de stock à lui : il est monté à
        # partir des produits à l'unité. C'est cette liste qui
        # permet à l'écran Stock de savoir combien de coffrets
        # sont montables, et de déduire les bons composants
        # quand un coffret est vendu.
        ####################################################

        self.groupeComposition = QGroupBox("🎁 Composition du bundle")
        layoutComposition = QVBoxLayout(self.groupeComposition)

        self.btnAjouterComposant = QPushButton("+ Ajouter un composant")
        layoutComposition.addWidget(self.btnAjouterComposant)

        self.tableComposants = QTableWidget()
        self.tableComposants.setColumnCount(4)
        self.tableComposants.setHorizontalHeaderLabels([
            "Code EAN/SKU", "Produit", "Qté", ""
        ])

        enteteComposants = self.tableComposants.horizontalHeader()
        enteteComposants.setSectionResizeMode(0, QHeaderView.Fixed)
        enteteComposants.setSectionResizeMode(1, QHeaderView.Stretch)
        enteteComposants.setSectionResizeMode(2, QHeaderView.Fixed)
        enteteComposants.setSectionResizeMode(3, QHeaderView.Fixed)
        self.tableComposants.setColumnWidth(0, 150)
        self.tableComposants.setColumnWidth(2, 70)
        self.tableComposants.setColumnWidth(3, 50)
        self.tableComposants.setMinimumHeight(160)

        layoutComposition.addWidget(self.tableComposants)

        aideComposition = QLabel(
            "Tape le SKU ou le code-barres du composant puis "
            "appuie sur Entrée. La quantité est le nombre "
            "d'exemplaires de ce produit dans UN bundle."
        )
        aideComposition.setWordWrap(True)
        aideComposition.setStyleSheet("color:#64748b; font-size:12px;")
        layoutComposition.addWidget(aideComposition)

        principal.addWidget(self.groupeComposition)

        self.btnAjouterComposant.clicked.connect(
            self.ajouterComposant
        )

        # Visible uniquement pour un bundle. Le type est écrit
        # dans le champ par la fiche produit après coup, d'où
        # ce branchement plutôt qu'un test à la construction.
        self._estBundle = False
        self.groupeComposition.setVisible(False)
        self.typeProduit.textChanged.connect(
            self._basculerComposition
        )

        identification = QGroupBox("📝 Identification")
        formIdentification = QFormLayout(identification)

        self.nom = QLineEdit()
        self.ean = QLineEdit()
        self.sku = QLineEdit()
        self.sku.setReadOnly(True)

        formIdentification.addRow("Nom", self.nom)
        formIdentification.addRow("EAN", self.ean)
        formIdentification.addRow("SKU", self.sku)

        principal.addWidget(identification)
        principal.addStretch()

        ####################################################
        # Création à la volée d'un fournisseur, d'une licence
        # ou d'une marque qui n'existe pas encore, sans
        # quitter la fiche produit en cours de saisie.
        ####################################################

        self.btnAjouterFournisseur.clicked.connect(
            lambda: self._creerReference(
                self.cboFournisseur,
                "fournisseurs",
                "fournisseur",
            )
        )

        self.btnAjouterLicence.clicked.connect(
            lambda: self._creerReference(
                self.cboLicence,
                "licences",
                "licence",
            )
        )

        self.btnAjouterMarque.clicked.connect(
            lambda: self._creerReference(
                self.cboMarque,
                "marques",
                "marque",
            )
        )

    def _creerReference(self, combo, table, libelle):
        """
        Demande un nom, crée l'élément s'il n'existe pas
        déjà, recharge la liste déroulante et le sélectionne.

        Volontairement minimal : seul le nom est demandé, le
        reste (contact, conditions de règlement, logo...) se
        complète plus tard dans l'écran dédié. L'objectif est
        de ne pas interrompre la saisie d'une fiche produit.
        """

        nom, valide = QInputDialog.getText(
            self,
            f"Nouveau {libelle}",
            f"Nom du {libelle} :",
        )

        if not valide:
            return

        nom = nom.strip()

        if not nom:

            QMessageBox.warning(
                self,
                "Nom manquant",
                f"Indique un nom pour ce {libelle}."
            )
            return

        db = Database()

        # Déjà présent ? On le sélectionne au lieu d'en créer
        # un doublon — y compris s'il avait été désactivé.
        existant = db.lire_un(
            f"SELECT id, actif FROM {table} WHERE nom = ?",
            (nom,)
        )

        if existant is not None:

            if not existant["actif"]:
                db.executer(
                    f"UPDATE {table} SET actif = 1 WHERE id = ?",
                    (existant["id"],)
                )

            identifiant = existant["id"]

            QMessageBox.information(
                self,
                f"{libelle.capitalize()} existant",
                f"« {nom} » existait déjà : il a été "
                f"sélectionné."
            )

        else:

            curseur = db.executer(
                f"INSERT INTO {table} (nom, actif) VALUES (?, 1)",
                (nom,)
            )

            identifiant = curseur.lastrowid

        combo.charger()
        combo.selectionner(identifiant)

    ########################################################
    # Composition du bundle
    ########################################################

    def _basculerComposition(self, texte):

        # On mémorise le type dans un booléen plutôt que de
        # relire isVisible() : au moment où l'écran Produits
        # enregistre, la fiche est déjà fermée, donc tous ses
        # widgets sont invisibles et la composition serait
        # perdue en silence.
        self._estBundle = "Bundle" in (texte or "")

        self.groupeComposition.setVisible(self._estBundle)

    def est_bundle(self):

        return self._estBundle

    def ajouterComposant(self, donnees=None):
        """
        Ajoute une ligne vide dans la composition. Le produit
        se retrouve en tapant son SKU ou son EAN puis Entrée,
        comme dans une commande.
        """

        ligne = self.tableComposants.rowCount()
        self.tableComposants.insertRow(ligne)

        champCode = QLineEdit()
        champCode.setPlaceholderText("EAN ou SKU, puis Entrée")
        champCode.produit_id = None

        libelle = QLabel("—")
        libelle.setStyleSheet("color:#64748b;")

        quantite = QSpinBox()
        quantite.setMinimum(1)
        quantite.setMaximum(999)
        quantite.setValue(1)

        supprimer = QPushButton("🗑")
        supprimer.setStyleSheet(
            "QPushButton{min-width:0px; max-width:40px; padding:4px 0px;}"
        )
        supprimer.clicked.connect(
            lambda: self._supprimerComposant(supprimer)
        )

        def rechercher():

            code = champCode.text().strip()

            if not code:
                return

            produit = ProductManager().trouver_par_code(code)

            if produit is None:
                libelle.setText("❌ Introuvable")
                libelle.setStyleSheet("color:#c0392b;")
                champCode.produit_id = None
                return

            if produit["type_produit"] == "bundle":
                libelle.setText("❌ Un bundle ne peut pas en contenir un autre")
                libelle.setStyleSheet("color:#c0392b;")
                champCode.produit_id = None
                return

            if produit["type_produit"] != "stock":
                libelle.setText("❌ Seuls les produits en stock sont possibles")
                libelle.setStyleSheet("color:#c0392b;")
                champCode.produit_id = None
                return

            champCode.produit_id = produit["id"]
            libelle.setText(produit["nom"] or "")
            libelle.setStyleSheet("color:#2c3e50;")

        champCode.returnPressed.connect(rechercher)

        self.tableComposants.setCellWidget(ligne, 0, champCode)
        self.tableComposants.setCellWidget(ligne, 1, libelle)
        self.tableComposants.setCellWidget(ligne, 2, quantite)
        self.tableComposants.setCellWidget(ligne, 3, supprimer)

        if donnees:

            champCode.produit_id = donnees.get("produit_id")
            champCode.setText(donnees.get("code") or "")
            libelle.setText(donnees.get("nom") or "—")
            libelle.setStyleSheet("color:#2c3e50;")
            quantite.setValue(donnees.get("quantite") or 1)

    def _supprimerComposant(self, bouton):

        for ligne in range(self.tableComposants.rowCount()):

            if self.tableComposants.cellWidget(ligne, 3) == bouton:
                self.tableComposants.removeRow(ligne)
                return

    def charger_composants(self, bundle_id):
        """
        Remplit la composition à l'ouverture d'un bundle
        existant.
        """

        self.tableComposants.setRowCount(0)

        if not bundle_id:
            return

        produits = ProductManager()

        for composant in StockManager().composants(bundle_id):

            fiche = produits.obtenir(composant["produit_id"])

            self.ajouterComposant({
                "produit_id": composant["produit_id"],
                "code": (
                    (fiche["sku"] or fiche["ean"] or "")
                    if fiche else ""
                ),
                "nom": composant["nom"] or "",
                "quantite": composant["quantite"] or 1,
            })

    def composants_saisis(self):
        """
        Liste (produit_id, quantite) des lignes valides. Les
        lignes dont le code n'a pas été reconnu sont ignorées.
        """

        resultat = []

        for ligne in range(self.tableComposants.rowCount()):

            champCode = self.tableComposants.cellWidget(ligne, 0)
            quantite = self.tableComposants.cellWidget(ligne, 2)

            if champCode is None or champCode.produit_id is None:
                continue

            resultat.append(
                (champCode.produit_id, quantite.value())
            )

        return resultat

    def composants_non_reconnus(self):
        """
        Codes saisis qui ne correspondent à aucun produit —
        pour prévenir avant d'enregistrer plutôt que de les
        perdre en silence.
        """

        codes = []

        for ligne in range(self.tableComposants.rowCount()):

            champCode = self.tableComposants.cellWidget(ligne, 0)

            if champCode is None:
                continue

            if champCode.produit_id is None and champCode.text().strip():
                codes.append(champCode.text().strip())

        return codes

    def enregistrer_composants(self, bundle_id):
        """
        Écrit la composition en base. Appelé par l'écran
        Produits une fois la fiche enregistrée.
        """

        if not bundle_id:
            return

        if not self._estBundle:
            return

        StockManager().definir_composants(
            bundle_id,
            self.composants_saisis(),
        )

    def _majCouleurStatut(self):

        cle = self.statutStock.currentData() or "actif"

        _libelle, couleur = self.STATUTS.get(
            cle, self.STATUTS["actif"]
        )

        self.statutStock.setStyleSheet(
            f"color:{couleur}; font-weight:600;"
        )

    def statut_stock(self):

        return self.statutStock.currentData()

    def selectionner_statut_stock(self, statut):

        index = self.statutStock.findData(statut or "actif")

        if index >= 0:
            self.statutStock.setCurrentIndex(index)