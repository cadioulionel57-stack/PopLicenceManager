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

        ligneKpi2.addWidget(self.carteCroissance)
        ligneKpi2.addWidget(self.carteDeveloppement)
        ligneKpi2.addWidget(self.carteReserve)

        layout.addLayout(ligneKpi2)

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

        self.btnSaisirDepense = QPushButton("💸 Saisir une dépense")
        self.btnSaisirDepense.clicked.connect(self.saisirDepensePub)
        entêtePub.addWidget(self.btnSaisirDepense)

        self.btnModifierLignePub = QPushButton("✏ Modifier")
        self.btnModifierLignePub.clicked.connect(self.modifierLignePub)
        entêtePub.addWidget(self.btnModifierLignePub)

        self.btnSupprimerLignePub = QPushButton("🗑 Supprimer")
        self.btnSupprimerLignePub.setStyleSheet("background:#c0392b;")
        self.btnSupprimerLignePub.clicked.connect(self.supprimerLignePub)
        entêtePub.addWidget(self.btnSupprimerLignePub)

        layout.addLayout(entêtePub)

        self.tableBudgetPub = QTableWidget()
        self.tableBudgetPub.setColumnCount(6)
        self.tableBudgetPub.setHorizontalHeaderLabels([
            "ID", "Nom", "Enveloppe totale", "Dépensé à ce jour",
            "Restant", "% consommé"
        ])
        self.tableBudgetPub.setColumnHidden(0, True)
        self.tableBudgetPub.setAlternatingRowColors(True)
        self.tableBudgetPub.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableBudgetPub.verticalHeader().setVisible(False)

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

        self._chargerTableCharges(mois_actuel)
        self._chargerTableBudgetPub()

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

    def saisirDepensePub(self):

        ligne = self.tableBudgetPub.currentRow()

        if ligne == -1:
            QMessageBox.information(
                self, "Information",
                "Sélectionnez d'abord une ligne de budget."
            )
            return

        identifiant = int(self.tableBudgetPub.item(ligne, 0).text())
        ligne_data = self.managerBudgetPub.obtenir_ligne(identifiant)

        dialog = BudgetPubDepenseDialog(
            "Saisir une dépense", ligne_data["nom"]
        )

        if dialog.exec() != BudgetPubDepenseDialog.DialogCode.Accepted:
            return

        self.managerBudgetPub.definir_depense_mois(
            identifiant,
            dialog.mois.text().strip(),
            dialog.montant.value(),
        )

        self.charger()

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