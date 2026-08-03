from datetime import date

from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QLabel,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTableWidget,
    QHeaderView,
    QPushButton,
    QInputDialog,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
    QLineEdit,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QTextDocument, QPageLayout
from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter

from ui.list_page import ListPage
from ui.inventaire_import_dialog import InventaireImportDialog
from modules.stock_manager import StockManager


def date_fr(valeur):
    """
    Les dates sont stockées en AAAA-MM-JJ. On les affiche
    partout en JJ/MM/AAAA.
    """

    if not valeur:
        return ""

    morceaux = str(valeur)[:10].split("-")

    if len(morceaux) != 3:
        return str(valeur)

    return f"{morceaux[2]}/{morceaux[1]}/{morceaux[0]}"


class MouvementDialog(QDialog):
    """
    Saisie d'une entrée ou d'une sortie de stock à la main :
    casse, perte, retour fournisseur, cadeau, correction...

    Le motif est obligatoire : c'est lui qui justifiera le
    mouvement dans l'historique, des mois plus tard.
    """

    def __init__(self, nom_produit, prix_moyen=0.0, parent=None):

        super().__init__(parent)

        self.setWindowTitle(f"Mouvement de stock — {nom_produit}")
        self.setMinimumWidth(480)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 18, 18, 18)
        principal.setSpacing(14)

        titre = QLabel(nom_produit)
        police = QFont()
        police.setPointSize(13)
        police.setBold(True)
        titre.setFont(police)
        principal.addWidget(titre)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.sens = QComboBox()
        self.sens.addItem("➕ Entrée de stock", StockManager.ENTREE)
        self.sens.addItem("➖ Sortie de stock", StockManager.SORTIE)
        self.sens.currentIndexChanged.connect(self._basculerPrix)
        formulaire.addRow("Sens du mouvement", self.sens)

        self.quantite = QSpinBox()
        self.quantite.setMinimum(1)
        self.quantite.setMaximum(999999)
        formulaire.addRow("Quantité", self.quantite)

        self.dateMouvement = QDateEdit()
        self.dateMouvement.setCalendarPopup(True)
        self.dateMouvement.setDate(QDate.currentDate())
        formulaire.addRow("Date de l'opération", self.dateMouvement)

        self.motif = QComboBox()
        self.motif.setEditable(True)
        self.motif.addItems([
            "",
            "Casse",
            "Produit abîmé",
            "Perte",
            "Vol",
            "Retour client remis en stock",
            "Retour fournisseur",
            "Cadeau / échantillon",
            "Usage interne",
            "Régularisation",
        ])
        formulaire.addRow("Motif", self.motif)

        self.prixUnitaire = QDoubleSpinBox()
        self.prixUnitaire.setDecimals(2)
        self.prixUnitaire.setMaximum(999999)
        self.prixUnitaire.setSuffix(" € HT")
        self.prixUnitaire.setValue(prix_moyen or 0.0)
        self.labelPrix = QLabel("Prix d'achat unitaire")
        formulaire.addRow(self.labelPrix, self.prixUnitaire)

        principal.addLayout(formulaire)

        self.aide = QLabel(
            "Le motif est obligatoire : il justifiera ce "
            "mouvement dans l'historique du produit."
        )
        self.aide.setWordWrap(True)
        self.aide.setStyleSheet("color:#64748b; font-size:12px;")
        principal.addWidget(self.aide)

        boutons = QHBoxLayout()
        boutons.addStretch()

        annuler = QPushButton("Annuler")
        annuler.clicked.connect(self.reject)
        boutons.addWidget(annuler)

        valider = QPushButton("Enregistrer")
        valider.clicked.connect(self._valider)
        boutons.addWidget(valider)

        principal.addLayout(boutons)

    def _basculerPrix(self):
        """
        Le prix d'achat n'a de sens que pour une entrée :
        une sortie ne modifie pas le prix moyen du stock.
        """

        entree = self.sens.currentData() == StockManager.ENTREE

        self.prixUnitaire.setVisible(entree)
        self.labelPrix.setVisible(entree)

    def _valider(self):

        if not self.motif.currentText().strip():

            QMessageBox.warning(
                self,
                "Motif manquant",
                "Indique un motif : c'est ce qui permettra de "
                "comprendre ce mouvement plus tard."
            )
            return

        self.accept()

    def valeurs(self):

        return {
            "sens": self.sens.currentData(),
            "quantite": self.quantite.value(),
            "date": self.dateMouvement.date().toString("yyyy-MM-dd"),
            "motif": self.motif.currentText().strip(),
            "prix": (
                self.prixUnitaire.value()
                if self.sens.currentData() == StockManager.ENTREE
                else None
            ),
        }


