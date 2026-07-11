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
)
from PySide6.QtCore import QDate

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.product_manager import ProductManager


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

        self.setWindowTitle(titre)
        # (taille fixée plus bas, une fois tout le contenu
        # de la fenêtre posé)

        self.setStyleSheet("""
            QDialog{
                background:#f4f7fb;
                font-family:"Segoe UI";
            }

            QFrame#card{
                background:white;
                border:1px solid #e1e8f0;
                border-radius:12px;
            }

            QLabel#titre{
                font-size:22px;
                font-weight:600;
                color:#0f2f5c;
            }

            QGroupBox{
                font-weight:600;
                color:#0f2f5c;
                background:#fbfcfe;
                border:1px solid #e1e8f0;
                border-radius:10px;
                margin-top:12px;
                padding-top:12px;
            }

            QGroupBox::title{
                subcontrol-origin:margin;
                left:12px;
                padding:0 8px;
            }

            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
            QSpinBox, QTextEdit{
                background:#f7f9fc;
                border:1px solid #d7e0ec;
                border-radius:7px;
                padding:6px 8px;
                font-size:10.5pt;
                color:#1c2b3a;
            }

            QSpinBox::up-button, QDoubleSpinBox::up-button{
                subcontrol-origin:border;
                subcontrol-position:top right;
                width:18px;
                border-left:1px solid #d7e0ec;
                border-bottom:1px solid #d7e0ec;
                border-top-right-radius:7px;
                background:#eef2f8;
            }

            QSpinBox::down-button, QDoubleSpinBox::down-button{
                subcontrol-origin:border;
                subcontrol-position:bottom right;
                width:18px;
                border-left:1px solid #d7e0ec;
                border-bottom-right-radius:7px;
                background:#eef2f8;
            }

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover{
                background:#dbe7f7;
            }

            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow{
                image:none;
                border-left:4px solid transparent;
                border-right:4px solid transparent;
                border-bottom:5px solid #144b8b;
                width:0;
                height:0;
            }

            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow{
                image:none;
                border-left:4px solid transparent;
                border-right:4px solid transparent;
                border-top:5px solid #144b8b;
                width:0;
                height:0;
            }

            QPushButton{
                background:#144b8b;
                color:white;
                border:none;
                border-radius:8px;
                padding:8px 16px;
                font-weight:500;
            }

            QPushButton:hover{
                background:#1d61b4;
            }

            QTableWidget{
                background:white;
                gridline-color:#eef1f6;
                alternate-background-color:#f8fafc;
            }

            QHeaderView::section{
                background:#0f2f5c;
                color:white;
                font-weight:600;
                border:none;
                padding:8px 6px;
            }
        """)

        principal = QVBoxLayout(self)

        carte = QFrame()
        carte.setObjectName("card")
        principal.addWidget(carte)

        layout = QVBoxLayout(carte)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")
        layout.addWidget(titreLabel)

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
        self.tableLignes.setColumnCount(6)
        self.tableLignes.setHorizontalHeaderLabels([
            "Code EAN/SKU", "Produit", "Qté",
            "Prix d'achat HT unitaire", "", ""
        ])
        self.tableLignes.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
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

        boutons = QHBoxLayout()
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layout.addLayout(boutons)

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
        labelProduit.setStyleSheet("color:#7f8c8d;")

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
        btnCreerProduit.setStyleSheet(
            "background:#e67e22; min-width:0; padding:4px 8px;"
        )

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

        self.tableLignes.setCellWidget(ligne, 0, champCode)
        self.tableLignes.setCellWidget(ligne, 1, labelProduit)
        self.tableLignes.setCellWidget(ligne, 2, spinQuantite)
        self.tableLignes.setCellWidget(ligne, 3, spinPrixHt)
        self.tableLignes.setCellWidget(ligne, 4, btnCreerProduit)
        self.tableLignes.setCellWidget(ligne, 5, btnSupprimer)

        if donnees:

            if donnees.get("produit_id"):

                champCode.produit_id = donnees["produit_id"]
                produit = self.productManager.obtenir(donnees["produit_id"])

                if produit:
                    champCode.setText(produit["ean"] or produit["sku"] or "")

            labelProduit.setText(donnees.get("nom_produit") or "—")
            labelProduit.setStyleSheet("color:#2c3e50;")
            spinQuantite.setValue(donnees.get("quantite", 1))
            spinPrixHt.setValue(donnees.get("prix_unitaire_ht") or 0)

    def _ajouterLigneTableau(self, ligne_bdd):

        self.ajouterLigne(donnees=dict(ligne_bdd))

    def _supprimerLigneTableau(self, bouton):

        for ligne in range(self.tableLignes.rowCount()):

            if self.tableLignes.cellWidget(ligne, 5) == bouton:
                self.tableLignes.removeRow(ligne)
                return

    def lignes_saisies(self):

        resultat = []

        for ligne in range(self.tableLignes.rowCount()):

            champCode = self.tableLignes.cellWidget(ligne, 0)
            labelProduit = self.tableLignes.cellWidget(ligne, 1)
            spinQuantite = self.tableLignes.cellWidget(ligne, 2)
            spinPrixHt = self.tableLignes.cellWidget(ligne, 3)

            resultat.append({
                "produit_id": champCode.produit_id,
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

        self.accept()