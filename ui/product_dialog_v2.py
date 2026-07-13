from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QPushButton,
    QMessageBox,
)

from ui.tabs.tab_general import GeneralTab
from ui.tabs.tab_caracteristiquesv2 import CaracteristiquesTab
from ui.tabs.tab_publication import PublicationTab
from ui.tabs.tab_tarification import TarificationTab
from ui.tabs.tab_seo import SeoTab
from ui.tabs.tab_images import ImagesTab

from modules.numerotation_manager import NumerotationManager
from modules.product_manager import ProductManager


class ProductDialogV2(QDialog):

    def __init__(
        self,
        type_produit=None,
        produit=None,
        nom_prerempli=None,
        prix_achat_prerempli=None,
        code_prerempli=None,
        parent=None,
    ):

        super().__init__(parent)

        self.produit = produit
        self._creation_rapide = nom_prerempli is not None

        if produit is not None:
            self.type_produit = produit["type_produit"]
        else:
            self.type_produit = type_produit

        self.productManager = ProductManager()
        self.numerotation = NumerotationManager()

        if self.produit is None:
            self.setWindowTitle("📦 Nouveau produit")
        else:
            self.setWindowTitle("✏ Modifier le produit")

        # (taille fixée plus bas, une fois tout le contenu
        # de la fenêtre posé — sinon Qt l'agrandit tout seul
        # ensuite pour faire de la place à son contenu)

        self.setStyleSheet("""
        QDialog{
            background:#f4f7fb;
            font-family:"Segoe UI";
        }

        QTabWidget::pane{
            background:white;
            border:1px solid #e1e8f0;
            border-radius:10px;
            top:-1px;
        }

        QTabBar::tab{
            background:#e7edf6;
            color:#3d5773;
            padding:11px 22px;
            margin-right:3px;
            border-top-left-radius:8px;
            border-top-right-radius:8px;
            font-size:10pt;
        }

        QTabBar::tab:hover{
            background:#d9e4f2;
        }

        QTabBar::tab:selected{
            background:white;
            font-weight:600;
            color:#0f2f5c;
            border-bottom:3px solid #144b8b;
        }

        QGroupBox{
            background:white;
            border:1px solid #e1e8f0;
            border-radius:10px;
            margin-top:14px;
            padding-top:14px;
            font-weight:600;
            font-size:10.5pt;
            color:#0f2f5c;
        }

        QGroupBox::title{
            subcontrol-origin:margin;
            left:12px;
            padding:0 8px;
        }

        QLineEdit,
        QTextEdit,
        QComboBox,
        QSpinBox,
        QDoubleSpinBox,
        QDateEdit{
            background:#f7f9fc;
            border:1px solid #d7e0ec;
            border-radius:7px;
            padding:6px 8px;
            font-size:10pt;
            color:#1c2b3a;
            selection-background-color:#dbe7f7;
        }

        QLineEdit:focus,
        QTextEdit:focus,
        QComboBox:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus,
        QDateEdit:focus{
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
            font-size:10pt;
            color:#1c2b3a;
            spacing:8px;
        }

        QLabel{
            color:#1c2b3a;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px 20px;
            min-width:140px;
            font-weight:500;
        }

        QPushButton:hover{
            background:#1d61b4;
        }

        QPushButton:pressed{
            background:#0d3a6e;
        }
        """)

        ####################################################
        # Layout principal
        ####################################################

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        ####################################################
        # Onglet Général
        ####################################################

        self.pageGeneral = GeneralTab()

        self.tabs.addTab(
            self.pageGeneral,
            "📦 Général"
        )

        ####################################################
        # Type de produit
        ####################################################

        libelles = {
            "stock": "📦 Produit en stock",
            "dropshipping": "🚚 Direct fournisseur",
            "precommande": "⏳ Précommande",
            "bundle": "🎁 Bundle",
        }

        self.pageGeneral.typeProduit.setText(
            libelles[self.type_produit]
        )

        ####################################################
        # Aperçu du SKU
        ####################################################

        codes = {
            "stock": "SKU_STOCK",
            "dropshipping": "SKU_DROP",
            "precommande": "SKU_PRECO",
            "bundle": "SKU_BUNDLE",
        }

        self.codeNumerotation = codes[self.type_produit]

        if self.produit is None:

            self.pageGeneral.sku.setText(
                self.numerotation.apercu(
                    self.codeNumerotation
                )
            )

            if self._creation_rapide:

                self.pageGeneral.nom.setText(nom_prerempli or "")
                self.pageGeneral.prixAchatHt.setValue(
                    prix_achat_prerempli or 0
                )
                self.pageGeneral.ean.setText(code_prerempli or "")
                self.pageGeneral.ficheATerminer.setChecked(True)

        else:

            self.pageGeneral.sku.setText(
                self.produit["sku"]
            )

            self.pageGeneral.nom.setText(
                self.produit["nom"] or ""
            )

            self.pageGeneral.ean.setText(
                self.produit["ean"] or ""
            )

            self.pageGeneral.referenceFournisseur.setText(
                self.produit["reference_fournisseur"] or ""
            )

            self.pageGeneral.cboLicence.selectionner(
                self.produit["licence_id"]
            )

            self.pageGeneral.cboMarque.selectionner(
                self.produit["marque_id"]
            )

            self.pageGeneral.cboFournisseur.selectionner(
                self.produit["fournisseur_id"]
            )

            self.pageGeneral.prixAchatHt.setValue(
                self.produit["prix_fournisseur_ht"] or 0
            )

            self.pageGeneral.selectionner_statut_stock(
                self.produit["statut_stock"]
            )

            self.pageGeneral.quantiteStock.setValue(
                self.produit["quantite_stock"] or 0
            )

            self.pageGeneral.ficheATerminer.setChecked(
                bool(self.produit["fiche_a_terminer"])
            )

        ####################################################
        # Onglet Caractéristiques
        ####################################################

        self.pageCaracteristiques = CaracteristiquesTab(self.type_produit)

        self.tabs.addTab(
            self.pageCaracteristiques,
            "📏 Caractéristiques"
        )

        if self.produit is not None:

            categories_canaux = self.productManager.categories_canaux(
                self.produit["id"]
            )

            self.pageCaracteristiques.charger(
                self.produit,
                categories_canaux
            )

        ####################################################
        # Onglet Publication
        ####################################################

        self.pagePublication = PublicationTab(self.type_produit)

        self.tabs.addTab(
            self.pagePublication,
            "🚀 Publication"
        )

        if self.produit is not None:

            canaux_produit = self.productManager.canaux_produit(
                self.produit["id"]
            )

            self.pagePublication.charger(canaux_produit)

            self.pagePublication.definir_categorie_site(
                self.produit["categorie_site_id"]
            )

            self.pagePublication.definir_modele_fiche(
                self.produit["modele_fiche_id"]
            )

        ####################################################
        # Onglet Tarification
        ####################################################

        self.pageTarification = TarificationTab(self.type_produit)

        # Relie l'onglet Tarification aux vrais champs des
        # autres onglets (prix d'achat, famille, poids,
        # catégorie par canal), sans dépendance figée.
        self.pageTarification._prix_achat_ht = (
            lambda: self.pageGeneral.prixAchatHt.value()
        )
        self.pageTarification._famille_produit_id = (
            lambda: self.pageCaracteristiques.familleProduit.id()
        )
        self.pageTarification._poids = (
            lambda: self.pageCaracteristiques.poids.value()
        )
        self.pageTarification._longueur = (
            lambda: self.pageCaracteristiques.longueur.value()
        )
        self.pageTarification._largeur = (
            lambda: self.pageCaracteristiques.largeur.value()
        )
        self.pageTarification._hauteur = (
            lambda: self.pageCaracteristiques.hauteur.value()
        )
        self.pageTarification._longueur_expedition = (
            lambda: self.pageCaracteristiques.longueurExpedition.value()
        )
        self.pageTarification._largeur_expedition = (
            lambda: self.pageCaracteristiques.largeurExpedition.value()
        )
        self.pageTarification._hauteur_expedition = (
            lambda: self.pageCaracteristiques.hauteurExpedition.value()
        )
        self.pageTarification._emballage_id = (
            lambda: self.pageCaracteristiques.emballage_id()
        )
        self.pageTarification._categorie_pour_canal = (
            lambda canal_id: self.pageCaracteristiques
            .categoriesCanaux.get(canal_id).id()
            if self.pageCaracteristiques.categoriesCanaux.get(canal_id)
            else None
        )

        self.tabs.addTab(
            self.pageTarification,
            "💰 Tarification"
        )

        if self.produit is not None:

            marche = self.productManager.prix_marche_par_canal(
                self.produit["id"]
            )

            marges = self.productManager.marges_par_canal(
                self.produit["id"]
            )

            self.pageTarification.charger(
                self.produit,
                marche=marche,
                marges=marges
            )

        else:

            self.pageTarification.calculer()

        ####################################################
        # Onglet SEO
        ####################################################

        self.pageSeo = SeoTab()

        self.pageSeo._nom = (
            lambda: self.pageGeneral.nom.text()
        )
        self.pageSeo._licence_nom = (
            lambda: self.pageGeneral.cboLicence.texte() or None
        )
        self.pageSeo._marque_nom = (
            lambda: self.pageGeneral.cboMarque.texte() or None
        )
        self.pageSeo._matiere = (
            lambda: self.pageCaracteristiques.matiere.text() or None
        )
        self.pageSeo._couleur = (
            lambda: self.pageCaracteristiques.couleur.text() or None
        )
        self.pageSeo._age_minimum = (
            lambda: self.pageCaracteristiques.age.value() or None
        )
        self.pageSeo._pays_fabrication = (
            lambda: self.pageCaracteristiques.fabrication.text() or None
        )
        self.pageSeo._ean = (
            lambda: self.pageGeneral.ean.text() or None
        )
        self.pageSeo._sku = (
            lambda: self.pageGeneral.sku.text() or None
        )
        self.pageSeo._prix_ttc_site = self._prix_ttc_site_actuel

        self.tabs.addTab(self.pageSeo, "🌐 SEO")

        if self.produit is not None:
            self.pageSeo.charger(self.produit)

        ####################################################
        # Autres onglets
        ####################################################

        ####################################################
        # Images
        ####################################################

        self.pageImages = ImagesTab()
        self.tabs.addTab(self.pageImages, "🖼 Images")

        if self.produit is not None:
            self.pageImages.charger(
                self.produit["image_principale"],
                self.produit["image_2"],
                self.produit["image_3"],
                self.produit["image_ambiance"],
            )

        self.tabs.addTab(QWidget(), "📜 Historique")

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
        self.btnEnregistrer.clicked.connect(self.enregistrer)

        self._adapterTailleEcran(1400, 800)

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

    def _prix_ttc_site_actuel(self):
        """
        Renvoie le prix de vente TTC calculé sur le canal
        "Site" (WiziShop), s'il a déjà été calculé dans
        l'onglet Tarification — utilisé pour les données
        structurées Schema.org (prix affiché dans Google).
        Renvoie None si pas encore calculé, ce qui est géré
        proprement par le générateur SEO.
        """

        canaux = getattr(self.pageTarification, "_derniersCanaux", None)

        if not canaux:
            return None

        for canal in canaux:

            if "site" not in (canal["nom"] or "").lower():
                continue

            resultat = self.pageTarification.derniersResultats.get(
                canal["id"]
            )

            if resultat and not resultat.get("erreur"):
                return resultat.get("prix_vente_ttc")

        return None

    def enregistrer(self):

        # Un produit Direct Fournisseur est expédié par le
        # fournisseur, jamais par toi — aucun emballage de ta
        # grille ne s'applique, donc ce contrôle ne le
        # concerne pas.
        if (
            self.type_produit != "dropshipping"
            and not self.pageCaracteristiques.emballage_valide()
        ):

            QMessageBox.warning(
                self,
                "Aucun emballage compatible",
                "Aucun emballage de la grille ne convient aux "
                "dimensions et au poids saisis pour ce produit.\n\n"
                "Ajoutez un emballage adapté dans la grille "
                "d'emballages avant d'enregistrer ce produit."
            )

            return

        if self.produit is None:

            sku = self.numerotation.generer(
                self.codeNumerotation
            )

            # Génération automatique du contenu SEO à la
            # toute première sauvegarde du produit, si
            # l'onglet n'a pas déjà été rempli/régénéré
            # manuellement entre-temps.
            if self.pageSeo.est_vide():
                self.pageSeo.regenerer()

            identifiant_produit = self.productManager.ajouter(

                type_produit=self.type_produit,

                ean=self.pageGeneral.ean.text(),

                sku=sku,

                nom=self.pageGeneral.nom.text(),

                licence_id=self.pageGeneral.cboLicence.id(),

                marque_id=self.pageGeneral.cboMarque.id(),

                fournisseur_id=self.pageGeneral.cboFournisseur.id(),

                reference_fournisseur=self.pageGeneral.referenceFournisseur.text(),

                prix_fournisseur_ht=self.pageGeneral.prixAchatHt.value(),

                famille_produit_id=self.pageCaracteristiques.familleProduit.id(),

                marge_visee_pourcentage=self.pageTarification.margeVisee.value(),

                longueur=self.pageCaracteristiques.longueur.value(),

                largeur=self.pageCaracteristiques.largeur.value(),

                hauteur=self.pageCaracteristiques.hauteur.value(),

                poids=self.pageCaracteristiques.poids.value(),

                longueur_expedition=self.pageCaracteristiques.longueurExpedition.value(),

                largeur_expedition=self.pageCaracteristiques.largeurExpedition.value(),

                hauteur_expedition=self.pageCaracteristiques.hauteurExpedition.value(),

                emballage_id=self.pageCaracteristiques.emballage_id(),

                matiere=self.pageCaracteristiques.matiere.text(),

                couleur=self.pageCaracteristiques.couleur.text(),

                age_minimum=self.pageCaracteristiques.age.value(),

                pays_fabrication=self.pageCaracteristiques.fabrication.text(),

                composition_matiere=self.pageCaracteristiques.compositionMatiere.text() or None,

                instructions_entretien=self.pageCaracteristiques.instructionsEntretien.text() or None,

                coupe_type=self.pageCaracteristiques.coupeType.text() or None,

                type_manche=self.pageCaracteristiques.typeManche.text() or None,

                age_conseille=self.pageCaracteristiques.ageConseille.text() or None,

                nombre_joueurs=self.pageCaracteristiques.nombreJoueurs.text() or None,

                duree_partie=self.pageCaracteristiques.dureePartie.text() or None,

                contenu_boite=self.pageCaracteristiques.contenuBoite.text() or None,

                nombre_pieces=self.pageCaracteristiques.nombrePieces.text() or None,

                taille_literie=self.pageCaracteristiques.tailleLiterie.text() or None,

                contenance=self.pageCaracteristiques.contenance.text() or None,

                compatible_lave_vaisselle=self.pageCaracteristiques.compatibleLaveVaisselle.isChecked(),

                titre_seo=self.pageSeo.titreSeo.text(),

                meta_description=self.pageSeo.metaDescription.toPlainText(),

                mots_cles=self.pageSeo.motsCles.text(),

                url_slug=self.pageSeo.urlSlug.text(),

                description_courte=self.pageSeo.descriptionCourte.toPlainText(),

                description_longue=self.pageSeo.descriptionLongue.toPlainText(),

                eligible_papier_cadeau=self.pageCaracteristiques.eligiblePapierCadeau.isChecked(),

                statut_stock=self.pageGeneral.statut_stock(),

                quantite_stock=self.pageGeneral.quantiteStock.value(),

                fiche_a_terminer=self.pageGeneral.ficheATerminer.isChecked(),

                image_principale=self.pageImages.image_principale(),

                image_2=self.pageImages.image_2(),

                image_3=self.pageImages.image_3(),

                image_ambiance=self.pageImages.image_ambiance(),

                categorie_site_id=self.pagePublication.categorie_site_id(),

                modele_fiche_id=self.pagePublication.modele_fiche_id(),

            )

        else:

            identifiant_produit = self.produit["id"]

            self.productManager.modifier(

                identifiant=identifiant_produit,

                type_produit=self.type_produit,

                ean=self.pageGeneral.ean.text(),

                nom=self.pageGeneral.nom.text(),

                licence_id=self.pageGeneral.cboLicence.id(),

                marque_id=self.pageGeneral.cboMarque.id(),

                fournisseur_id=self.pageGeneral.cboFournisseur.id(),

                reference_fournisseur=self.pageGeneral.referenceFournisseur.text(),

                prix_fournisseur_ht=self.pageGeneral.prixAchatHt.value(),

                famille_produit_id=self.pageCaracteristiques.familleProduit.id(),

                marge_visee_pourcentage=self.pageTarification.margeVisee.value(),

                longueur=self.pageCaracteristiques.longueur.value(),

                largeur=self.pageCaracteristiques.largeur.value(),

                hauteur=self.pageCaracteristiques.hauteur.value(),

                poids=self.pageCaracteristiques.poids.value(),

                longueur_expedition=self.pageCaracteristiques.longueurExpedition.value(),

                largeur_expedition=self.pageCaracteristiques.largeurExpedition.value(),

                hauteur_expedition=self.pageCaracteristiques.hauteurExpedition.value(),

                emballage_id=self.pageCaracteristiques.emballage_id(),

                matiere=self.pageCaracteristiques.matiere.text(),

                couleur=self.pageCaracteristiques.couleur.text(),

                age_minimum=self.pageCaracteristiques.age.value(),

                pays_fabrication=self.pageCaracteristiques.fabrication.text(),

                composition_matiere=self.pageCaracteristiques.compositionMatiere.text() or None,

                instructions_entretien=self.pageCaracteristiques.instructionsEntretien.text() or None,

                coupe_type=self.pageCaracteristiques.coupeType.text() or None,

                type_manche=self.pageCaracteristiques.typeManche.text() or None,

                age_conseille=self.pageCaracteristiques.ageConseille.text() or None,

                nombre_joueurs=self.pageCaracteristiques.nombreJoueurs.text() or None,

                duree_partie=self.pageCaracteristiques.dureePartie.text() or None,

                contenu_boite=self.pageCaracteristiques.contenuBoite.text() or None,

                nombre_pieces=self.pageCaracteristiques.nombrePieces.text() or None,

                taille_literie=self.pageCaracteristiques.tailleLiterie.text() or None,

                contenance=self.pageCaracteristiques.contenance.text() or None,

                compatible_lave_vaisselle=self.pageCaracteristiques.compatibleLaveVaisselle.isChecked(),

                titre_seo=self.pageSeo.titreSeo.text(),

                meta_description=self.pageSeo.metaDescription.toPlainText(),

                mots_cles=self.pageSeo.motsCles.text(),

                url_slug=self.pageSeo.urlSlug.text(),

                description_courte=self.pageSeo.descriptionCourte.toPlainText(),

                description_longue=self.pageSeo.descriptionLongue.toPlainText(),

                eligible_papier_cadeau=self.pageCaracteristiques.eligiblePapierCadeau.isChecked(),

                statut_stock=self.pageGeneral.statut_stock(),

                quantite_stock=self.pageGeneral.quantiteStock.value(),

                fiche_a_terminer=self.pageGeneral.ficheATerminer.isChecked(),

                image_principale=self.pageImages.image_principale(),

                image_2=self.pageImages.image_2(),

                image_3=self.pageImages.image_3(),

                image_ambiance=self.pageImages.image_ambiance(),

                categorie_site_id=self.pagePublication.categorie_site_id(),

                modele_fiche_id=self.pagePublication.modele_fiche_id(),

            )

        self.productManager.definir_categories_canaux(
            identifiant_produit,
            self.pageCaracteristiques.categories_canaux_selectionnees()
        )

        self.productManager.definir_canaux_produit(
            identifiant_produit,
            self.pagePublication.canaux_selectionnes()
        )

        for canal_id, champ in self.pageTarification.champsPrixMarche.items():

            # Toujours enregistrer, même à 0€ — sinon remettre
            # un prix marché à zéro ne l'effaçait jamais en
            # base, l'ancienne valeur restait affichée au
            # prochain chargement.
            self.productManager.definir_prix_marche(
                identifiant_produit,
                canal_id,
                champ.value()
            )

        for canal_id, marge in self.pageTarification.marges_saisies().items():

            self.productManager.definir_marge_canal(
                identifiant_produit,
                canal_id,
                marge
            )

        QMessageBox.information(
            self,
            "Produit",
            "Produit enregistré avec succès."
        )

        self.accept()