class InventaireDialog(QDialog):
    """
    Comptage physique d'un produit.

    Demande la quantité réellement comptée, et — quand le
    comptage fait MONTER le stock — le prix d'achat unitaire
    des exemplaires qui entrent. Sans ce prix, la quantité
    serait juste mais la valeur resterait à zéro.
    """

    def __init__(
        self,
        nom_produit,
        quantite_actuelle,
        prix_moyen=0.0,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle(f"Inventaire — {nom_produit}")
        self.setMinimumWidth(500)

        self.quantite_actuelle = quantite_actuelle

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 18, 18, 18)
        principal.setSpacing(14)

        titre = QLabel(nom_produit)
        police = QFont()
        police.setPointSize(13)
        police.setBold(True)
        titre.setFont(police)
        principal.addWidget(titre)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        actuel = QLabel(str(quantite_actuelle))
        actuel.setStyleSheet("font-weight:600; color:#0f2f5c;")
        formulaire.addRow("Stock enregistré", actuel)

        self.quantiteComptee = QSpinBox()
        self.quantiteComptee.setMinimum(0)
        self.quantiteComptee.setMaximum(999999)
        self.quantiteComptee.setValue(quantite_actuelle)
        self.quantiteComptee.valueChanged.connect(self._majEcart)
        formulaire.addRow("Quantité réellement comptée", self.quantiteComptee)

        self.dateInventaire = QDateEdit()
        self.dateInventaire.setCalendarPopup(True)
        self.dateInventaire.setDate(QDate.currentDate())
        formulaire.addRow("Date du comptage", self.dateInventaire)

        self.prixUnitaire = QDoubleSpinBox()
        self.prixUnitaire.setDecimals(2)
        self.prixUnitaire.setMaximum(999999)
        self.prixUnitaire.setSuffix(" € HT")
        self.prixUnitaire.setValue(prix_moyen or 0.0)
        self.labelPrix = QLabel("Prix d'achat unitaire")
        formulaire.addRow(self.labelPrix, self.prixUnitaire)

        self.commentaire = QLineEdit()
        self.commentaire.setPlaceholderText(
            "Facultatif : inventaire annuel, recomptage rayon..."
        )
        formulaire.addRow("Remarque", self.commentaire)

        principal.addLayout(formulaire)

        self.ecart = QLabel()
        self.ecart.setWordWrap(True)
        principal.addWidget(self.ecart)

        boutons = QHBoxLayout()
        boutons.addStretch()

        annuler = QPushButton("Annuler")
        annuler.clicked.connect(self.reject)
        boutons.addWidget(annuler)

        valider = QPushButton("Enregistrer")
        valider.clicked.connect(self._valider)
        boutons.addWidget(valider)

        principal.addLayout(boutons)

        self._majEcart()

    def _majEcart(self):
        """
        Affiche l'écart en clair, et n'expose le prix d'achat
        que lorsqu'il sert réellement — c'est-à-dire quand le
        comptage fait entrer de la marchandise.
        """

        ecart = self.quantiteComptee.value() - self.quantite_actuelle

        entree = ecart > 0

        self.prixUnitaire.setVisible(entree)
        self.labelPrix.setVisible(entree)

        if ecart == 0:

            self.ecart.setText("Aucun écart : le stock est juste.")
            self.ecart.setStyleSheet("color:#1e7d32; font-weight:600;")

        elif entree:

            self.ecart.setText(
                f"Écart : +{ecart} — {ecart} exemplaire(s) vont "
                f"entrer en stock. Renseigne leur prix d'achat "
                f"pour que la valeur du stock reste juste."
            )
            self.ecart.setStyleSheet("color:#1e7d32; font-weight:600;")

        else:

            self.ecart.setText(
                f"Écart : {ecart} — {abs(ecart)} exemplaire(s) "
                f"vont sortir du stock."
            )
            self.ecart.setStyleSheet("color:#c0392b; font-weight:600;")

    def _valider(self):

        ecart = self.quantiteComptee.value() - self.quantite_actuelle

        if ecart > 0 and self.prixUnitaire.value() <= 0:

            reponse = QMessageBox.question(
                self,
                "Prix d'achat non renseigné",
                "Sans prix d'achat, ces exemplaires entreront "
                "en stock avec une valeur de 0 €, et la valeur "
                "totale de ton stock sera sous-évaluée.\n\n"
                "Enregistrer quand même ?"
            )

            if reponse != QMessageBox.StandardButton.Yes:
                return

        self.accept()

    def valeurs(self):

        ecart = self.quantiteComptee.value() - self.quantite_actuelle

        return {
            "ecart": ecart,
            "date": self.dateInventaire.date().toString("yyyy-MM-dd"),
            "prix": (
                self.prixUnitaire.value() if ecart > 0 else None
            ),
            "commentaire": self.commentaire.text().strip(),
        }


