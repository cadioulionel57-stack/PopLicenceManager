"""
Onglet Variations de la fiche produit.

En haut, les critères qui s'appliquent à ce produit : tu
coches les valeurs retenues — Couleur : Noir, Blanc ;
Taille : S, M, L, XL. Un clic sur Générer crée les huit
références correspondantes.

En bas, le tableau des références. Le SKU est calculé, le
reste se saisit : l'EAN vient du fournisseur, le stock est
le tien, et le supplément de prix ne sert que si une taille
coûte plus cher que les autres.

Regénérer ne détruit rien : les références déjà là gardent
leur code-barres et leur stock, seules les combinaisons
manquantes s'ajoutent.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from modules.attribut_manager import AttributManager
from modules.variation_manager import VariationManager
from modules.stock_manager import StockManager


class VariationsTab(QWidget):

    def __init__(self):

        super().__init__()

        self.attributs = AttributManager()
        self.manager = VariationManager()
        self.stock = StockManager()

        # Renseigné par la fiche produit une fois le produit
        # enregistré. Sans identifiant, on ne peut pas encore
        # créer de références.
        self.produit_id = None

        # {attribut_id: {valeur_id: QCheckBox}}
        self.cases = {}

        exterieur = QVBoxLayout(self)
        exterieur.setContentsMargins(0, 0, 0, 0)

        defilement = QScrollArea()
        defilement.setWidgetResizable(True)
        defilement.setStyleSheet(
            "QScrollArea{border:none; background:transparent;}"
        )

        contenu = QWidget()
        principal = QVBoxLayout(contenu)
        principal.setSpacing(12)

        defilement.setWidget(contenu)
        exterieur.addWidget(defilement)

        ####################################################
        # Message quand le produit n'est pas encore créé
        ####################################################

        self.avertissement = QLabel(
            "⚠ Enregistre d'abord le produit : les références "
            "ont besoin de son SKU pour être numérotées."
        )
        self.avertissement.setWordWrap(True)
        self.avertissement.setStyleSheet(
            "color:#8a5a00; font-weight:600; padding:6px;"
        )
        principal.addWidget(self.avertissement)

        ####################################################
        # Choix des critères
        ####################################################

        self.groupeCriteres = QGroupBox("🎨 Critères de ce produit")

        layoutCriteres = QVBoxLayout(self.groupeCriteres)

        aide = QLabel(
            "Coche les valeurs qui existent pour ce produit. "
            "Croiser Couleur et Taille crée une référence par "
            "combinaison. Un seul critère coché fonctionne "
            "aussi bien."
        )
        aide.setWordWrap(True)
        aide.setStyleSheet("color:#64748b; font-size:12px;")
        layoutCriteres.addWidget(aide)

        self.zoneCases = QHBoxLayout()
        self.zoneCases.setSpacing(12)
        layoutCriteres.addLayout(self.zoneCases)

        ligneBouton = QHBoxLayout()

        self.btnGenerer = QPushButton("⚙ Générer les références")
        self.btnGenerer.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        ligneBouton.addWidget(self.btnGenerer)

        self.resume = QLabel("")
        self.resume.setStyleSheet("color:#64748b;")
        ligneBouton.addWidget(self.resume)

        ligneBouton.addStretch()
        layoutCriteres.addLayout(ligneBouton)

        principal.addWidget(self.groupeCriteres)

        ####################################################
        # Tableau des références
        ####################################################

        self.groupeReferences = QGroupBox("📦 Références vendables")

        layoutReferences = QVBoxLayout(self.groupeReferences)

        barre = QHBoxLayout()

        self.btnSupprimer = QPushButton("🗑 Supprimer la référence")
        self.btnSupprimer.setObjectName("btnSupprimer")
        self.btnSupprimer.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        barre.addWidget(self.btnSupprimer)

        barre.addStretch()

        self.totalStock = QLabel("")
        police = QFont()
        police.setBold(True)
        self.totalStock.setFont(police)
        self.totalStock.setStyleSheet("color:#0f2f5c;")
        barre.addWidget(self.totalStock)

        layoutReferences.addLayout(barre)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Référence", "SKU", "EAN", "Stock",
            "Supplément HT", "Poids (g)", "Active",
        ])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        entete = self.table.horizontalHeader()
        entete.setSectionResizeMode(1, QHeaderView.Fixed)
        entete.setSectionResizeMode(2, QHeaderView.Stretch)
        entete.setSectionResizeMode(3, QHeaderView.Fixed)
        entete.setSectionResizeMode(4, QHeaderView.Fixed)
        entete.setSectionResizeMode(5, QHeaderView.Fixed)
        entete.setSectionResizeMode(6, QHeaderView.Fixed)
        entete.setSectionResizeMode(7, QHeaderView.Fixed)

        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 90)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 80)

        self.table.setMinimumHeight(260)

        layoutReferences.addWidget(self.table)

        rappel = QLabel(
            "L'EAN est le seul champ que tu dois saisir : il "
            "vient de ton fournisseur. Le SKU, lui, est "
            "calculé à partir de celui du produit."
        )
        rappel.setWordWrap(True)
        rappel.setStyleSheet("color:#64748b; font-size:12px;")
        layoutReferences.addWidget(rappel)

        principal.addWidget(self.groupeReferences)

        principal.addStretch()

        self.btnGenerer.clicked.connect(self.generer)
        self.btnSupprimer.clicked.connect(self.supprimer)

        self._basculerDisponibilite()

    ########################################################
    # Critères
    ########################################################

    def construireCases(self):
        """
        Une petite colonne de cases à cocher par critère
        actif, reconstruite à chaque ouverture pour tenir
        compte des critères créés entre-temps.
        """

        while self.zoneCases.count():

            element = self.zoneCases.takeAt(0)
            widget = element.widget()

            if widget is not None:
                # setParent(None) retire le widget de
                # l'affichage TOUT DE SUITE. Avec le seul
                # deleteLater(), la suppression n'a lieu qu'au
                # tour de boucle suivant : les anciennes cases
                # restaient visibles et les nouvelles se
                # dessinaient par-dessus.
                widget.setParent(None)
                widget.deleteLater()

        self.cases = {}

        criteres = self.attributs.attributs(actifs_seulement=True)

        if not criteres:

            vide = QLabel(
                "Aucun critère défini. Va dans Paramètres, "
                "onglet Variations, pour créer tes couleurs "
                "et tes tailles."
            )
            vide.setWordWrap(True)
            vide.setStyleSheet("color:#c0392b;")
            self.zoneCases.addWidget(vide)
            return

        for critere in criteres:

            boite = QGroupBox(critere["nom"])
            layout = QVBoxLayout(boite)
            layout.setSpacing(4)

            self.cases[critere["id"]] = {}

            valeurs = self.attributs.valeurs(
                critere["id"], actives_seulement=True
            )

            if not valeurs:
                layout.addWidget(QLabel("— aucune valeur —"))

            for valeur in valeurs:

                case = QCheckBox(valeur["valeur"])
                layout.addWidget(case)

                self.cases[critere["id"]][valeur["id"]] = case

            layout.addStretch()

            self.zoneCases.addWidget(boite)

        self.zoneCases.addStretch()

    def selection(self):
        """
        Ce qui est coché : {attribut_id: [valeur_id, ...]}
        """

        resultat = {}

        for attribut_id, valeurs in self.cases.items():

            cochees = [
                valeur_id
                for valeur_id, case in valeurs.items()
                if case.isChecked()
            ]

            if cochees:
                resultat[attribut_id] = cochees

        return resultat

    ########################################################
    # Chargement
    ########################################################

    def charger(self, produit_id):
        """
        Appelée par la fiche produit à l'ouverture.
        """

        self.produit_id = produit_id

        self.construireCases()

        if produit_id:

            deja = self.manager.selection_actuelle(produit_id)

            for attribut_id, valeurs in deja.items():
                for valeur_id in valeurs:
                    case = self.cases.get(attribut_id, {}).get(valeur_id)
                    if case is not None:
                        case.setChecked(True)

        self._basculerDisponibilite()
        self.chargerTable()

    def _basculerDisponibilite(self):

        pret = self.produit_id is not None

        self.avertissement.setVisible(not pret)
        self.groupeCriteres.setEnabled(pret)
        self.groupeReferences.setEnabled(pret)

    def chargerTable(self):

        self.table.setRowCount(0)

        if not self.produit_id:
            self.totalStock.setText("")
            return

        # Rattrapage : une taille peut porter une quantité
        # saisie sans qu'aucun mouvement de stock n'ait été
        # écrit — c'est le cas de toutes celles remplies avant
        # que la colonne Stock ne soit reliée au stock réel.
        # initialiser_variation() ne fait rien si l'entrée de
        # départ existe déjà, on peut donc l'appeler à chaque
        # ouverture sans risque de doublon.
        for variation in self.manager.variations(self.produit_id):
            self.stock.initialiser_variation(variation["id"])

        for variation in self.manager.variations(self.produit_id):

            ligne = self.table.rowCount()
            self.table.insertRow(ligne)

            self.table.setItem(
                ligne, 0, QTableWidgetItem(str(variation["id"]))
            )

            itemLibelle = QTableWidgetItem(variation["libelle"] or "")
            police = QFont()
            police.setBold(True)
            itemLibelle.setFont(police)
            self.table.setItem(ligne, 1, itemLibelle)

            itemSku = QTableWidgetItem(variation["sku"] or "")
            itemSku.setForeground(QColor("#64748b"))
            self.table.setItem(ligne, 2, itemSku)

            champEan = QLineEdit(variation["ean"] or "")
            champEan.setPlaceholderText("code-barres")
            champEan.setMinimumHeight(30)
            champEan.editingFinished.connect(
                lambda v=variation["id"], c=champEan:
                self._enregistrerEan(v, c)
            )
            self.table.setCellWidget(ligne, 3, champEan)

            champStock = QSpinBox()
            champStock.setMaximum(999999)
            champStock.setValue(variation["quantite_stock"] or 0)
            champStock.setMinimumHeight(30)
            # editingFinished plutôt que valueChanged : sinon
            # taper « 12 » écrirait un mouvement pour 1 puis
            # un autre pour 12.
            champStock.editingFinished.connect(
                lambda v=variation["id"], c=champStock:
                self._enregistrerStock(v, c.value())
            )
            self.table.setCellWidget(ligne, 4, champStock)

            champSupplement = QDoubleSpinBox()
            champSupplement.setDecimals(2)
            champSupplement.setMaximum(9999)
            champSupplement.setSuffix(" €")
            champSupplement.setValue(
                variation["prix_supplement_ht"] or 0
            )
            champSupplement.setMinimumHeight(30)
            champSupplement.valueChanged.connect(
                lambda valeur, v=variation["id"]:
                self._enregistrer(v, prix_supplement_ht=valeur)
            )
            self.table.setCellWidget(ligne, 5, champSupplement)

            champPoids = QDoubleSpinBox()
            champPoids.setDecimals(0)
            champPoids.setMaximum(99999)
            champPoids.setSpecialValueText("—")
            champPoids.setValue(variation["poids"] or 0)
            champPoids.setMinimumHeight(30)
            champPoids.valueChanged.connect(
                lambda valeur, v=variation["id"]:
                self._enregistrer(v, poids=valeur or None)
            )
            self.table.setCellWidget(ligne, 6, champPoids)

            caseActive = QCheckBox()
            caseActive.setChecked(bool(variation["actif"]))
            caseActive.toggled.connect(
                lambda coche, v=variation["id"]:
                self._enregistrer(v, actif=1 if coche else 0)
            )

            conteneur = QWidget()
            layoutCase = QHBoxLayout(conteneur)
            layoutCase.addWidget(caseActive)
            layoutCase.setAlignment(
                caseActive, Qt.AlignmentFlag.AlignCenter
            )
            layoutCase.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(ligne, 7, conteneur)

        self._majTotal()

    def _majTotal(self):

        if not self.produit_id:
            return

        total = self.manager.stock_total(self.produit_id)
        nombre = self.table.rowCount()

        self.totalStock.setText(
            f"{nombre} référence(s) — stock total : {total}"
        )

    ########################################################
    # Écritures
    ########################################################

    def _enregistrer(self, variation_id, **champs):

        self.manager.modifier(variation_id, **champs)
        self._majTotal()

    def _enregistrerStock(self, variation_id, quantite):
        """
        La quantité saisie ici est à la fois ce qu'on met en
        vente et ce qu'on a réellement en rayon.

        On aligne donc le stock réel dessus, en écrivant le
        mouvement correspondant : sans ça, la taille
        apparaîtrait à zéro dans l'écran Stock alors qu'on
        vient d'en saisir cinq.

        La première saisie devient le stock de départ ; les
        suivantes sont tracées comme un ajustement, pour
        qu'on sache toujours d'où vient un écart.
        """

        self.manager.modifier(variation_id, quantite_stock=quantite)

        variation = self.manager.obtenir(variation_id)

        if variation is None:
            return

        # Sans prix propre à la taille, on reprend celui du
        # produit parent : sinon la référence entrerait en
        # stock avec une valeur nulle.
        prix = variation["prix_achat_ht"]

        if not prix:

            parent = self.stock.db.lire_un(
                """
                SELECT prix_achat_gestion, prix_fournisseur_ht
                FROM produits WHERE id = ?
                """,
                (variation["produit_id"],)
            )

            if parent is not None:
                prix = (
                    parent["prix_achat_gestion"]
                    or parent["prix_fournisseur_ht"]
                    or None
                )

        reel = self.stock.quantite(
            variation["produit_id"], variation_id
        )

        ecart = quantite - reel

        if ecart == 0:
            self._majTotal()
            return

        premiere_fois = reel == 0 and not self.stock.mouvements(
            variation_id=variation_id
        )

        self.stock.enregistrer_mouvement(
            produit_id=variation["produit_id"],
            type_mouvement=(
                StockManager.ENTREE if ecart > 0
                else StockManager.SORTIE
            ),
            quantite=abs(ecart),
            origine="creation" if premiere_fois else "inventaire",
            reference=variation["produit_id"],
            prix_unitaire_ht=(prix if ecart > 0 else None),
            commentaire=(
                f"Stock de départ — {variation['libelle'] or ''}"
                if premiere_fois else
                f"Ajustement depuis la fiche produit "
                f"({ecart:+d}) — {variation['libelle'] or ''}"
            ),
            variation_id=variation_id,
        )

        self._majTotal()

    def _enregistrerEan(self, variation_id, champ):
        """
        L'EAN doit rester unique : deux tailles ne peuvent
        pas partager un code-barres.
        """

        valeur = champ.text().strip() or None

        try:
            self.manager.modifier(variation_id, ean=valeur)
        except Exception:
            QMessageBox.warning(
                self,
                "Code-barres déjà utilisé",
                f"Le code « {valeur} » est déjà attribué à une "
                f"autre référence. Chaque taille doit avoir le "
                f"sien."
            )
            actuel = self.manager.obtenir(variation_id)
            champ.setText(actuel["ean"] or "" if actuel else "")

    ########################################################
    # Actions
    ########################################################

    def generer(self):

        if not self.produit_id:
            return

        selection = self.selection()

        if not selection:
            QMessageBox.information(
                self,
                "Aucun critère coché",
                "Coche au moins une valeur — par exemple les "
                "tailles S, M, L et XL."
            )
            return

        # Croiser trois critères fait exploser le nombre de
        # références : 6 couleurs x 5 tailles x 3 tours de
        # tête, cela fait 90 codes-barres à saisir. On prévient
        # avant, plutôt que de laisser découvrir le tableau.
        total = 1

        for valeurs in selection.values():
            total *= len(valeurs)

        if total > 30:

            detail = " x ".join(
                str(len(v)) for v in selection.values()
            )

            reponse = QMessageBox.question(
                self,
                "Beaucoup de références",
                f"Cette combinaison ({detail}) va créer "
                f"jusqu'à {total} références, chacune avec son "
                f"code-barres à saisir.\n\n"
                f"Vérifie que tous les critères cochés "
                f"s'appliquent vraiment à ce produit — un "
                f"t-shirt n'a pas de tour de tête.\n\n"
                f"Continuer ?"
            )

            if reponse != QMessageBox.StandardButton.Yes:
                return

        creees, deja = self.manager.generer(self.produit_id, selection)

        self.chargerTable()

        if creees:
            self.resume.setText(
                f"{creees} référence(s) créée(s)"
                + (f", {deja} déjà présente(s)" if deja else "")
            )
        else:
            self.resume.setText(
                "Rien de nouveau : toutes les combinaisons "
                "existent déjà."
            )

    def supprimer(self):

        ligne = self.table.currentRow()

        if ligne < 0 or self.table.item(ligne, 0) is None:
            QMessageBox.information(
                self,
                "Aucune référence",
                "Sélectionne d'abord une ligne du tableau."
            )
            return

        variation_id = int(self.table.item(ligne, 0).text())
        libelle = self.table.item(ligne, 1).text()

        reponse = QMessageBox.question(
            self,
            "Supprimer la référence",
            f"Supprimer « {libelle} » ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        try:
            self.manager.supprimer(variation_id)
        except ValueError as erreur:
            QMessageBox.warning(
                self, "Suppression impossible", str(erreur)
            )
            return

        self.chargerTable()