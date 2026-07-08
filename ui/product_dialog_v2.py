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
from ui.tabs.tab_caracteristiques import CaracteristiquesTab
from ui.tabs.tab_publication import PublicationTab
from ui.tabs.tab_tarification import TarificationTab

from modules.numerotation_manager import NumerotationManager
from modules.product_manager import ProductManager


class ProductDialogV2(QDialog):

    def __init__(self, type_produit=None, produit=None):

        super().__init__()

        self.produit = produit

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
        self.resize(1100, 750)

        self.setStyleSheet("""
        QDialog{
            background:#edf3fa;
            font-family:"Segoe UI";
        }

        QTabWidget::pane{
            background:white;
            border:1px solid #d7e3ef;
            border-radius:10px;
        }

        QTabBar::tab{
            background:#dfeaf6;
            padding:12px 24px;
            margin-right:2px;
            border-top-left-radius:8px;
            border-top-right-radius:8px;
        }

        QTabBar::tab:selected{
            background:white;
            font-weight:bold;
            color:#144b8b;
        }

        QPushButton{
            background:#144b8b;
            color:white;
            border:none;
            border-radius:8px;
            padding:10px 20px;
            min-width:140px;
        }

        QPushButton:hover{
            background:#1d61b4;
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
        # Autres onglets
        ####################################################

        self.tabs.addTab(QWidget(), "🌐 SEO")
        self.tabs.addTab(QWidget(), "🖼 Images")
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

    def enregistrer(self):

        if self.produit is None:

            sku = self.numerotation.generer(
                self.codeNumerotation
            )

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

                matiere=self.pageCaracteristiques.matiere.text(),

                couleur=self.pageCaracteristiques.couleur.text(),

                age_minimum=self.pageCaracteristiques.age.value(),

                pays_fabrication=self.pageCaracteristiques.fabrication.text()

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

                matiere=self.pageCaracteristiques.matiere.text(),

                couleur=self.pageCaracteristiques.couleur.text(),

                age_minimum=self.pageCaracteristiques.age.value(),

                pays_fabrication=self.pageCaracteristiques.fabrication.text()

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

            if champ.value() > 0:

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