class MouvementsDialog(QDialog):
    """
    Historique des entrées et sorties d'un produit : chaque
    ligne dit d'où vient le mouvement, à quelle date, et
    pourquoi.
    """

    ORIGINES = {
        "creation": "Création de la fiche",
        "achat": "Réception fournisseur",
        "commande": "Commande client",
        "manuel": "Saisie manuelle",
        "inventaire": "Inventaire",
        "reprise": "Reprise du stock initial",
    }

    def __init__(
        self, produit_id, nom_produit, parent=None, variation_id=None
    ):

        super().__init__(parent)

        self.setWindowTitle(f"Mouvements — {nom_produit}")
        self.resize(920, 500)

        self.manager = StockManager()

        principal = QVBoxLayout(self)
        principal.setContentsMargins(16, 16, 16, 16)
        principal.setSpacing(12)

        titre = QLabel(nom_produit)
        police = QFont()
        police.setPointSize(13)
        police.setBold(True)
        titre.setFont(police)
        principal.addWidget(titre)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date",
            "Sens",
            "Quantité",
            "Justificatif",
            "Prix unitaire HT",
            "Motif",
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        entete = self.table.horizontalHeader()
        entete.setSectionResizeMode(QHeaderView.ResizeToContents)
        entete.setSectionResizeMode(5, QHeaderView.Stretch)

        principal.addWidget(self.table)

        self.resume = QLabel()
        self.resume.setStyleSheet("color:#0f2f5c; font-weight:600;")
        principal.addWidget(self.resume)

        bas = QHBoxLayout()
        bas.addStretch()

        fermer = QPushButton("Fermer")
        fermer.clicked.connect(self.accept)
        bas.addWidget(fermer)

        principal.addLayout(bas)

        self.charger(produit_id, variation_id)

    def charger(self, produit_id, variation_id=None):

        mouvements = self.manager.mouvements(
            produit_id, variation_id=variation_id
        )

        self.table.setRowCount(0)

        total_entrees = 0
        total_sorties = 0

        for mouvement in mouvements:

            ligne = self.table.rowCount()
            self.table.insertRow(ligne)

            entree = mouvement["type"] != "SORTIE"

            if entree:
                total_entrees += mouvement["quantite"] or 0
            else:
                total_sorties += mouvement["quantite"] or 0

            prix = mouvement["prix_unitaire_ht"]

            valeurs = [
                date_fr(mouvement["date"]),
                "Entrée" if entree else "Sortie",
                f"{'+' if entree else '-'}{mouvement['quantite']}",
                self.ORIGINES.get(
                    mouvement["origine"] or "",
                    (mouvement["origine"] or "").capitalize()
                ),
                (
                    f"{prix:.2f} €".replace(".", ",")
                    if prix is not None else ""
                ),
                mouvement["commentaire"] or "",
            ]

            for colonne, valeur in enumerate(valeurs):

                cellule = QTableWidgetItem(str(valeur))

                if colonne in (1, 2):
                    cellule.setForeground(
                        QColor("#1e7d32") if entree
                        else QColor("#c0392b")
                    )

                self.table.setItem(ligne, colonne, cellule)

        self.resume.setText(
            f"Total entrées : +{total_entrees}     "
            f"Total sorties : -{total_sorties}     "
            f"Stock actuel : {total_entrees - total_sorties}"
        )


