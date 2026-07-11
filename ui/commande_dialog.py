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
    QScrollArea,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QTextEdit,
    QCheckBox,
)
from PySide6.QtCore import QDate

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.client_manager import ClientManager
from modules.product_manager import ProductManager


class CommandeDialog(QDialog):
    """
    Fenêtre de création/modification d'une commande :
    en-tête (client, canal, dates, frais de port client vs
    réel), panier (lignes de produits, ajout/suppression
    dynamique) et retours (par ligne de produit).
    """

    def __init__(self, titre, commande=None, lignes=None, retours=None):

        super().__init__()

        self.commande = commande
        self.lignes_existantes = lignes or []
        self.retours_existants = retours or []

        self.clientManager = ClientManager()
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
                font-size:10.5pt;
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

            QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
            QDoubleSpinBox:focus, QSpinBox:focus, QTextEdit:focus{
                border:1px solid #144b8b;
                background:white;
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

            QCheckBox{
                font-size:10.5pt;
                color:#1c2b3a;
                spacing:8px;
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

            QPushButton:pressed{
                background:#0d3a6e;
            }

            QTableWidget{
                background:white;
                gridline-color:#eef1f6;
                alternate-background-color:#f8fafc;
                selection-background-color:#dbe7f7;
                selection-color:#0f2f5c;
            }

            QTableWidget::item{
                padding:6px;
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

        layoutCarte = QVBoxLayout(carte)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")
        layoutCarte.addWidget(titreLabel)

        zoneDefilement = QScrollArea()
        zoneDefilement.setWidgetResizable(True)
        zoneDefilement.setStyleSheet("border:none;")

        contenu = QWidget()
        layout = QVBoxLayout(contenu)

        ####################################################
        # En-tête commande
        ####################################################

        groupeEntete = QGroupBox("Informations générales")
        formEntete = QFormLayout(groupeEntete)

        self.numero = QLineEdit()
        formEntete.addRow("Numéro de commande", self.numero)

        self.canal = ReferenceComboBox("canaux_vente")
        formEntete.addRow("Canal de vente", self.canal)

        ligneClient = QHBoxLayout()
        self.client = QComboBox()
        self._rechargerClients()
        ligneClient.addWidget(self.client)
        self.btnNouveauClient = QPushButton("+ Nouveau client")
        ligneClient.addWidget(self.btnNouveauClient)
        formEntete.addRow("Client", ligneClient)

        self.dateCommande = QDateEdit()
        self.dateCommande.setCalendarPopup(True)
        self.dateCommande.setDate(QDate.currentDate())
        formEntete.addRow("Date de commande", self.dateCommande)

        ligneExpedition = QHBoxLayout()

        self.dejaExpediee = QCheckBox("Déjà expédiée")

        self.dateExpedition = QDateEdit()
        self.dateExpedition.setCalendarPopup(True)
        self.dateExpedition.setDate(QDate.currentDate())
        self.dateExpedition.setEnabled(False)

        self.dejaExpediee.toggled.connect(
            self.dateExpedition.setEnabled
        )

        ligneExpedition.addWidget(self.dejaExpediee)
        ligneExpedition.addWidget(self.dateExpedition)

        formEntete.addRow("Date d'expédition", ligneExpedition)

        self.statut = QComboBox()
        self.statut.addItems([
            "En cours", "Expédiée", "Livrée", "Annulée"
        ])
        formEntete.addRow("Statut", self.statut)

        self.tracking = QLineEdit()
        formEntete.addRow("Numéro de suivi", self.tracking)

        layout.addWidget(groupeEntete)

        ####################################################
        # Frais de port
        ####################################################

        groupePort = QGroupBox(
            "Frais de port — bien distincts : ce que le "
            "client a payé, et ce que ça t'a réellement coûté"
        )
        formPort = QFormLayout(groupePort)

        self.fraisPortClient = QDoubleSpinBox()
        self.fraisPortClient.setDecimals(2)
        self.fraisPortClient.setMaximum(9999)
        self.fraisPortClient.setSuffix(" € TTC")
        formPort.addRow(
            "Payé par le client", self.fraisPortClient
        )

        self.fraisPortReel = QDoubleSpinBox()
        self.fraisPortReel.setDecimals(2)
        self.fraisPortReel.setMaximum(9999)
        self.fraisPortReel.setSuffix(" € HT")
        formPort.addRow(
            "Coût réel du transport", self.fraisPortReel
        )

        layout.addWidget(groupePort)

        ####################################################
        # Panier (lignes de produits)
        ####################################################

        groupePanier = QGroupBox("Produits achetés")
        layoutPanier = QVBoxLayout(groupePanier)

        self.tableLignes = QTableWidget()
        self.tableLignes.setColumnCount(7)
        self.tableLignes.setHorizontalHeaderLabels([
            "Code EAN/SKU", "Produit", "Qté", "Prix vente HT",
            "Prix vente TTC", "Coût achat HT unitaire", ""
        ])
        self.tableLignes.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableLignes.setMinimumHeight(180)

        layoutPanier.addWidget(self.tableLignes)

        self.labelInfoPrix = QLabel("")
        self.labelInfoPrix.setWordWrap(True)
        layoutPanier.addWidget(self.labelInfoPrix)

        self.btnAjouterLigne = QPushButton("+ Ajouter un produit")
        layoutPanier.addWidget(self.btnAjouterLigne)

        layout.addWidget(groupePanier)

        ####################################################
        # Retours
        ####################################################

        groupeRetours = QGroupBox("Retours")
        layoutRetours = QVBoxLayout(groupeRetours)

        self.tableRetours = QTableWidget()
        self.tableRetours.setColumnCount(7)
        self.tableRetours.setHorizontalHeaderLabels([
            "Produit concerné", "Date", "Motif", "Statut",
            "Remboursé TTC", "Coût retour HT", ""
        ])
        self.tableRetours.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableRetours.setMinimumHeight(140)

        layoutRetours.addWidget(self.tableRetours)

        self.btnAjouterRetour = QPushButton("+ Signaler un retour")
        layoutRetours.addWidget(self.btnAjouterRetour)

        layout.addWidget(groupeRetours)

        ####################################################
        # Emballage cadeau
        ####################################################

        groupeCadeau = QGroupBox("🎁 Emballage cadeau")
        formCadeau = QFormLayout(groupeCadeau)

        self.papierCadeauActif = QCheckBox(
            "Cette commande inclut un emballage cadeau"
        )
        self.papierCadeauActif.toggled.connect(
            self._basculerEmballageCadeau
        )
        formCadeau.addRow("", self.papierCadeauActif)

        self.papierCadeauEmballage = QComboBox()

        from modules.emballage_cadeau_manager import (
            EmballageCadeauManager
        )

        self._emballageCadeauManager = EmballageCadeauManager()

        for e in self._emballageCadeauManager.principaux():

            self.papierCadeauEmballage.addItem(
                f"{e['code']} — {e['nom']} "
                f"({e['tarif_facture_ht']:.2f}€ HT facturé)",
                e["id"]
            )

        formCadeau.addRow(
            "Emballage choisi (facturé au client)",
            self.papierCadeauEmballage
        )

        self.papierCadeauSupplement = QComboBox()
        self.papierCadeauSupplement.addItem("Aucun", None)

        for e in self._emballageCadeauManager.supplements():

            self.papierCadeauSupplement.addItem(
                f"{e['code']} — {e['nom']} "
                f"(+{e['cout_ht']:.2f}€ HT de coût)",
                e["id"]
            )

        formCadeau.addRow(
            "Supplément (papier de soie, étiquette...)",
            self.papierCadeauSupplement
        )

        layout.addWidget(groupeCadeau)

        self.papierCadeauEmballage.setEnabled(False)
        self.papierCadeauSupplement.setEnabled(False)

        ####################################################
        # Commentaire
        ####################################################

        groupeCommentaire = QGroupBox("Commentaire")
        layoutCommentaire = QVBoxLayout(groupeCommentaire)

        self.commentaire = QTextEdit()
        self.commentaire.setFixedHeight(70)
        layoutCommentaire.addWidget(self.commentaire)

        layout.addWidget(groupeCommentaire)

        layout.addStretch()

        zoneDefilement.setWidget(contenu)
        layoutCarte.addWidget(zoneDefilement)

        ####################################################
        # Boutons
        ####################################################

        boutons = QHBoxLayout()
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layoutCarte.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self._validerAvantAccept)

        self.btnAjouterLigne.clicked.connect(self.ajouterLigne)
        self.btnNouveauClient.clicked.connect(self.creerClient)
        self.btnAjouterRetour.clicked.connect(self.ajouterRetour)

        ####################################################
        # Pré-remplissage si modification
        ####################################################

        if self.commande is not None:
            self._chargerCommande()

        for ligne in self.lignes_existantes:
            self._ajouterLigneTableau(ligne)

        for retour in self.retours_existants:
            self._ajouterRetourTableau(retour)

        self._adapterTailleEcran(1250, 850)

    def _basculerEmballageCadeau(self, actif):

        self.papierCadeauEmballage.setEnabled(actif)
        self.papierCadeauSupplement.setEnabled(actif)

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

    def _rechargerClients(self):

        self.client.clear()
        self.client.addItem("", None)

        for client in self.clientManager.tous():

            nom_complet = f"{client['prenom'] or ''} {client['nom'] or ''}".strip()

            self.client.addItem(nom_complet, client["id"])

    def _chargerCommande(self):

        self.numero.setText(self.commande["numero"] or "")

        self.canal.selectionner(self.commande["canal_id"])

        for i in range(self.client.count()):
            if self.client.itemData(i) == self.commande["client_id"]:
                self.client.setCurrentIndex(i)
                break

        if self.commande["date_commande"]:
            self.dateCommande.setDate(
                QDate.fromString(self.commande["date_commande"], "yyyy-MM-dd")
            )

        if self.commande["date_expedition"]:
            self.dejaExpediee.setChecked(True)
            self.dateExpedition.setDate(
                QDate.fromString(self.commande["date_expedition"], "yyyy-MM-dd")
            )

        index_statut = self.statut.findText(self.commande["statut"] or "En cours")
        if index_statut >= 0:
            self.statut.setCurrentIndex(index_statut)

        self.tracking.setText(self.commande["tracking"] or "")
        self.fraisPortClient.setValue(self.commande["frais_port_client_ttc"] or 0)
        self.fraisPortReel.setValue(self.commande["frais_port_reel_ht"] or 0)
        self.commentaire.setPlainText(self.commande["commentaire"] or "")

        self.papierCadeauActif.setChecked(
            bool(self.commande["papier_cadeau_actif"])
        )

        if self.commande["papier_cadeau_emballage_id"]:

            index = self.papierCadeauEmballage.findData(
                self.commande["papier_cadeau_emballage_id"]
            )
            if index >= 0:
                self.papierCadeauEmballage.setCurrentIndex(index)

        if self.commande["papier_cadeau_supplement_id"]:

            index = self.papierCadeauSupplement.findData(
                self.commande["papier_cadeau_supplement_id"]
            )
            if index >= 0:
                self.papierCadeauSupplement.setCurrentIndex(index)

    def creerClient(self):

        from ui.client_dialog import ClientDialog

        dialog = ClientDialog("Nouveau client")

        if dialog.exec() != ClientDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        nouvel_id = self.clientManager.ajouter(
            nom,
            dialog.prenom.text(),
            dialog.societe.text(),
            dialog.email.text(),
            dialog.telephone.text(),
            dialog.adresse.text(),
            dialog.codePostal.text(),
            dialog.ville.text(),
            dialog.pays.text() or "France"
        )

        self._rechargerClients()

        for i in range(self.client.count()):
            if self.client.itemData(i) == nouvel_id:
                self.client.setCurrentIndex(i)
                break

    ####################################################
    # Lignes de produits (panier)
    ####################################################

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
        spinQuantite.setMaximum(9999)
        spinQuantite.setValue(1)

        spinPrixHt = QDoubleSpinBox()
        spinPrixHt.setDecimals(2)
        spinPrixHt.setMaximum(99999)

        spinPrixTtc = QDoubleSpinBox()
        spinPrixTtc.setDecimals(2)
        spinPrixTtc.setMaximum(99999)

        spinCoutAchat = QDoubleSpinBox()
        spinCoutAchat.setDecimals(2)
        spinCoutAchat.setMaximum(99999)

        btnSupprimer = QPushButton("🗑")
        btnSupprimer.setMaximumWidth(40)
        btnSupprimer.clicked.connect(
            lambda: self._supprimerLigneTableau(btnSupprimer)
        )

        def rechercher_produit():

            code = champCode.text().strip()

            if not code:
                return

            try:

                produit = self.productManager.trouver_par_code(code)

            except Exception as erreur:

                # Ne jamais échouer en silence : une erreur ici
                # doit se voir, pas juste laisser le champ vide
                # sans explication.
                labelProduit.setText("⚠ Erreur technique")
                labelProduit.setStyleSheet("color:#c0392b;")
                self.labelInfoPrix.setText(
                    f"⚠ Erreur lors de la recherche du produit : "
                    f"{erreur}"
                )
                self.labelInfoPrix.setStyleSheet("color:#c0392b;")
                return

            if produit is None:

                labelProduit.setText("❌ Introuvable")
                labelProduit.setStyleSheet("color:#c0392b;")
                champCode.produit_id = None
                return

            champCode.produit_id = produit["id"]

            labelProduit.setText(produit["nom"] or "")
            labelProduit.setStyleSheet("color:#2c3e50;")

            spinCoutAchat.setValue(produit["prix_fournisseur_ht"] or 0)

            self._suggererPrixVente(
                produit, spinPrixHt, spinPrixTtc, self.labelInfoPrix
            )

        champCode.returnPressed.connect(rechercher_produit)

        self.tableLignes.setCellWidget(ligne, 0, champCode)
        self.tableLignes.setCellWidget(ligne, 1, labelProduit)
        self.tableLignes.setCellWidget(ligne, 2, spinQuantite)
        self.tableLignes.setCellWidget(ligne, 3, spinPrixHt)
        self.tableLignes.setCellWidget(ligne, 4, spinPrixTtc)
        self.tableLignes.setCellWidget(ligne, 5, spinCoutAchat)
        self.tableLignes.setCellWidget(ligne, 6, btnSupprimer)

        if donnees:

            if donnees.get("produit_id"):

                champCode.produit_id = donnees["produit_id"]
                produit = self.productManager.obtenir(donnees["produit_id"])

                if produit:
                    champCode.setText(produit["ean"] or produit["sku"] or "")

            labelProduit.setText(
                donnees.get("nom_produit") or "—"
            )
            labelProduit.setStyleSheet("color:#2c3e50;")

            spinQuantite.setValue(donnees.get("quantite", 1))
            spinPrixHt.setValue(donnees.get("prix_unitaire_ht") or 0)
            spinPrixTtc.setValue(donnees.get("prix_unitaire_ttc") or 0)
            spinCoutAchat.setValue(donnees.get("cout_achat_unitaire_ht") or 0)

    def _suggererPrixVente(self, produit, spinPrixHt, spinPrixTtc, labelInfo=None):
        """
        Propose automatiquement le prix de vente calculé
        pour ce produit sur le canal actuellement sélectionné
        dans l'en-tête de la commande — reste modifiable si
        le prix réellement pratiqué a différé (promo,
        négociation...).

        Si le calcul échoue (canal mal configuré, catégorie
        manquante...), le champ reste à 0 mais labelInfo
        explique pourquoi — jamais d'échec silencieux.
        """

        canal_id = self.canal.id()

        if canal_id is None:

            if labelInfo:
                labelInfo.setText(
                    "⚠ Sélectionne d'abord un canal de vente "
                    "pour que le prix se propose automatiquement."
                )
                labelInfo.setStyleSheet("color:#b9770e;")
            return

        try:

            from modules.moteur_prix import MoteurPrix

            categories_canaux = self.productManager.categories_canaux(
                produit["id"]
            )
            categorie_id = categories_canaux.get(canal_id)

            # La marge spécifique à ce canal prime sur la
            # marge par défaut du produit — même règle que
            # dans l'onglet Tarification de la fiche produit.
            # Sans ça, une marge personnalisée par canal
            # n'était jamais prise en compte ici.
            marges_par_canal = self.productManager.marges_par_canal(
                produit["id"]
            )

            produit_pour_calcul = dict(produit)

            if canal_id in marges_par_canal:
                produit_pour_calcul["marge_visee_pourcentage"] = (
                    marges_par_canal[canal_id]
                )

            resultat = MoteurPrix().calculer(
                produit_pour_calcul, canal_id, categorie_id
            )

            if resultat.get("erreur"):

                if labelInfo:
                    labelInfo.setText(
                        f"⚠ Prix non calculable automatiquement : "
                        f"{resultat['erreur']} — saisis-le à la main."
                    )
                    labelInfo.setStyleSheet("color:#b9770e;")
                return

            spinPrixTtc.setValue(resultat.get("prix_vente_ttc") or 0)
            spinPrixHt.setValue(resultat.get("prix_vente_ht") or 0)

            if labelInfo:
                labelInfo.setText("")

        except Exception as erreur:

            if labelInfo:
                labelInfo.setText(
                    f"⚠ Prix non calculable automatiquement "
                    f"({erreur}) — saisis-le à la main."
                )
                labelInfo.setStyleSheet("color:#b9770e;")

    def _ajouterLigneTableau(self, ligne_bdd):

        self.ajouterLigne(donnees=dict(ligne_bdd))

    def _supprimerLigneTableau(self, bouton):

        for ligne in range(self.tableLignes.rowCount()):

            if self.tableLignes.cellWidget(ligne, 6) == bouton:
                self.tableLignes.removeRow(ligne)
                return

    def lignes_saisies(self):
        """
        Renvoie la liste des lignes du panier telles que
        saisies à l'écran, prêtes à être enregistrées.
        """

        resultat = []

        for ligne in range(self.tableLignes.rowCount()):

            champCode = self.tableLignes.cellWidget(ligne, 0)
            labelProduit = self.tableLignes.cellWidget(ligne, 1)
            spinQuantite = self.tableLignes.cellWidget(ligne, 2)
            spinPrixHt = self.tableLignes.cellWidget(ligne, 3)
            spinPrixTtc = self.tableLignes.cellWidget(ligne, 4)
            spinCoutAchat = self.tableLignes.cellWidget(ligne, 5)

            resultat.append({
                "produit_id": champCode.produit_id,
                "nom_produit": labelProduit.text(),
                "quantite": spinQuantite.value(),
                "prix_unitaire_ht": spinPrixHt.value(),
                "prix_unitaire_ttc": spinPrixTtc.value(),
                "cout_achat_unitaire_ht": spinCoutAchat.value(),
                "remise_ht": 0,
                "tva": 20,
            })

        return resultat

    ####################################################
    # Retours
    ####################################################

    def ajouterRetour(self):

        if self.tableLignes.rowCount() == 0:

            QMessageBox.information(
                self,
                "Information",
                "Ajoute d'abord au moins un produit dans le "
                "panier avant de signaler un retour."
            )
            return

        from ui.retour_dialog import RetourDialog

        produits = []

        for ligne in range(self.tableLignes.rowCount()):

            label = self.tableLignes.cellWidget(ligne, 1)
            produits.append(label.text() or "Produit sans nom")

        dialog = RetourDialog("Nouveau retour", produits)

        if dialog.exec() != RetourDialog.DialogCode.Accepted:
            return

        self._ajouterRetourTableau({
            "produit_index": dialog.produit.currentIndex(),
            "produit_nom": dialog.produit.currentText(),
            "date_retour": dialog.dateRetour.date().toString("yyyy-MM-dd"),
            "motif": dialog.motif.text(),
            "statut": dialog.statut.currentText(),
            "montant_rembourse_ttc": dialog.montantRembourse.value(),
            "cout_retour_ht": dialog.coutRetour.value(),
            "frais_reexpedition_ht": dialog.fraisReexpedition.value(),
            "notes": dialog.notes.toPlainText(),
        })

    def _ajouterRetourTableau(self, donnees):

        ligne = self.tableRetours.rowCount()
        self.tableRetours.insertRow(ligne)

        nom_produit = donnees.get("nom_produit") or donnees.get("produit_nom", "")

        valeurs = [
            nom_produit,
            donnees.get("date_retour", ""),
            donnees.get("motif", ""),
            donnees.get("statut", ""),
            f"{donnees.get('montant_rembourse_ttc', 0):.2f} €",
            f"{donnees.get('cout_retour_ht', 0):.2f} €",
        ]

        for colonne, valeur in enumerate(valeurs):
            self.tableRetours.setItem(
                ligne, colonne, QTableWidgetItem(str(valeur))
            )

        btnSupprimer = QPushButton("🗑")
        btnSupprimer.setMaximumWidth(40)
        btnSupprimer.clicked.connect(
            lambda: self._supprimerRetourTableau(btnSupprimer)
        )
        self.tableRetours.setCellWidget(ligne, 6, btnSupprimer)

        self._donnees_retours = getattr(self, "_donnees_retours", [])
        self._donnees_retours.append(donnees)

    def _supprimerRetourTableau(self, bouton):

        for ligne in range(self.tableRetours.rowCount()):

            if self.tableRetours.cellWidget(ligne, 6) == bouton:
                self.tableRetours.removeRow(ligne)
                return

    def retours_saisis(self):

        return getattr(self, "_donnees_retours", [])

    def _validerAvantAccept(self):

        if self.numero.text().strip() == "":

            QMessageBox.warning(
                self,
                "Numéro manquant",
                "Le numéro de commande est obligatoire."
            )
            return

        if self.tableLignes.rowCount() == 0:

            QMessageBox.warning(
                self,
                "Panier vide",
                "Ajoute au moins un produit à la commande."
            )
            return

        self.accept()