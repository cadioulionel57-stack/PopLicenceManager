from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QAbstractItemView,
    QFileDialog,
)

from ui.list_page import ListPage
from ui.commande_dialog import CommandeDialog
from modules.commande_manager import CommandeManager


class CommandesPage(ListPage):
    """
    Écran de gestion des commandes : import à venir plus
    tard (CSV/API WiziShop, Base.com) — pour l'instant,
    saisie manuelle complète (client, panier, frais de port
    client vs réel, retours par produit), plus un export CSV
    d'archive (indépendant de WiziShop) sur les commandes
    sélectionnées.
    """

    def __init__(self):

        super().__init__("🛒 Commandes")

        self.manager = CommandeManager()

        self.table.setColumnCount(10)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Numéro",
            "Date",
            "Canal",
            "Client",
            "Statut",
            "Payé",
            "Montant TTC",
            "Port client",
            "Gain net réel",
        ])

        self.table.setColumnHidden(0, True)

        # Sélection multiple (Ctrl/Shift + clic) — nécessaire
        # pour exporter plusieurs commandes en une fois,
        # comme sur l'écran Produits.
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )

        self.btnAjouter.clicked.connect(self.ajouterCommande)
        self.btnModifier.clicked.connect(self.modifierCommande)
        self.btnSupprimer.clicked.connect(self.supprimerCommande)

        # Import (depuis WiziShop) : chantier séparé, pas
        # encore construit — masqué pour l'instant, comme sur
        # l'écran Produits en attendant l'export.
        self.btnImporter.setVisible(False)
        self.btnExporter.clicked.connect(self.exporterCommandes)

        self.table.doubleClicked.connect(self.modifierCommande)

        self.recherche.textChanged.connect(self.filtrer)

        self.charger()

    def charger(self):

        self.table.setRowCount(0)

        commandes = self.manager.tous()

        for ligne, commande in enumerate(commandes):

            self.table.insertRow(ligne)

            gain = self.manager.gain_net_reel(commande["id"])
            gain_texte = (
                f"{gain['gain_net_ht']:.2f} € HT" if gain else "—"
            )

            valeurs = [
                str(commande["id"]),
                commande["numero"] or "",
                commande["date_commande"] or "",
                commande["nom_canal"] or "",
                commande["nom_client"] or "",
                commande["statut"] or "",
                "💰 Payée" if commande["paye"] else "⏳ À venir",
                f"{commande['montant_ttc'] or 0:.2f} €",
                f"{commande['frais_port_client_ttc'] or 0:.2f} €",
                gain_texte,
            ]

            for colonne, valeur in enumerate(valeurs):

                item = QTableWidgetItem(valeur)

                if colonne == 8 and gain:

                    if gain["gain_net_ht"] < 0:
                        item.setForeground(self._couleurRouge())
                    else:
                        item.setForeground(self._couleurVerte())

                self.table.setItem(
                    ligne,
                    colonne,
                    item
                )

    def _couleurRouge(self):

        from PySide6.QtGui import QColor
        return QColor("#c0392b")

    def _couleurVerte(self):

        from PySide6.QtGui import QColor
        return QColor("#1e7d32")

    def ajouterCommande(self):

        dialog = CommandeDialog("Nouvelle commande")

        if dialog.exec() != CommandeDialog.DialogCode.Accepted:
            return

        self._enregistrerDepuisDialogue(dialog)

    def modifierCommande(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une commande."
            )
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        self.ouvrirCommandeParId(identifiant)

    def ouvrirCommandeParId(self, identifiant):
        """
        Ouvre directement la fenêtre de modification d'une
        commande à partir de son identifiant — utilisé
        depuis l'écran SAV (double-clic sur un retour) sans
        passer par une sélection dans le tableau des
        commandes.
        """

        commande = self.manager.obtenir(identifiant)
        lignes = self.manager.lignes(identifiant)
        retours = self.manager.retours_commande(identifiant)

        dialog = CommandeDialog(
            "Modifier la commande",
            commande=commande,
            lignes=lignes,
            retours=retours,
        )

        if dialog.exec() != CommandeDialog.DialogCode.Accepted:
            return

        self._enregistrerDepuisDialogue(dialog, identifiant)

    def _enregistrerDepuisDialogue(self, dialog, identifiant=None):

        client_id = dialog.client.currentData()

        if client_id is None:

            QMessageBox.warning(
                self,
                "Client manquant",
                "Sélectionne ou crée un client avant "
                "d'enregistrer la commande."
            )
            return

        lignes_saisies = dialog.lignes_saisies()

        montant_ttc = sum(
            l["prix_unitaire_ttc"] * l["quantite"]
            for l in lignes_saisies
        )
        montant_ht = sum(
            l["prix_unitaire_ht"] * l["quantite"]
            for l in lignes_saisies
        )

        date_expedition = None

        if dialog.dejaExpediee.isChecked():
            date_expedition = dialog.dateExpedition.date().toString(
                "yyyy-MM-dd"
            )

        if identifiant is None:

            identifiant = self.manager.ajouter(
                numero=dialog.numero.text().strip(),
                canal_id=dialog.canal.id(),
                client_id=client_id,
                date_commande=dialog.dateCommande.date().toString("yyyy-MM-dd"),
                date_expedition=date_expedition,
                statut=dialog.statut.currentText(),
                montant_ht=montant_ht,
                montant_ttc=montant_ttc,
                frais_port_client_ttc=dialog.fraisPortClient.value(),
                frais_port_reel_ht=dialog.fraisPortReel.value(),
                papier_cadeau_actif=dialog.papierCadeauActif.isChecked(),
                papier_cadeau_emballage_id=dialog.papierCadeauEmballage.currentData() if dialog.papierCadeauActif.isChecked() else None,
                papier_cadeau_supplement_id=dialog.papierCadeauSupplement.currentData() if dialog.papierCadeauActif.isChecked() else None,
                tracking=dialog.tracking.text(),
                commentaire=dialog.commentaire.toPlainText(),
            )

        else:

            self.manager.modifier(
                identifiant=identifiant,
                numero=dialog.numero.text().strip(),
                canal_id=dialog.canal.id(),
                client_id=client_id,
                date_commande=dialog.dateCommande.date().toString("yyyy-MM-dd"),
                date_expedition=date_expedition,
                statut=dialog.statut.currentText(),
                montant_ht=montant_ht,
                montant_ttc=montant_ttc,
                frais_port_client_ttc=dialog.fraisPortClient.value(),
                frais_port_reel_ht=dialog.fraisPortReel.value(),
                papier_cadeau_actif=dialog.papierCadeauActif.isChecked(),
                papier_cadeau_emballage_id=dialog.papierCadeauEmballage.currentData() if dialog.papierCadeauActif.isChecked() else None,
                papier_cadeau_supplement_id=dialog.papierCadeauSupplement.currentData() if dialog.papierCadeauActif.isChecked() else None,
                tracking=dialog.tracking.text(),
                commentaire=dialog.commentaire.toPlainText(),
            )

        # Panier : remplacement complet des lignes
        self.manager.definir_lignes(identifiant, lignes_saisies)

        # Retours : rattachés aux nouvelles lignes fraîchement
        # créées, en les faisant correspondre par nom de
        # produit (les lignes sont toujours recréées à chaque
        # sauvegarde, donc leurs identifiants changent).
        nouvelles_lignes = self.manager.lignes(identifiant)

        for retour in dialog.retours_saisis():

            ligne_correspondante = next(
                (
                    l for l in nouvelles_lignes
                    if l["nom_produit"] == retour.get(
                        "nom_produit", retour.get("produit_nom")
                    )
                ),
                None
            )

            if ligne_correspondante is None:
                continue

            self.manager.ajouter_retour(
                ligne_commande_id=ligne_correspondante["id"],
                date_retour=retour.get("date_retour", ""),
                motif=retour.get("motif", ""),
                statut=retour.get("statut", "Demandé"),
                montant_rembourse_ttc=retour.get("montant_rembourse_ttc", 0),
                frais_reexpedition_ht=retour.get("frais_reexpedition_ht", 0),
                cout_retour_ht=retour.get("cout_retour_ht", 0),
                notes=retour.get("notes", ""),
            )

        self.manager.marquer_paye(
            identifiant,
            dialog.commandePayee.isChecked(),
            dialog.datePaiement.date().toString("yyyy-MM-dd")
            if dialog.commandePayee.isChecked() else None,
        )

        self.charger()

    def supprimerCommande(self):

        ligne = self.table.currentRow()

        if ligne == -1:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez une commande."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cette commande ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(
            self.table.item(ligne, 0).text()
        )

        self.manager.supprimer(identifiant)

        self.charger()

    def _lignesSelectionnees(self):
        """
        Renvoie la liste des numéros de ligne réellement
        sélectionnées (une seule fois par ligne, même si
        plusieurs cellules de la même ligne sont sélectionnées).
        """

        lignes = sorted({
            index.row() for index in self.table.selectedIndexes()
        })

        return lignes

    def _commandesSelectionnees(self):

        identifiants = []

        for ligne in self._lignesSelectionnees():

            item_id = self.table.item(ligne, 0)

            if item_id is not None:
                identifiants.append(int(item_id.text()))

        return identifiants

    def exporterCommandes(self):
        """
        Exporte en CSV les commandes actuellement sélectionnées
        dans le tableau (et seulement celles-là) — un fichier
        d'archive perso, indépendant de WiziShop.
        """

        identifiants = self._commandesSelectionnees()

        if not identifiants:

            QMessageBox.information(
                self,
                "Information",
                "Sélectionnez au moins une commande à exporter "
                "(Ctrl ou Shift + clic pour en sélectionner "
                "plusieurs)."
            )
            return

        chemin, _filtre = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'export des commandes",
            "export_commandes.csv",
            "Fichiers CSV (*.csv)"
        )

        if not chemin:
            return

        from modules.commande_export_manager import CommandeExportManager

        try:

            CommandeExportManager().exporter(identifiants, chemin)

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur d'export",
                f"L'export a échoué :\n{erreur}"
            )
            return

        QMessageBox.information(
            self,
            "Export terminé",
            f"{len(identifiants)} commande(s) exportée(s) avec "
            f"succès vers :\n{chemin}"
        )

    def filtrer(self):

        texte = self.recherche.text().lower().strip()

        for ligne in range(self.table.rowCount()):

            visible = False

            for colonne in range(1, self.table.columnCount()):

                item = self.table.item(ligne, colonne)

                if item and texte in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(
                ligne,
                not visible
            )