class StockPage(ListPage):
    """
    État du stock : quantités réelles et valeur.

    Les quantités ne se tapent pas dans un tableau : elles
    résultent des mouvements (création de fiche, réceptions
    fournisseur, commandes clients, mouvements manuels,
    inventaires). Chaque changement laisse donc une trace
    datée et motivée.

    Un produit à variations n'apparaît pas en une ligne :
    chacune de ses tailles a la sienne, avec son propre
    stock et sa propre valeur.

    Les bundles apparaissent avec le nombre d'exemplaires
    montables à partir du stock de leurs composants, et sans
    valeur : celle-ci est déjà comptée dans les composants.
    """

    def __init__(self):

        super().__init__("🗃️ Stock")

        self.manager = StockManager()

        ####################################################
        # Barre d'outils
        ####################################################

        self.btnAjouter.setText("📦 Entrée / Sortie")
        self.btnAjouter.clicked.connect(self.mouvementManuel)

        self.btnModifier.setText("📋 Inventaire")
        self.btnModifier.clicked.connect(self.inventaire)

        self.btnExporter.setText("🖨️ Imprimer")
        self.btnExporter.clicked.connect(self.imprimer)

        self.btnSupprimer.setVisible(False)

        self.btnImporter.setText("📥 Importer un inventaire")
        self.btnImporter.clicked.connect(self.importerInventaire)

        ####################################################
        # Date du jour
        ####################################################

        self.labelDuJour = QLabel()
        police = QFont()
        police.setPointSize(11)
        police.setBold(True)
        self.labelDuJour.setFont(police)
        self.labelDuJour.setStyleSheet(
            "color:#0f2f5c; padding:2px 10px 8px 10px;"
        )
        self.layout().insertWidget(1, self.labelDuJour)

        ####################################################
        # Tableau
        ####################################################

        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "SKU",
            "EAN / Gencod",
            "Produit",
            "Type",
            "Quantité",
            "Prix moyen HT",
            "Valeur HT",
        ])

        self.table.setColumnHidden(0, True)

        self.table.doubleClicked.connect(self.voirMouvements)

        self.recherche.textChanged.connect(self.filtrer)

        ####################################################
        # Total
        ####################################################

        self.totalLabel = QLabel()
        policeTotal = QFont()
        policeTotal.setPointSize(12)
        policeTotal.setBold(True)
        self.totalLabel.setFont(policeTotal)
        self.totalLabel.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )
        self.totalLabel.setStyleSheet(
            "color:#0f2f5c; padding:6px 10px;"
        )

        self.layout().addWidget(self.totalLabel)

        self.charger()

    ########################################################
    # Chargement
    ########################################################

    def charger(self):

        self.labelDuJour.setText(
            f"État du stock au {date_fr(date.today().isoformat())}"
        )

        self.table.setRowCount(0)

        for produit in self.manager.etat_stock():

            ligne = self.table.rowCount()
            self.table.insertRow(ligne)

            est_bundle = produit["type"] == "Bundle"

            valeurs = [
                produit["produit_id"],
                produit["sku"],
                produit["ean"],
                produit["nom"],
                produit["type"],
                produit["quantite"],
                self._euros(produit["prix_moyen"]),
                self._euros(produit["valeur"]),
            ]

            for colonne, valeur in enumerate(valeurs):

                cellule = QTableWidgetItem(str(valeur))

                # La taille concernée voyage avec la ligne,
                # sans occuper de colonne à l'écran.
                if colonne == 0:
                    cellule.setData(
                        Qt.ItemDataRole.UserRole,
                        produit.get("variation_id"),
                    )

                if colonne in (5, 6, 7):
                    cellule.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter
                    )

                if est_bundle:
                    cellule.setForeground(QColor("#5b6b7f"))

                elif colonne == 5 and produit["quantite"] <= 0:
                    cellule.setForeground(QColor("#c0392b"))

                self.table.setItem(ligne, colonne, cellule)

        self._afficherTotal()

    def _afficherTotal(self):

        total = self.manager.valeur_totale()

        self.totalLabel.setText(
            f"Valeur totale du stock : {total:,.2f} €"
            .replace(",", " ")
            .replace(".", ",")
        )

    def _euros(self, valeur):

        if valeur is None:
            return "—"

        return f"{valeur:.2f} €".replace(".", ",")

    ########################################################
    # Sélection
    ########################################################

    def _produitSelectionne(self, message=True):

        ligne = self.table.currentRow()

        if ligne < 0:

            if message:
                QMessageBox.information(
                    self,
                    "Aucun produit",
                    "Sélectionne d'abord un produit dans la liste."
                )
            return None

        return {
            "id": int(self.table.item(ligne, 0).text()),
            "variation_id": self.table.item(ligne, 0).data(
                Qt.ItemDataRole.UserRole
            ),
            "nom": self.table.item(ligne, 3).text(),
            "type": self.table.item(ligne, 4).text(),
            "quantite": int(self.table.item(ligne, 5).text()),
        }

    def _refuserBundle(self, produit, action):

        if produit["type"] != "Bundle":
            return False

        QMessageBox.information(
            self,
            "Bundle",
            f"Un bundle n'a pas de stock à lui : sa quantité "
            f"est calculée à partir de ses composants.\n\n"
            f"Fais {action} sur les produits qui le composent."
        )
        return True

    ########################################################
    # Mouvement manuel (entrée / sortie)
    ########################################################

    def mouvementManuel(self):

        produit = self._produitSelectionne()

        if produit is None:
            return

        if self._refuserBundle(produit, "le mouvement"):
            return

        dialog = MouvementDialog(
            produit["nom"],
            self.manager.prix_moyen(
                produit["id"], produit["variation_id"]
            ),
            self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        saisie = dialog.valeurs()

        if saisie["sens"] == StockManager.SORTIE:

            if saisie["quantite"] > produit["quantite"]:

                reponse = QMessageBox.question(
                    self,
                    "Stock insuffisant",
                    f"Tu sors {saisie['quantite']} exemplaires "
                    f"alors qu'il n'en reste que "
                    f"{produit['quantite']} en stock.\n\n"
                    f"Le stock passera en négatif. Continuer ?"
                )

                if reponse != QMessageBox.StandardButton.Yes:
                    return

        try:

            # On écrit le mouvement nous-mêmes plutôt que de
            # passer par mouvement_manuel() : c'est le seul
            # moyen de viser une taille précise. Le motif est
            # déjà rendu obligatoire par la fenêtre de saisie.
            self.manager.enregistrer_mouvement(
                produit_id=produit["id"],
                type_mouvement=saisie["sens"],
                quantite=saisie["quantite"],
                origine="manuel",
                reference="",
                prix_unitaire_ht=saisie["prix"],
                commentaire=saisie["motif"],
                date_mouvement=saisie["date"],
                variation_id=produit["variation_id"],
            )

        except ValueError as erreur:

            QMessageBox.warning(self, "Mouvement refusé", str(erreur))
            return

        self.charger()

    ########################################################
    # Inventaire
    ########################################################

    def inventaire(self):

        produit = self._produitSelectionne()

        if produit is None:
            return

        if self._refuserBundle(produit, "l'inventaire"):
            return

        dialog = InventaireDialog(
            produit["nom"],
            produit["quantite"],
            self.manager.prix_moyen(
                produit["id"], produit["variation_id"]
            ),
            self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        saisie = dialog.valeurs()
        ecart = saisie["ecart"]

        if ecart == 0:

            QMessageBox.information(
                self,
                "Inventaire",
                "Aucun écart : le stock était juste."
            )
            return

        # On écrit le mouvement nous-mêmes plutôt que de
        # passer par corriger() : c'est le seul moyen de
        # porter le prix d'achat saisi, et de garder
        # l'origine « inventaire » dans l'historique.
        remarque = saisie["commentaire"] or "Inventaire"

        self.manager.enregistrer_mouvement(
            produit_id=produit["id"],
            type_mouvement=(
                StockManager.ENTREE if ecart > 0
                else StockManager.SORTIE
            ),
            quantite=abs(ecart),
            origine="inventaire",
            reference="",
            prix_unitaire_ht=saisie["prix"],
            commentaire=f"{remarque} — écart {ecart:+d}",
            date_mouvement=saisie["date"],
            variation_id=produit["variation_id"],
        )

        self.charger()

        QMessageBox.information(
            self,
            "Inventaire",
            f"Écart enregistré : {ecart:+d}.\n\n"
            "Le mouvement est visible dans l'historique du "
            "produit."
        )

    ########################################################
    # Import d'un inventaire au collecteur
    ########################################################

    def importerInventaire(self):
        """
        Ouvre la fenêtre d'import d'un comptage réalisé au
        collecteur de données. Le tableau est rechargé après
        coup pour que les nouvelles quantités s'affichent.
        """

        dialog = InventaireImportDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.charger()

    ########################################################
    # Historique
    ########################################################

    def voirMouvements(self):

        produit = self._produitSelectionne(message=False)

        if produit is None:
            return

        if self._refuserBundle(produit, "la consultation"):
            return

        MouvementsDialog(
            produit["id"],
            produit["nom"],
            self,
            produit["variation_id"],
        ).exec()

    ########################################################
    # Impression
    ########################################################

    def imprimer(self):
        """
        Aperçu avant impression de l'état du stock. La
        fenêtre d'aperçu permet aussi d'enregistrer en PDF.
        """

        try:

            document = QTextDocument()
            document.setHtml(self._html())

            imprimante = QPrinter(QPrinter.PrinterMode.HighResolution)

            # L'orientation passe par QPageLayout : l'ancienne
            # constante QPrinter.Orientation n'existe plus dans
            # les versions récentes de PySide6, et l'utiliser
            # faisait échouer le bouton en silence.
            imprimante.setPageOrientation(
                QPageLayout.Orientation.Portrait
            )

            apercu = QPrintPreviewDialog(imprimante, self)
            apercu.setWindowTitle("Impression de l'état du stock")
            apercu.resize(1000, 750)
            apercu.paintRequested.connect(document.print_)
            apercu.exec()

        except Exception as erreur:

            # Un bouton qui ne fait rien est le pire des
            # défauts : on montre toujours ce qui a échoué.
            QMessageBox.critical(
                self,
                "Impression impossible",
                f"L'aperçu n'a pas pu s'ouvrir :\n\n{erreur}\n\n"
                "Vérifie qu'au moins une imprimante est "
                "installée sur le poste (« Microsoft Print to "
                "PDF » suffit)."
            )

    def _html(self):

        jour = date_fr(date.today().isoformat())

        lignes = []

        for produit in self.manager.etat_stock():

            lignes.append(
                "<tr>"
                f"<td>{produit['sku']}</td>"
                f"<td>{produit['ean']}</td>"
                f"<td>{produit['nom']}</td>"
                f"<td>{produit['type']}</td>"
                f"<td align='right'>{produit['quantite']}</td>"
                f"<td align='right'>{self._euros(produit['prix_moyen'])}</td>"
                f"<td align='right'>{self._euros(produit['valeur'])}</td>"
                "</tr>"
            )

        total = self.manager.valeur_totale()

        total_texte = (
            f"{total:,.2f} €".replace(",", " ").replace(".", ",")
        )

        return f"""
        <html>
        <body style="font-family:Arial; font-size:10pt;">

            <h2 style="color:#0f2f5c; margin-bottom:2px;">
                Pop Licence — État du stock
            </h2>

            <p style="color:#555; margin-top:0;">
                Édité le {jour}
            </p>

            <table width="100%" cellspacing="0" cellpadding="5"
                   border="1" style="border-collapse:collapse;">

                <thead>
                    <tr style="background:#0f2f5c; color:white;">
                        <th align="left">SKU</th>
                        <th align="left">EAN / Gencod</th>
                        <th align="left">Produit</th>
                        <th align="left">Type</th>
                        <th align="right">Quantité</th>
                        <th align="right">Prix moyen HT</th>
                        <th align="right">Valeur HT</th>
                    </tr>
                </thead>

                <tbody>
                    {''.join(lignes)}
                </tbody>

            </table>

            <h3 style="text-align:right; color:#0f2f5c;">
                Valeur totale du stock : {total_texte}
            </h3>

            <p style="color:#777; font-size:8pt;">
                Les bundles sont affichés sans valeur : elle est
                déjà comptée dans leurs composants.
            </p>

        </body>
        </html>
        """

    ########################################################
    # Recherche
    ########################################################

    def filtrer(self):

        texte = self.recherche.text().strip().lower()

        for ligne in range(self.table.rowCount()):

            # SKU, EAN, nom et type : on peut donc chercher
            # aussi bien « S000012 » qu'un code-barres complet
            # scanné à la douchette.
            contenu = " ".join(
                self.table.item(ligne, colonne).text().lower()
                for colonne in (1, 2, 3, 4)
                if self.table.item(ligne, colonne)
            )

            self.table.setRowHidden(ligne, texte not in contenu)