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
    QSizePolicy,
    QFileDialog,
    QInputDialog,
)
from PySide6.QtCore import QDate, Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices

from ui.widgets.reference_combobox import ReferenceComboBox
from modules.client_manager import ClientManager
from modules.product_manager import ProductManager
from modules.variation_manager import VariationManager
from modules.photo_commande_manager import PhotoCommandeManager
from ui import theme


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
        self.variationManager = VariationManager()
        self.photoManager = PhotoCommandeManager()

        self.setWindowTitle(titre)
        # (taille fixée plus bas, une fois tout le contenu
        # de la fenêtre posé)

        # Le style vient du thème global (ui/theme.py).
        # Cette fenêtre prend la couleur du module
        # Commandes, comme l'écran qui l'ouvre.
        #
        # Son ancienne feuille locale contenait une règle
        # QTableWidget::item : c'est elle qui empêchait Qt
        # de dessiner les couleurs posées sur les cellules
        # dans le code.
        self.accent = theme.accent_pour("commandes")
        self.setStyleSheet(theme.feuille_accent(self.accent))

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 16, 18, 16)

        carte = QFrame()
        carte.setObjectName("card")
        principal.addWidget(carte)

        layoutCarte = QVBoxLayout(carte)
        layoutCarte.setContentsMargins(18, 16, 18, 16)
        layoutCarte.setSpacing(12)

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

        layoutCarte.addLayout(entete)

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

        ligneEncaissement = QHBoxLayout()

        self.commandePayee = QCheckBox(
            "💰 Commande payée (argent réellement reçu)"
        )
        self.commandePayee.toggled.connect(self._basculerDatePaiement)
        ligneEncaissement.addWidget(self.commandePayee)

        self.datePaiement = QDateEdit()
        self.datePaiement.setCalendarPopup(True)
        self.datePaiement.setDate(QDate.currentDate())
        self.datePaiement.setEnabled(False)
        ligneEncaissement.addWidget(self.datePaiement)

        formEntete.addRow("Encaissement", ligneEncaissement)

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
        self.tableLignes.setColumnCount(8)
        self.tableLignes.setHorizontalHeaderLabels([
            "Code EAN/SKU", "Produit", "Taille", "Qté",
            "Prix vente HT", "Prix vente TTC",
            "Coût achat HT unitaire", ""
        ])

        entete_lignes = self.tableLignes.horizontalHeader()

        # Seule la colonne "Produit" s'étire pour occuper
        # l'espace restant — toutes les autres gardent une
        # largeur fixe suffisante pour que les chiffres (avec
        # leurs flèches +/-) ne soient jamais écrasés.
        entete_lignes.setSectionResizeMode(0, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(1, QHeaderView.Stretch)
        entete_lignes.setSectionResizeMode(2, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(3, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(4, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(5, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(6, QHeaderView.Fixed)
        entete_lignes.setSectionResizeMode(7, QHeaderView.Fixed)

        self.tableLignes.setColumnWidth(0, 140)
        self.tableLignes.setColumnWidth(2, 150)
        self.tableLignes.setColumnWidth(3, 70)
        self.tableLignes.setColumnWidth(4, 130)
        self.tableLignes.setColumnWidth(5, 130)
        self.tableLignes.setColumnWidth(6, 150)
        self.tableLignes.setColumnWidth(7, 50)

        self.tableLignes.setMinimumHeight(180)

        # Le bouton est placé AVANT le tableau : sur un écran
        # peu haut, il se retrouvait sous le tableau, hors du
        # champ visible, et devenait introuvable.
        self.btnAjouterLigne = QPushButton("+ Ajouter un produit")
        layoutPanier.addWidget(self.btnAjouterLigne)

        layoutPanier.addWidget(self.tableLignes)

        self.labelInfoPrix = QLabel("")
        self.labelInfoPrix.setWordWrap(True)
        layoutPanier.addWidget(self.labelInfoPrix)

        layout.addWidget(groupePanier)

        ####################################################
        # Retours
        ####################################################

        groupeRetours = QGroupBox("Retours")
        layoutRetours = QVBoxLayout(groupeRetours)

        self.tableRetours = QTableWidget()
        self.tableRetours.setColumnCount(8)
        self.tableRetours.setHorizontalHeaderLabels([
            "Produit concerné", "Date", "Motif", "Statut",
            "Remboursé TTC", "Coût retour HT",
            "Contrôle EAN", ""
        ])
        self.tableRetours.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableRetours.setMinimumHeight(140)

        layoutRetours.addWidget(self.tableRetours)

        boutonsRetours = QHBoxLayout()

        self.btnAjouterRetour = QPushButton("+ Signaler un retour")
        boutonsRetours.addWidget(self.btnAjouterRetour)

        self.btnControlerRetour = QPushButton(
            "🔍  Contrôler le retour (scan EAN)"
        )
        boutonsRetours.addWidget(self.btnControlerRetour)

        boutonsRetours.addStretch()

        layoutRetours.addLayout(boutonsRetours)

        layout.addWidget(groupeRetours)

        ####################################################
        # Photos d'expédition
        ####################################################

        groupePhotos = QGroupBox("📷 Photos d'expédition")
        layoutPhotos = QVBoxLayout(groupePhotos)

        explication = QLabel(
            "Photographie le produit puis le colis fermé avant "
            "de l'expédier. En cas de contestation, c'est cette "
            "preuve qui compte, pas les conditions de vente."
        )
        explication.setWordWrap(True)
        layoutPhotos.addWidget(explication)

        boutonsPhotos = QHBoxLayout()

        self.btnAjouterPhoto = QPushButton("+ Ajouter des photos")
        boutonsPhotos.addWidget(self.btnAjouterPhoto)

        self.labelNbPhotos = QLabel("")
        boutonsPhotos.addWidget(self.labelNbPhotos)

        boutonsPhotos.addStretch()

        layoutPhotos.addLayout(boutonsPhotos)

        self.zoneMiniatures = QScrollArea()
        self.zoneMiniatures.setWidgetResizable(True)
        self.zoneMiniatures.setFixedHeight(150)

        self.contenuMiniatures = QWidget()
        self.layoutMiniatures = QHBoxLayout(self.contenuMiniatures)
        self.layoutMiniatures.setSpacing(10)
        self.layoutMiniatures.addStretch()

        self.zoneMiniatures.setWidget(self.contenuMiniatures)

        layoutPhotos.addWidget(self.zoneMiniatures)

        layout.addWidget(groupePhotos)

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

        carteBoutons = QFrame()
        carteBoutons.setObjectName("barreOutils")

        boutons = QHBoxLayout(carteBoutons)
        boutons.setContentsMargins(14, 10, 14, 10)
        boutons.setSpacing(10)
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnAnnuler.setObjectName("btnSecondaire")

        self.btnEnregistrer = QPushButton("💾  Enregistrer la commande")

        # Largeur figée : le libellé ne sera jamais rogné,
        # quelle que soit la taille de la fenêtre.
        for bouton in (self.btnAnnuler, self.btnEnregistrer):
            bouton.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed,
            )

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layoutCarte.addWidget(carteBoutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self._validerAvantAccept)

        self.btnAjouterLigne.clicked.connect(self.ajouterLigne)
        self.btnNouveauClient.clicked.connect(self.creerClient)
        self.btnAjouterRetour.clicked.connect(self.ajouterRetour)
        self.btnControlerRetour.clicked.connect(self._controlerRetour)
        self.btnAjouterPhoto.clicked.connect(self._ajouterPhotos)

        ####################################################
        # Pré-remplissage si modification
        ####################################################

        if self.commande is not None:
            self._chargerCommande()

        for ligne in self.lignes_existantes:
            self._ajouterLigneTableau(ligne)

        for retour in self.retours_existants:
            self._ajouterRetourTableau(retour)

        # Nouvelle commande : une ligne vide est prête tout de
        # suite, pour que le champ de saisie du code soit
        # visible sans avoir à chercher le bouton.
        if self.tableLignes.rowCount() == 0:
            self.ajouterLigne()

        self._rafraichirPhotos()

        self._adapterTailleEcran(1250, 850)

    def _basculerDatePaiement(self, actif):

        self.datePaiement.setEnabled(actif)

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

        self.commandePayee.setChecked(bool(self.commande["paye"]))

        if self.commande["date_paiement"]:
            self.datePaiement.setDate(
                QDate.fromString(self.commande["date_paiement"], "yyyy-MM-dd")
            )
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

        # Le thème (ui/theme.py) habille déjà les champs
        # posés dans une cellule de tableau : fond blanc,
        # texte foncé, bordure et contour bleu au clic. Il ne
        # reste qu'à leur donner une hauteur confortable.

        def forcer_lisibilite(widget):

            widget.setMinimumHeight(30)

        champCode = QLineEdit()
        champCode.setPlaceholderText("EAN ou SKU, puis Entrée")
        champCode.produit_id = None
        forcer_lisibilite(champCode)

        labelProduit = QLabel("—")
        labelProduit.setStyleSheet("color:#64748b;")

        # Taille vendue. Vide et grisée tant que le produit
        # n'a pas de déclinaison — un mug n'a pas de taille.
        champTaille = QComboBox()
        champTaille.setEnabled(False)
        champTaille.addItem("—", None)

        spinQuantite = QSpinBox()
        spinQuantite.setMinimum(1)
        spinQuantite.setMaximum(9999)
        spinQuantite.setValue(1)
        forcer_lisibilite(spinQuantite)

        spinPrixHt = QDoubleSpinBox()
        spinPrixHt.setDecimals(2)
        spinPrixHt.setMaximum(99999)
        forcer_lisibilite(spinPrixHt)

        spinPrixTtc = QDoubleSpinBox()
        spinPrixTtc.setDecimals(2)
        spinPrixTtc.setMaximum(99999)
        forcer_lisibilite(spinPrixTtc)

        spinCoutAchat = QDoubleSpinBox()
        spinCoutAchat.setDecimals(2)
        spinCoutAchat.setMaximum(99999)
        forcer_lisibilite(spinCoutAchat)

        btnSupprimer = QPushButton("🗑")
        btnSupprimer.setMaximumWidth(40)
        btnSupprimer.clicked.connect(
            lambda: self._supprimerLigneTableau(btnSupprimer)
        )

        def remplir_tailles(produit_id):
            """
            Propose les tailles du produit. Une commande qui
            n'en désigne aucune ne pourrait pas décrémenter le
            bon stock, alors on la rend obligatoire dès qu'il
            y en a.
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
            """
            Une taille peut coûter et se vendre plus cher que
            les autres : on reporte son supplément et son
            prix d'achat propre.
            """

            variation_id = champTaille.currentData()

            if not variation_id:
                return

            variation = self.variationManager.obtenir(variation_id)

            if variation is None:
                return

            if variation["prix_achat_ht"]:
                spinCoutAchat.setValue(variation["prix_achat_ht"])

            supplement = variation["prix_supplement_ht"] or 0

            if supplement:
                spinPrixHt.setValue(spinPrixHt.value() + supplement)
                spinPrixTtc.setValue(
                    spinPrixTtc.value() + supplement * 1.2
                )

        champTaille.currentIndexChanged.connect(appliquer_taille)

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

            remplir_tailles(produit["id"])

            spinCoutAchat.setValue(produit["prix_fournisseur_ht"] or 0)

            self._suggererPrixVente(
                produit, spinPrixHt, spinPrixTtc, self.labelInfoPrix
            )

        champCode.returnPressed.connect(rechercher_produit)

        self.tableLignes.setCellWidget(ligne, 0, champCode)
        self.tableLignes.setCellWidget(ligne, 1, labelProduit)
        self.tableLignes.setCellWidget(ligne, 2, champTaille)
        self.tableLignes.setCellWidget(ligne, 3, spinQuantite)
        self.tableLignes.setCellWidget(ligne, 4, spinPrixHt)
        self.tableLignes.setCellWidget(ligne, 5, spinPrixTtc)
        self.tableLignes.setCellWidget(ligne, 6, spinCoutAchat)
        self.tableLignes.setCellWidget(ligne, 7, btnSupprimer)

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

            if self.tableLignes.cellWidget(ligne, 7) == bouton:
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
            champTaille = self.tableLignes.cellWidget(ligne, 2)
            spinQuantite = self.tableLignes.cellWidget(ligne, 3)
            spinPrixHt = self.tableLignes.cellWidget(ligne, 4)
            spinPrixTtc = self.tableLignes.cellWidget(ligne, 5)
            spinCoutAchat = self.tableLignes.cellWidget(ligne, 6)

            resultat.append({
                "produit_id": champCode.produit_id,
                "variation_id": champTaille.currentData(),
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
        etat = donnees.get("ean_controle")

        if etat:
            texte_controle = (
                f"✅ {etat}" if donnees.get("ean_conforme")
                else f"❌ {etat}"
            )
        else:
            texte_controle = "— non contrôlé"

        self.tableRetours.setItem(
            ligne, 6, QTableWidgetItem(texte_controle)
        )

        self.tableRetours.setCellWidget(ligne, 7, btnSupprimer)

        self._donnees_retours = getattr(self, "_donnees_retours", [])
        self._donnees_retours.append(donnees)

    def _supprimerRetourTableau(self, bouton):

        for ligne in range(self.tableRetours.rowCount()):

            if self.tableRetours.cellWidget(ligne, 7) == bouton:
                self.tableRetours.removeRow(ligne)
                return

    def retours_saisis(self):

        return getattr(self, "_donnees_retours", [])

    def _eansProduit(self, produit_id):
        """
        Codes-barres acceptables pour ce produit : le sien et
        ceux de ses déclinaisons, chaque taille ayant le sien.
        """

        codes = []

        if produit_id is None:
            return codes

        produit = self.productManager.obtenir(produit_id)

        if produit is not None and produit["ean"]:
            codes.append(str(produit["ean"]).strip())

        for variation in self.variationManager.variations(produit_id):

            if variation["ean"]:
                codes.append(str(variation["ean"]).strip())

        return codes

    def _controlerRetour(self):
        """
        Scanne le code-barres de l'article reçu et le compare
        à celui qui avait été expédié.
        """

        ligne = self.tableRetours.currentRow()

        if ligne < 0:

            QMessageBox.information(
                self,
                "Aucun retour sélectionné",
                "Clique d'abord sur la ligne du retour que tu "
                "veux contrôler."
            )
            return

        donnees = self.retours_saisis()

        if ligne >= len(donnees):
            return

        retour = donnees[ligne]

        index_produit = retour.get("produit_index")

        produit_id = None

        if index_produit is not None:

            if 0 <= index_produit < self.tableLignes.rowCount():

                champCode = self.tableLignes.cellWidget(
                    index_produit, 0
                )

                produit_id = champCode.produit_id

        attendus = self._eansProduit(produit_id)

        if not attendus:

            QMessageBox.warning(
                self,
                "Aucun code connu",
                "Ce produit n'a pas de code-barres enregistré : "
                "le contrôle est impossible."
            )
            return

        scanne, valide = QInputDialog.getText(
            self,
            "Contrôle du retour",
            "Scanne ou saisis le code-barres de l'article reçu :"
        )

        if not valide:
            return

        scanne = (scanne or "").strip()

        conforme = scanne != "" and scanne in attendus

        retour["ean_controle"] = scanne
        retour["ean_conforme"] = 1 if conforme else 0

        self.tableRetours.setItem(
            ligne,
            6,
            QTableWidgetItem(
                f"✅ {scanne}" if conforme else f"❌ {scanne}"
            )
        )

        if conforme:

            QMessageBox.information(
                self,
                "Article conforme",
                "Le code-barres correspond bien à ce qui avait "
                "été expédié."
            )

        else:

            QMessageBox.warning(
                self,
                "Article NON conforme",
                "Le code-barres scanné ne correspond à aucun "
                "de ceux expédiés pour cette ligne.\n\n"
                "Photographie l'article reçu et son emballage "
                "avant toute autre manipulation."
            )

    def _ajouterPhotos(self):
        """
        Choisit une ou plusieurs images et les range dans le
        dossier de la commande.
        """

        if self.commande is None:

            QMessageBox.information(
                self,
                "Commande non enregistrée",
                "Enregistre d'abord la commande : les photos "
                "sont rangées dans un dossier portant son "
                "numéro."
            )
            return

        fichiers, _ = QFileDialog.getOpenFileNames(
            self,
            "Choisir les photos",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)"
        )

        if not fichiers:
            return

        for fichier in fichiers:

            self.photoManager.ajouter(
                self.commande["id"],
                self.commande["numero"],
                fichier,
                "expedition"
            )

        self._rafraichirPhotos()

    def _rafraichirPhotos(self):
        """
        Reconstruit la bande de miniatures.
        """

        while self.layoutMiniatures.count():

            element = self.layoutMiniatures.takeAt(0)

            widget = element.widget()

            if widget is not None:
                widget.deleteLater()

        if self.commande is None:

            self.labelNbPhotos.setText(
                "Commande non encore enregistrée"
            )
            self.layoutMiniatures.addStretch()
            return

        photos = self.photoManager.lister(self.commande["id"])

        self.labelNbPhotos.setText(
            f"{len(photos)} photo(s)" if photos
            else "Aucune photo"
        )

        for photo in photos:

            vignette = QWidget()
            colonne = QVBoxLayout(vignette)
            colonne.setContentsMargins(0, 0, 0, 0)
            colonne.setSpacing(4)

            bouton = QPushButton()
            bouton.setFixedSize(110, 90)
            bouton.setToolTip(photo["chemin"])

            image = QPixmap(photo["chemin"])

            if not image.isNull():

                bouton.setIcon(image)
                bouton.setIconSize(
                    image.scaled(
                        104,
                        84,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ).size()
                )

            else:
                bouton.setText("Image\nintrouvable")

            chemin = photo["chemin"]

            bouton.clicked.connect(
                lambda _=False, c=chemin: self._ouvrirPhoto(c)
            )

            colonne.addWidget(bouton)

            btnRetirer = QPushButton("🗑 Retirer")
            btnRetirer.setObjectName("btnSecondaire")

            identifiant = photo["id"]

            btnRetirer.clicked.connect(
                lambda _=False, i=identifiant:
                self._supprimerPhoto(i)
            )

            colonne.addWidget(btnRetirer)

            self.layoutMiniatures.addWidget(vignette)

        self.layoutMiniatures.addStretch()

    def _ouvrirPhoto(self, chemin):

        QDesktopServices.openUrl(QUrl.fromLocalFile(chemin))

    def _supprimerPhoto(self, photo_id):

        reponse = QMessageBox.question(
            self,
            "Retirer la photo",
            "Supprimer définitivement cette photo ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        self.photoManager.supprimer(photo_id)

        self._rafraichirPhotos()

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

        # Une ligne dont le code n'a pas été reconnu ne
        # correspond à aucun produit : elle serait enregistrée
        # dans le vide et ne sortirait rien du stock.
        codes_non_reconnus = []

        for ligne in range(self.tableLignes.rowCount()):

            champCode = self.tableLignes.cellWidget(ligne, 0)

            if champCode.produit_id is None:
                codes_non_reconnus.append(
                    champCode.text().strip() or f"ligne {ligne + 1}"
                )

        # Une taille non choisie, c'est un stock qui ne
        # bougera pas : on ne saurait pas lequel décrémenter.
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
                self,
                "Taille non choisie",
                "Ces produits existent en plusieurs tailles, il "
                "faut dire laquelle est vendue :\n\n"
                + "\n".join(f"   • {n}" for n in tailles_manquantes)
                + "\n\nSans cette précision, le stock de la "
                "taille vendue ne serait pas décrémenté."
            )
            return

        if codes_non_reconnus:

            QMessageBox.warning(
                self,
                "Produit non reconnu",
                "Ces codes ne correspondent à aucun produit :\n\n"
                + "\n".join(f"   • {code}" for code in codes_non_reconnus)
                + "\n\nSaisis un EAN ou un SKU existant puis "
                "appuie sur Entrée, ou supprime la ligne avec "
                "le bouton 🗑."
            )
            return

        self.accept()