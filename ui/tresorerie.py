from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from modules.tresorerie_manager import TresorerieManager
from modules.commande_manager import CommandeManager
from modules.budget_publicitaire_manager import BudgetPublicitaireManager
from ui.charge_dialog import ChargeDialog
from ui.budget_pub_ligne_dialog import BudgetPubLigneDialog
from ui.budget_pub_depense_dialog import BudgetPubDepenseDialog


class TresoreriePage(QWidget):
    """
    Écran Trésorerie : solde du jour, charges récurrentes
    (loyer, prêt, crédit TVA...) avec suivi de paiement
    mensuel, et les 3 enveloppes (Croissance, Développement,
    Réserve).
    """

    def __init__(self):

        super().__init__()

        self.manager = TresorerieManager()
        self.managerBudgetPub = BudgetPublicitaireManager()

        self.setStyleSheet("""
        QWidget{ background:#f4f7fb; font-family:'Segoe UI'; }
        QLabel#titre{ font-size:24px; font-weight:600; color:#0f2f5c; }
        QFrame#card{
            background:white; border:1px solid #e1e8f0;
            border-radius:12px;
        }
        QLabel#kpiTitre{ font-size:12px; color:#888; }
        QLabel#kpiValeur{ font-size:24px; font-weight:bold; }
        QDoubleSpinBox{
            background:#f7f9fc; border:1px solid #d7e0ec;
            border-radius:7px; padding:6px 8px; font-size:11pt;
        }
        QPushButton{
            background:#144b8b; color:white; border:none;
            border-radius:8px; padding:9px 16px; font-weight:500;
        }
        QPushButton:hover{ background:#1d61b4; }
        QTableWidget{
            background:white; gridline-color:#eef1f6;
            alternate-background-color:#f8fafc;
        }
        QHeaderView::section{
            background:#0f2f5c; color:white; font-weight:600;
            border:none; padding:8px 6px;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        entete = QHBoxLayout()
        titre = QLabel("🏦 Trésorerie")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        ####################################################
        # Saisie du solde du jour
        ####################################################

        carteSolde = QFrame()
        carteSolde.setObjectName("card")
        layoutSolde = QHBoxLayout(carteSolde)

        layoutSolde.addWidget(QLabel("Solde bancaire du jour :"))

        self.champSolde = QDoubleSpinBox()
        self.champSolde.setDecimals(2)
        self.champSolde.setMaximum(9999999)
        self.champSolde.setSuffix(" € TTC")
        layoutSolde.addWidget(self.champSolde)

        self.btnEnregistrerSolde = QPushButton("💾 Enregistrer le solde du jour")
        self.btnEnregistrerSolde.clicked.connect(self.enregistrerSolde)
        layoutSolde.addWidget(self.btnEnregistrerSolde)

        layoutSolde.addStretch()

        layout.addWidget(carteSolde)

        ####################################################
        # KPI
        ####################################################

        def carte(titre_kpi, couleur="#144b8b"):

            cadre = QFrame()
            cadre.setObjectName("card")
            cadre.setMinimumHeight(100)
            l = QVBoxLayout(cadre)

            t = QLabel(titre_kpi)
            t.setObjectName("kpiTitre")

            v = QLabel("—")
            v.setObjectName("kpiValeur")
            v.setStyleSheet(f"color:{couleur};")

            l.addWidget(t)
            l.addWidget(v)
            l.addStretch()

            cadre.labelValeur = v
            return cadre

        ligneKpi1 = QHBoxLayout()

        self.carteSoldeActuel = carte("💰 Solde actuel", "#000000")
        self.carteChargesMois = carte("🧾 Charges du mois (restant)", "#c0392b")
        self.cartePrevisionnelle = carte("📈 Trésorerie prévisionnelle", "#144b8b")

        ligneKpi1.addWidget(self.carteSoldeActuel)
        ligneKpi1.addWidget(self.carteChargesMois)
        ligneKpi1.addWidget(self.cartePrevisionnelle)

        layout.addLayout(ligneKpi1)

        ligneKpi2 = QHBoxLayout()

        self.carteCroissance = carte("🌱 Fonds de Croissance", "#1e7d32")
        self.carteDeveloppement = carte("🛠 Fonds de Développement", "#8e44ad")
        self.carteReserve = carte("🛡 Réserve de Trésorerie", "#e67e22")
        self.carteRenouvellementStock = carte("📦 Renouvellement Stock", "#144b8b")

        ligneKpi2.addWidget(self.carteCroissance)
        ligneKpi2.addWidget(self.carteDeveloppement)
        ligneKpi2.addWidget(self.carteReserve)
        ligneKpi2.addWidget(self.carteRenouvellementStock)

        layout.addLayout(ligneKpi2)

        ligneAjustementStock = QHBoxLayout()
        ligneAjustementStock.addWidget(QLabel(
            "Ajustement manuel du Renouvellement Stock "
            "(positif pour ajouter, négatif pour retirer) :"
        ))

        self.champAjustementStock = QDoubleSpinBox()
        self.champAjustementStock.setDecimals(2)
        self.champAjustementStock.setMinimum(-999999)
        self.champAjustementStock.setMaximum(999999)
        self.champAjustementStock.setSuffix(" €")
        ligneAjustementStock.addWidget(self.champAjustementStock)

        self.btnAjustementStock = QPushButton("💾 Appliquer l'ajustement")
        self.btnAjustementStock.clicked.connect(self.enregistrerAjustementStock)
        ligneAjustementStock.addWidget(self.btnAjustementStock)

        ligneAjustementStock.addStretch()

        layout.addLayout(ligneAjustementStock)

        ####################################################
        # Charges du mois
        ####################################################

        entêteCharges = QHBoxLayout()
        entêteCharges.addWidget(QLabel("Charges récurrentes"))
        entêteCharges.addStretch()

        self.btnAjouterCharge = QPushButton("➕ Nouvelle charge")
        self.btnAjouterCharge.clicked.connect(self.ajouterCharge)
        entêteCharges.addWidget(self.btnAjouterCharge)

        self.btnModifierCharge = QPushButton("✏ Modifier")
        self.btnModifierCharge.clicked.connect(self.modifierCharge)
        entêteCharges.addWidget(self.btnModifierCharge)

        self.btnSupprimerCharge = QPushButton("🗑 Supprimer")
        self.btnSupprimerCharge.setStyleSheet("background:#c0392b;")
        self.btnSupprimerCharge.clicked.connect(self.supprimerCharge)
        entêteCharges.addWidget(self.btnSupprimerCharge)

        layout.addLayout(entêteCharges)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Catégorie", "Fréquence", "Montant",
            "Échéances", "Payé ce mois"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        ####################################################
        # Budget publicitaire
        ####################################################

        entêtePub = QHBoxLayout()
        entêtePub.addWidget(QLabel("📣 Budget publicitaire"))
        entêtePub.addStretch()

        self.btnAjouterLignePub = QPushButton("➕ Nouvelle enveloppe")
        self.btnAjouterLignePub.clicked.connect(self.ajouterLignePub)
        entêtePub.addWidget(self.btnAjouterLignePub)

        self.btnModifierLignePub = QPushButton("✏ Modifier l'enveloppe")
        self.btnModifierLignePub.clicked.connect(self.modifierLignePub)
        entêtePub.addWidget(self.btnModifierLignePub)

        self.btnSupprimerLignePub = QPushButton("🗑 Supprimer")
        self.btnSupprimerLignePub.setStyleSheet("background:#c0392b;")
        self.btnSupprimerLignePub.clicked.connect(self.supprimerLignePub)
        entêtePub.addWidget(self.btnSupprimerLignePub)

        layout.addLayout(entêtePub)

        sousTitrePub = QLabel(
            "Une ligne = une enveloppe globale (ex : Google "
            "Shopping, 5040€ sur 15 mois). Clique sur une "
            "ligne pour voir et remplir ses dépenses mois par "
            "mois juste en dessous."
        )
        sousTitrePub.setStyleSheet("color:#5a6b7d; font-size:9.5pt;")
        sousTitrePub.setWordWrap(True)
        layout.addWidget(sousTitrePub)

        self.tableBudgetPub = QTableWidget()
        self.tableBudgetPub.setColumnCount(6)
        self.tableBudgetPub.setHorizontalHeaderLabels([
            "ID", "Nom", "Enveloppe totale HT",
            "Dépensé à ce jour (cumul de tous les mois saisis)",
            "Restant sur l'enveloppe", "% déjà consommé"
        ])
        self.tableBudgetPub.setColumnHidden(0, True)
        self.tableBudgetPub.setAlternatingRowColors(True)
        self.tableBudgetPub.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableBudgetPub.verticalHeader().setVisible(False)
        self.tableBudgetPub.itemSelectionChanged.connect(
            self._chargerDetailMensuelPub
        )
        layout.addWidget(self.tableBudgetPub)

        ####################################################
        # Détail mensuel de la ligne sélectionnée
        ####################################################

        entêteDetailPub = QHBoxLayout()
        self.labelDetailPub = QLabel(
            "Détail mensuel — sélectionne une ligne ci-dessus"
        )
        entêteDetailPub.addWidget(self.labelDetailPub)
        entêteDetailPub.addStretch()

        self.btnAjouterMoisPub = QPushButton("➕ Ajouter un mois")
        self.btnAjouterMoisPub.clicked.connect(self.ajouterMoisDetailPub)
        entêteDetailPub.addWidget(self.btnAjouterMoisPub)

        layout.addLayout(entêteDetailPub)

        self.tableDetailPub = QTableWidget()
        self.tableDetailPub.setColumnCount(2)
        self.tableDetailPub.setHorizontalHeaderLabels([
            "Mois (AAAA-MM)", "Montant dépensé HT"
        ])
        self.tableDetailPub.setMaximumHeight(180)
        self.tableDetailPub.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableDetailPub.verticalHeader().setVisible(False)
        self.tableDetailPub.itemChanged.connect(
            self.enregistrerDetailMensuelPub
        )
        layout.addWidget(self.tableDetailPub)

        layout.addWidget(self.tableBudgetPub)

        self.charger()

    def charger(self):

        solde = self.manager.solde_actuel()

        if solde is not None:
            self.champSolde.setValue(solde)

        self.carteSoldeActuel.labelValeur.setText(
            f"{solde:.2f} €" if solde is not None else "Non renseigné"
        )

        mois_actuel = date.today().strftime("%Y-%m")

        charges_mois = self.manager.total_charges_mois(mois_actuel)
        self.carteChargesMois.labelValeur.setText(
            f"{charges_mois['restant']:.2f} €"
        )

        previsionnelle = self.manager.tresorerie_previsionnelle(mois_actuel)
        self.cartePrevisionnelle.labelValeur.setText(
            f"{previsionnelle:.2f} €"
        )

        self.carteCroissance.labelValeur.setText(
            f"{self.manager.fonds_croissance_actuel():.2f} €"
        )
        self.carteDeveloppement.labelValeur.setText(
            f"{self.manager.fonds_developpement():.2f} €"
        )
        self.carteReserve.labelValeur.setText(
            f"{self.manager.reserve_tresorerie():.2f} €"
        )
        self.carteRenouvellementStock.labelValeur.setText(
            f"{self.manager.renouvellement_stock_total():.2f} €"
        )
        self.champAjustementStock.setValue(
            self.manager.ajustement_manuel_stock()
        )

        self._chargerTableCharges(mois_actuel)
        self._chargerTableBudgetPub()

    def enregistrerAjustementStock(self):

        self.manager.definir_ajustement_manuel_stock(
            self.champAjustementStock.value()
        )

        self.charger()

    def _chargerTableBudgetPub(self):

        self.tableBudgetPub.setRowCount(0)

        for ligne, item in enumerate(self.managerBudgetPub.synthese()):

            self.tableBudgetPub.insertRow(ligne)

            ligne_data = item["ligne"]

            valeurs = [
                str(ligne_data["id"]),
                ligne_data["nom"] or "",
                f"{ligne_data['enveloppe_totale_ht'] or 0:.2f} € HT",
                f"{item['depense_ht']:.2f} € HT",
                f"{item['restant_ht']:.2f} € HT",
                f"{item['pourcentage_consomme']:.0f} %",
            ]

            for colonne, valeur in enumerate(valeurs):

                item_table = QTableWidgetItem(valeur)

                if colonne == 5:

                    pourcentage = item["pourcentage_consomme"]

                    if pourcentage >= 100:
                        item_table.setForeground(Qt.GlobalColor.red)
                    elif pourcentage >= 80:
                        item_table.setForeground(Qt.GlobalColor.darkYellow)

                self.tableBudgetPub.setItem(ligne, colonne, item_table)

    def ajouterLignePub(self):

        dialog = BudgetPubLigneDialog("Nouvelle enveloppe publicitaire")

        if dialog.exec() != BudgetPubLigneDialog.DialogCode.Accepted:
            return

        self.managerBudgetPub.ajouter_ligne(
            dialog.nom.text().strip(),
            dialog.enveloppeTotale.value(),
            dialog.dateDebut.text().strip(),
            dialog.dateFin.text().strip() or None,
        )

        self.charger()

    def modifierLignePub(self):

        ligne = self.tableBudgetPub.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une ligne.")
            return

        identifiant = int(self.tableBudgetPub.item(ligne, 0).text())
        ligne_data = self.managerBudgetPub.obtenir_ligne(identifiant)

        dialog = BudgetPubLigneDialog(
            "Modifier l'enveloppe",
            ligne_data["nom"], ligne_data["enveloppe_totale_ht"],
            ligne_data["date_debut"], ligne_data["date_fin"],
        )

        if dialog.exec() != BudgetPubLigneDialog.DialogCode.Accepted:
            return

        self.managerBudgetPub.modifier_ligne(
            identifiant,
            dialog.nom.text().strip(),
            dialog.enveloppeTotale.value(),
            dialog.dateDebut.text().strip(),
            dialog.dateFin.text().strip() or None,
        )

        self.charger()

    def supprimerLignePub(self):

        ligne = self.tableBudgetPub.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une ligne.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Supprimer cette enveloppe publicitaire ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.tableBudgetPub.item(ligne, 0).text())
        self.managerBudgetPub.supprimer_ligne(identifiant)

        self.charger()

    def _chargerDetailMensuelPub(self):
        """
        Affiche, dans le tableau du bas, toutes les dépenses
        déjà saisies pour la ligne sélectionnée en haut —
        modifiables directement dans le tableau (double-clic
        sur une cellule).
        """

        ligne = self.tableBudgetPub.currentRow()

        self.tableDetailPub.blockSignals(True)
        self.tableDetailPub.setRowCount(0)

        if ligne == -1:
            self.labelDetailPub.setText(
                "Détail mensuel — sélectionne une ligne ci-dessus"
            )
            self._ligne_pub_selectionnee = None
            self.tableDetailPub.blockSignals(False)
            return

        identifiant = int(self.tableBudgetPub.item(ligne, 0).text())
        ligne_data = self.managerBudgetPub.obtenir_ligne(identifiant)

        self._ligne_pub_selectionnee = identifiant
        self.labelDetailPub.setText(
            f"Détail mensuel — {ligne_data['nom']}"
        )

        depenses = self.managerBudgetPub.depenses_ligne(identifiant)

        for r, depense in enumerate(depenses):

            self.tableDetailPub.insertRow(r)

            itemMois = QTableWidgetItem(depense["mois"] or "")
            itemMontant = QTableWidgetItem(
                f"{depense['montant_reel_ht']:.2f}"
            )

            self.tableDetailPub.setItem(r, 0, itemMois)
            self.tableDetailPub.setItem(r, 1, itemMontant)

        self.tableDetailPub.blockSignals(False)

    def ajouterMoisDetailPub(self):

        if getattr(self, "_ligne_pub_selectionnee", None) is None:
            QMessageBox.information(
                self, "Information",
                "Sélectionne d'abord une ligne de budget en haut."
            )
            return

        ligne = self.tableDetailPub.rowCount()

        # Signaux bloqués le temps d'insérer la ligne vide —
        # sinon chaque setItem() déclenche une sauvegarde
        # prématurée, avec un mois par défaut qui pourrait
        # écraser un mois déjà rempli portant la même valeur.
        self.tableDetailPub.blockSignals(True)

        self.tableDetailPub.insertRow(ligne)

        self.tableDetailPub.setItem(ligne, 0, QTableWidgetItem(""))
        self.tableDetailPub.setItem(ligne, 1, QTableWidgetItem("0.00"))

        self.tableDetailPub.blockSignals(False)

        self.tableDetailPub.editItem(
            self.tableDetailPub.item(ligne, 0)
        )

    def enregistrerDetailMensuelPub(self, item):
        """
        Sauvegarde automatiquement dès qu'une cellule du
        détail mensuel est modifiée — pas besoin de bouton
        "Enregistrer" séparé.
        """

        if getattr(self, "_ligne_pub_selectionnee", None) is None:
            return

        ligne = item.row()

        item_mois = self.tableDetailPub.item(ligne, 0)
        item_montant = self.tableDetailPub.item(ligne, 1)

        if item_mois is None or item_montant is None:
            return

        mois = item_mois.text().strip()

        try:
            montant = float(item_montant.text().replace(",", "."))
        except ValueError:
            return

        if not mois:
            return

        self.managerBudgetPub.definir_depense_mois(
            self._ligne_pub_selectionnee, mois, montant
        )

        # Signaux bloqués pendant le rechargement du tableau
        # du haut, pour ne pas déclencher en cascade un
        # rechargement du détail du bas qui écraserait la
        # ligne qu'on vient tout juste d'ajouter.
        self.tableBudgetPub.blockSignals(True)
        self._chargerTableBudgetPub()

        for r in range(self.tableBudgetPub.rowCount()):

            if int(self.tableBudgetPub.item(r, 0).text()) == self._ligne_pub_selectionnee:
                self.tableBudgetPub.selectRow(r)
                break

        self.tableBudgetPub.blockSignals(False)

    def _chargerTableCharges(self, mois_iso):

        self.table.setRowCount(0)

        lignes = self.manager.charges_du_mois(mois_iso)

        for ligne, item in enumerate(lignes):

            self.table.insertRow(ligne)

            charge = item["charge"]

            echeances = (
                f"{charge['nombre_occurrences']} échéances"
                if charge["nombre_occurrences"]
                else "Récurrent"
            )

            self.table.setItem(ligne, 0, QTableWidgetItem(str(charge["id"])))
            self.table.setItem(ligne, 1, QTableWidgetItem(charge["nom"] or ""))

            libelle_cat = ChargeDialog.CATEGORIES.get(
                charge["categorie"], charge["categorie"]
            )
            self.table.setItem(ligne, 2, QTableWidgetItem(libelle_cat))

            libelle_freq = (
                "📆 Annuelle"
                if charge["frequence"] == "annuelle"
                else "📅 Mensuelle"
            )
            self.table.setItem(ligne, 3, QTableWidgetItem(libelle_freq))

            self.table.setItem(
                ligne, 4,
                QTableWidgetItem(f"{charge['montant_mensuel']:.2f} €")
            )
            self.table.setItem(ligne, 5, QTableWidgetItem(echeances))

            case = QCheckBox()
            case.setChecked(item["paye"])
            case.toggled.connect(
                lambda coche, cid=charge["id"], m=mois_iso: (
                    self.manager.marquer_paye(cid, m, coche),
                    self.charger(),
                )
            )

            conteneur = QWidget()
            layoutCase = QHBoxLayout(conteneur)
            layoutCase.addWidget(case)
            layoutCase.setAlignment(case, Qt.AlignmentFlag.AlignCenter)
            layoutCase.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(ligne, 6, conteneur)

    def enregistrerSolde(self):

        aujourdhui = date.today().isoformat()

        self.manager.definir_solde_jour(aujourdhui, self.champSolde.value())

        if not self.manager.fonds_deja_initialise():
            self.manager.initialiser_fonds_croissance(self.champSolde.value())

        self.charger()

        QMessageBox.information(
            self, "Enregistré", "Solde du jour enregistré."
        )

    def ajouterCharge(self):

        dialog = ChargeDialog("Nouvelle charge")

        if dialog.exec() != ChargeDialog.DialogCode.Accepted:
            return

        self.manager.ajouter_charge(
            dialog.nom.text().strip(),
            dialog.categorie.currentData(),
            dialog.montantMensuel.value(),
            dialog.moisDebut.text().strip(),
            dialog.nombre_occurrences_choisi(),
            dialog.frequence.currentData(),
            dialog.tvaApplicable.isChecked(),
        )

        self.charger()

    def modifierCharge(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une charge.")
            return

        identifiant = int(self.table.item(ligne, 0).text())
        charge = self.manager.obtenir_charge(identifiant)

        dialog = ChargeDialog(
            "Modifier la charge",
            charge["nom"], charge["categorie"], charge["montant_mensuel"],
            charge["mois_debut"], charge["nombre_occurrences"],
            charge["frequence"], bool(charge["tva_applicable"]),
        )

        if dialog.exec() != ChargeDialog.DialogCode.Accepted:
            return

        self.manager.modifier_charge(
            identifiant,
            dialog.nom.text().strip(),
            dialog.categorie.currentData(),
            dialog.montantMensuel.value(),
            dialog.moisDebut.text().strip(),
            dialog.nombre_occurrences_choisi(),
            dialog.frequence.currentData(),
            dialog.tvaApplicable.isChecked(),
        )

        self.charger()

    def supprimerCharge(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une charge.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Supprimer cette charge récurrente ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())
        self.manager.supprimer_charge(identifiant)

        self.charger()

    def alimenter_fonds_croissance_si_nouveau_mois(self):
        """
        Appelé au lancement du logiciel : verse 5% du
        bénéfice du mois précédent dans le Fonds de
        Croissance, une seule fois par mois.
        """

        mois_actuel = date.today().strftime("%Y-%m")

        commande_manager = CommandeManager()
        benefice = commande_manager.benefice_mois()

        self.manager.alimenter_fonds_croissance_mensuel(
            benefice, mois_actuel
        )