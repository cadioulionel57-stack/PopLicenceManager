from ui.product_dialog_v2 import ProductDialogV2
from ui.product_type_dialog import ProductTypeDialog
from ui.list_page import ListPage

from modules.product_manager import ProductManager

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTableWidgetItem,
    QComboBox,
    QMessageBox,
)
from PySide6.QtGui import QColor, QFont


class ProductsPage(ListPage):
    """
    Liste de tous les produits, tous types confondus — avec
    un badge coloré par type (stock/dropshipping/précommande/
    bundle) et un filtre rapide, pour s'y retrouver vite dans
    un catalogue de plusieurs milliers de références.
    """

    TYPES = {
        "stock": ("📦 Stock", "#1e7d32"),
        "dropshipping": ("🚚 Direct fournisseur", "#144b8b"),
        "precommande": ("⏳ Précommande", "#b9770e"),
        "bundle": ("🎁 Bundle", "#8e44ad"),
    }

    STATUTS_STOCK = {
        "actif": None,
        "rupture": "#e67e22",
        "fin_de_vie": "#c0392b",
    }

    def __init__(self):

        super().__init__("📦 Gestion des produits")

        self.manager = ProductManager()

        ####################################################
        # Filtre par type de produit, ajouté à la barre
        # d'outils existante (héritée de ListPage)
        ####################################################

        self.filtreType = QComboBox()
        self.filtreType.addItem("Tous les types", None)

        for cle, (libelle, _couleur) in self.TYPES.items():
            self.filtreType.addItem(libelle, cle)

        self.filtreType.currentIndexChanged.connect(self.rechercher)

        # Insère le filtre juste avant la recherche, dans la
        # même barre d'outils
        barreLayout = self.recherche.parentWidget().layout()
        barreLayout.insertWidget(0, self.filtreType)

        self.compteur = QLabel("")
        self.compteur.setStyleSheet("color:#7f8c8d; font-size:9.5pt;")
        barreLayout.insertWidget(1, self.compteur)

        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Type",
            "SKU",
            "Produit",
            "Licence",
            "Marque",
            "Fournisseur",
            "EAN"
        ])

        self.table.setColumnHidden(0, True)

        self.recherche.textChanged.connect(self.rechercher)

        self.btnAjouter.clicked.connect(self.nouveauProduit)
        self.btnModifier.clicked.connect(self.ouvrirProduit)
        self.btnSupprimer.clicked.connect(self.supprimerProduit)
        self.btnImporter.setVisible(False)
        self.btnExporter.setVisible(False)

        self.table.doubleClicked.connect(self.ouvrirProduit)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        produits = self.manager.tous()

        for ligne, produit in enumerate(produits):

            self.table.insertRow(ligne)

            libelle_type, couleur_type = self.TYPES.get(
                produit["type_produit"], ("❓ Inconnu", "#7f8c8d")
            )

            itemType = QTableWidgetItem(libelle_type)
            itemType.setForeground(QColor(couleur_type))

            policeType = QFont()
            policeType.setBold(True)
            itemType.setFont(policeType)

            self.table.setItem(ligne, 0, QTableWidgetItem(str(produit["id"])))
            self.table.setItem(ligne, 1, itemType)

            valeurs = [
                produit["sku"] or "",
                produit["nom"] or "",
                produit["licence"] or "",
                produit["marque"] or "",
                produit["fournisseur"] or "",
                produit["ean"] or "",
            ]

            for offset, valeur in enumerate(valeurs):

                item = QTableWidgetItem(valeur)

                # Nom du produit (index 1 dans valeurs, colonne
                # 3 du tableau) : mis en évidence selon le
                # statut de disponibilité.
                if offset == 1:

                    a_terminer = bool(produit["fiche_a_terminer"])

                    police = QFont()
                    police.setBold(True)

                    if a_terminer:

                        item.setText(f"⚠ À TERMINER — {valeur}")
                        item.setForeground(QColor("#ffffff"))
                        item.setBackground(QColor("#c0392b"))

                    else:

                        couleur_statut = self.STATUTS_STOCK.get(
                            produit["statut_stock"] or "actif"
                        )

                        if couleur_statut:
                            item.setForeground(QColor(couleur_statut))

                    item.setFont(police)

                self.table.setItem(ligne, 2 + offset, item)

        self.table.clearSelection()
        self._majCompteur()

    def _majCompteur(self):

        visibles = sum(
            1 for l in range(self.table.rowCount())
            if not self.table.isRowHidden(l)
        )
        total = self.table.rowCount()

        if visibles == total:
            self.compteur.setText(f"{total} produit(s)")
        else:
            self.compteur.setText(f"{visibles} / {total} produit(s)")

    def nouveauProduit(self):

        choix = ProductTypeDialog()

        if choix.exec() != choix.DialogCode.Accepted:
            return

        dialog = ProductDialogV2(choix.typeProduit())

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.charger()

    def ouvrirProduit(self):

        ligne = self.table.currentRow()

        if ligne < 0:
            return

        identifiant = int(self.table.item(ligne, 0).text())

        produit = self.manager.obtenir(identifiant)

        dialog = ProductDialogV2(produit=produit)

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.charger()

    def supprimerProduit(self):

        ligne = self.table.currentRow()

        if ligne < 0:

            QMessageBox.information(
                self, "Information", "Sélectionnez un produit."
            )
            return

        identifiant = int(self.table.item(ligne, 0).text())

        reponse = QMessageBox.question(
            self,
            "Suppression",
            "Voulez-vous vraiment supprimer ce produit ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reponse != QMessageBox.Yes:
            return

        self.manager.supprimer(identifiant)

        self.charger()

    def rechercher(self):

        texte = self.recherche.text().lower()
        type_filtre = self.filtreType.currentData()

        for ligne in range(self.table.rowCount()):

            correspond_texte = texte == ""

            for colonne in range(1, self.table.columnCount()):

                item = self.table.item(ligne, colonne)

                if item is not None and texte in item.text().lower():
                    correspond_texte = True
                    break

            correspond_type = True

            if type_filtre is not None:

                libelle_attendu = self.TYPES.get(type_filtre, ("", ""))[0]
                item_type = self.table.item(ligne, 1)
                correspond_type = (
                    item_type is not None
                    and item_type.text() == libelle_attendu
                )

            self.table.setRowHidden(
                ligne,
                not (correspond_texte and correspond_type)
            )

        self._majCompteur()