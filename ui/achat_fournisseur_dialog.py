from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    QFrame,
    QGroupBox,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
    QSizePolicy,
)
from PySide6.QtCore import QDate

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.product_manager import ProductManager
from modules.variation_manager import VariationManager
from ui import theme


class AchatFournisseurDialog(QDialog):
    """
    Fenêtre de création/modification d'une commande passée à
    un fournisseur (achat de stock).
    """

    def __init__(self, titre, achat=None, lignes=None):

        super().__init__()

        self.achat = achat
        self.lignes_existantes = lignes or []

        self.productManager = ProductManager()
        self.variationManager = VariationManager()

        self.setWindowTitle(titre)
        # (taille fixée plus bas, une fois tout le contenu
        # de la fenêtre posé)

        # Le style vient du thème global (ui/theme.py).
        # Cette fenêtre prend la couleur du module Achats
        # Stocks, comme l'écran qui l'ouvre.
        self.accent = theme.accent_pour("achats stocks")
        self.setStyleSheet(theme.feuille_accent(self.accent))

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 16, 18, 16)

        carte = QFrame()
        carte.setObjectName("card")
        principal.addWidget(carte)

        layout = QVBoxLayout(carte)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Même repère coloré que les écrans de liste : on sait
        # d'un coup d'œil dans quel module on se trouve.
        entete = QHBoxLayout()
        entete.setSpacing(12)

        bandeau = QFrame()
        bandeau.setObjectName("bandeauAccent")
        bandeau.setFixedWidth(6)
        bandeau.setMinimumHeight(32)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")

        entete.addWidget(bandeau)
        entete.addWidget(titreLabel)
        entete.addStretch()

        layout.addLayout(entete)

        ####################################################
        # En-tête
        ####################################################

        groupeEntete = QGroupBox("Informations générales")
        formEntete = QFormLayout(groupeEntete)

        self.numero = QLineEdit()
        formEntete.addRow("Numéro de commande", self.numero)

        self.fournisseur = ReferenceComboBox("fournisseurs")
        formEntete.addRow("Fournisseur", self.fournisseur)

        self.dateAchat = QDateEdit()
        self.dateAchat.setCalendarPopup(True)
        self.dateAchat.setDate(QDate.currentDate())
        formEntete.addRow("Date de commande", self.dateAchat)

        self.dateReception = QDateEdit()
        self.dateReception.setCalendarPopup(True)
        self.dateReception.setDate(QDate.currentDate())
        formEntete.addRow(
            "Date de réception prévue/réelle", self.dateReception
        )

        self.statut = QComboBox()
        self.statut.addItems([
            "Commandé", "Expédié par le fournisseur",
            "Reçu", "Annulé"
        ])
        formEntete.addRow("Statut", self.statut)

        self.fraisPort = QDoubleSpinBox()
        self.fraisPort.setDecimals(2)
        self.fraisPort.setMaximum(9999)
        self.fraisPort.setSuffix(" € HT")
        formEntete.addRow("Frais de port", self.fraisPort)

        layout.addWidget(groupeEntete)

        ####################################################
        # Produits commandés
        ####################################################

        groupeProduits = QGroupBox("Produits commandés")
        layoutProduits = QVBoxLayout(groupeProduits)

        self.tableLignes = QTableWidget()
        self.tableLignes.setColumnCount(7)
        self.tableLignes.setHorizontalHeaderLabels([
            "Code EAN/SKU", "Produit", "Taille", "Qté",
            "Prix d'achat HT unitaire", "", ""
        ])

        entete_lignes = self.tableLignes.horizontalHeader()
        entete_lignes.setSectionResizeMode(0, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(1, QHeaderView.Stretch)
        entete_lignes.setSectionResizeMode(2, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(3, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(4, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(5, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(6, QHeaderView.Fixed)

        self.tableLignes.setColumnWidth(0, 150)
        self.tableLignes.setColumnWidth(2, 150)
        self.tableLignes.setColumnWidth(3, 70)
        self.tableLignes.setColumnWidth(4, 180)
        self.tableLignes.setColumnWidth(5, 150)
        self.tableLignes.setColumnWidth(6, 50)
        self.tableLignes.setMinimumHeight(200)

        layoutProduits.addWidget(self.tableLignes)

        self.btnAjouterLigne = QPushButton("+ Ajouter un produit")
        layoutProduits.addWidget(self.btnAjouterLigne)

        layout.addWidget(groupeProduits)

        ####################################################
        # Commentaire
        ####################################################

        groupeCommentaire = QGroupBox("Commentaire")
        layoutCommentaire = QVBoxLayout(groupeCommentaire)

        self.commentaire = QTextEdit()
        self.commentaire.setFixedHeight(60)
        layoutCommentaire.addWidget(self.commentaire)

        layout.addWidget(groupeCommentaire)

        ####################################################
        # Boutons
        ####################################################

        carteBoutons = QFrame()
        carteBoutons.setObjectName("barreOutils")

        boutons = QHBoxLayout(carteBoutons)
        boutons.setContentsMargins(14, 10, 14, 10)
        boutons.setSpacing(10)
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnAnnuler.setObjectName("btnSecondaire")

        self.btnEnregistrer = QPushButton("💾  Enregistrer l'achat")

        # Largeur figée : le libellé ne sera jamais rogné,
        # quelle que soit la taille de la fenêtre.
        for bouton in (self.btnAnnuler, self.btnEnregistrer):
            bouton.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed,
            )

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layout.addWidget(carteBoutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self._validerAvantAccept)

        self.btnAjouterLigne.clicked.connect(self.ajouterLigne)

        if self.achat is not None:
            self._chargerAchat()

        for ligne in self.lignes_existantes:
            self._ajouterLigneTableau(ligne)

        self._adapterTailleEcran(1000, 750)

    def _adapterTailleEcran(self, largeur_souhaitee, hauteur_souhaitee):
        """
        Force la taille de la fenêtre à rester dans les
        limites de l'écran — appelé en différé (juste après
        l'affichage), car Qt réajuste automatiquement la
        fenêtre à la taille de son contenu juste après un
        appel resize() classique, ce qui annulait sinon
        cette limite.
        """

        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer

        def appliquer():

            ecran_widget = self.screen() or QApplication.primaryScreen()
            ecran = ecran_widget.availableGeometry()

            largeur = min(largeur_souhaitee, ecran.width() - 60)
            hauteur = min(hauteur_souhaitee, ecran.height() - 100)

            self.resize(largeur, hauteur)

        QTimer.singleShot(0, appliquer)

    def _chargerAchat(self):

        self.numero.setText(self.achat["numero"] or "")
        self.fournisseur.selectionner(self.achat["fournisseur_id"])

        if self.achat["date_achat"]:
            self.dateAchat.setDate(
                QDate.fromString(self.achat["date_achat"], "yyyy-MM-dd")
            )

        if self.achat["date_reception"]:
            self.dateReception.setDate(
                QDate.fromString(self.achat["date_reception"], "yyyy-MM-dd")
            )

        index_statut = self.statut.findText(self.achat["statut"] or "Commandé")
        if index_statut >= 0:
            self.statut.setCurrentIndex(index_statut)

        self.fraisPort.setValue(self.achat["frais_port_ht"] or 0)
        self.commentaire.setPlainText(self.achat["commentaire"] or "")

    def ajouterLigne(self, donnees=None):

        ligne = self.tableLignes.rowCount()
        self.tableLignes.insertRow(ligne)

        champCode = QLineEdit()
        champCode.setPlaceholderText("EAN ou SKU, puis Entrée")
        champCode.produit_id = None

        labelProduit = QLabel("—")
        labelProduit.setStyleSheet("color:#64748b;")

        # Taille réceptionnée. Grisée tant que le produit n'a
        # pas de déclinaison : un mug n'a pas de taille.
        champTaille = QComboBox()
        champTaille.setEnabled(False)
        champTaille.addItem("—", None)

        spinQuantite = QSpinBox()
        spinQuantite.setMinimum(1)
        spinQuantite.setMaximum(99999)
        spinQuantite.setValue(1)

        spinPrixHt = QDoubleSpinBox()
        spinPrixHt.setDecimals(2)
        spinPrixHt.setMaximum(99999)

        btnSupprimer = QPushButton("🗑")
        btnSupprimer.setMaximumWidth(40)
        btnSupprimer.clicked.connect(
            lambda: self._supprimerLigneTableau(btnSupprimer)
        )

        btnCreerProduit = QPushButton("+ Créer ce produit")
        btnCreerProduit.setVisible(False)
        # Orange assombri : en #e67e22, le texte blanc tombait
        # à 2,9 de contraste, sous le minimum lisible de 4,5.
        btnCreerProduit.setStyleSheet(
            "background:#b35c10; min-width:0; padding:4px 8px;"
        )
        btnCreerProduit.setMinimumHeight(30)

        def remplir_tailles(produit_id):
            """
            Propose les tailles du produit. Sans elle, une
            réception créditerait le produit entier et aucune
            taille précise.
            """

            champTaille.clear()

            variations = self.variationManager.variations(
                produit_id, actives_seulement=True
            )

            if not variations:
                champTaille.addItem("—", None)
                champTaille.setEnabled(False)
                return

            champTaille.addItem("— à choisir —", None)

            for variation in variations:
                champTaille.addItem(
                    variation["libelle"] or "", variation["id"]
                )

            champTaille.setEnabled(True)

        def appliquer_taille():

            variation_id = champTaille.currentData()

            if not variation_id:
                return

            variation = self.variationManager.obtenir(variation_id)

            if variation is not None and variation["prix_achat_ht"]:
                spinPrixHt.setValue(variation["prix_achat_ht"])

        champTaille.currentIndexChanged.connect(appliquer_taille)

        def rechercher_produit():

            code = champCode.text().strip()

            if not code:
                return

            try:
                produit = self.productManager.trouver_par_code(code)
            except Exception:
                labelProduit.setText("⚠ Erreur technique")
                labelProduit.setStyleSheet("color:#c0392b;")
                return

            if produit is None:
                labelProduit.setText("❌ Introuvable")
                labelProduit.setStyleSheet("color:#c0392b;")
                champCode.produit_id = None
                btnCreerProduit.setVisible(True)
                return

            btnCreerProduit.setVisible(False)
            champCode.produit_id = produit["id"]
            labelProduit.setText(produit["nom"] or "")
            labelProduit.setStyleSheet("color:#2c3e50;")
            remplir_tailles(produit["id"])
            spinPrixHt.setValue(produit["prix_fournisseur_ht"] or 0)

        def creer_produit():

            from ui.product_type_dialog import ProductTypeDialog
            from ui.product_dialog_v2 import ProductDialogV2

            choix = ProductTypeDialog()

            if choix.exec() != choix.DialogCode.Accepted:
                return

            dialog = ProductDialogV2(
                type_produit=choix.typeProduit(),
                nom_prerempli=f"Produit {champCode.text().strip()}",
                prix_achat_prerempli=spinPrixHt.value(),
                code_prerempli=champCode.text().strip(),
            )

            if dialog.exec() != dialog.DialogCode.Accepted:
                return

            # Une fois créé, on relance la recherche pour lier
            # automatiquement cette ligne au produit tout juste
            # créé.
            rechercher_produit()

        btnCreerProduit.clicked.connect(creer_produit)

        champCode.returnPressed.connect(rechercher_produit)

        # Le thème habille déjà les champs posés dans une
        # cellule ; il ne reste qu'à leur donner une hauteur
        # confortable, comme dans la fenêtre Commande.
        for widget in (champCode, spinQuantite, spinPrixHt):
            widget.setMinimumHeight(30)

        self.tableLignes.setCellWidget(ligne, 0, champCode)
        self.tableLignes.setCellWidget(ligne, 1, labelProduit)
        self.tableLignes.setCellWidget(ligne, 2, champTaille)
        self.tableLignes.setCellWidget(ligne, 3, spinQuantite)
        self.tableLignes.setCellWidget(ligne, 4, spinPrixHt)
        self.tableLignes.setCellWidget(ligne, 5, btnCreerProduit)
        self.tableLignes.setCellWidget(ligne, 6, btnSupprimer)

        if donnees:

            if donnees.get("produit_id"):

                champCode.produit_id = donnees["produit_id"]
                produit = self.productManager.obtenir(donnees["produit_id"])

                if produit:
                    champCode.setText(produit["ean"] or produit["sku"] or "")

                remplir_tailles(donnees["produit_id"])

                if donnees.get("variation_id"):

                    index = champTaille.findData(donnees["variation_id"])

                    if index >= 0:
                        champTaille.setCurrentIndex(index)

            labelProduit.setText(donnees.get("nom_produit") or "—")
            labelProduit.setStyleSheet("color:#2c3e50;")
            spinQuantite.setValue(donnees.get("quantite", 1))
            spinPrixHt.setValue(donnees.get("prix_unitaire_ht") or 0)

    def _ajouterLigneTableau(self, ligne_bdd):

        self.ajouterLigne(donnees=dict(ligne_bdd))

    def _supprimerLigneTableau(self, bouton):

        for ligne in range(self.tableLignes.rowCount()):

            if self.tableLignes.cellWidget(ligne, 6) == bouton:
                self.tableLignes.removeRow(ligne)
                return

    def lignes_saisies(self):

        resultat = []

        for ligne in range(self.tableLignes.rowCount()):

            champCode = self.tableLignes.cellWidget(ligne, 0)
            labelProduit = self.tableLignes.cellWidget(ligne, 1)
            champTaille = self.tableLignes.cellWidget(ligne, 2)
            spinQuantite = self.tableLignes.cellWidget(ligne, 3)
            spinPrixHt = self.tableLignes.cellWidget(ligne, 4)

            resultat.append({
                "produit_id": champCode.produit_id,
                "variation_id": champTaille.currentData(),
                "nom_produit": labelProduit.text(),
                "quantite": spinQuantite.value(),
                "prix_unitaire_ht": spinPrixHt.value(),
            })

        return resultat

    def _validerAvantAccept(self):

        from PySide6.QtWidgets import QMessageBox

        if self.numero.text().strip() == "":

            QMessageBox.warning(
                self, "Numéro manquant",
                "Le numéro de commande est obligatoire."
            )
            return

        if self.fournisseur.id() is None:

            QMessageBox.warning(
                self, "Fournisseur manquant",
                "Sélectionne un fournisseur."
            )
            return

        # Sans taille précisée, la réception créditerait le
        # produit entier : on ne saurait pas combien de XL
        # sont réellement arrivés.
        tailles_manquantes = []

        for ligne in range(self.tableLignes.rowCount()):

            champTaille = self.tableLignes.cellWidget(ligne, 2)
            labelProduit = self.tableLignes.cellWidget(ligne, 1)

            if champTaille is None or not champTaille.isEnabled():
                continue

            if champTaille.currentData() is None:
                tailles_manquantes.append(
                    labelProduit.text() or f"ligne {ligne + 1}"
                )

        if tailles_manquantes:

            QMessageBox.warning(
                self, "Taille non choisie",
                "Ces produits existent en plusieurs tailles, il "
                "faut dire laquelle est réceptionnée :\n\n"
                + "\n".join(f"   • {n}" for n in tailles_manquantes)
                + "\n\nUne ligne par taille : ajoute autant de "
                "lignes que de tailles reçues."
            )
            return

        self.accept()