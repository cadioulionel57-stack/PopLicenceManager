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
from ui import theme
from modules.commande_manager import CommandeManager
from ui.charge_dialog import ChargeDialog


class TresoreriePage(QWidget):
    """
    Écran Trésorerie : solde du jour, charges récurrentes
    (loyer, prêt, crédit TVA...) avec suivi de paiement
    mensuel, et les enveloppes (Croissance, Développement,
    Réserve, Renouvellement Stock).

    Le budget publicitaire a sa propre page dédiée
    ("📣 Budget Publicité"), pour laisser de la place ici à
    un vrai suivi des charges.
    """

    def __init__(self):

        super().__init__()

        self.manager = TresorerieManager()

        # Le style vient du thème global (ui/theme.py), plus
        # la couleur du module Trésorerie. Ne restent en local
        # que les deux styles de carte KPI, propres à cet
        # écran et à celui des Statistiques.
        self.accent = theme.accent_pour("trésorerie")

        self.setStyleSheet(
            theme.feuille_accent(self.accent)
            + """
            QLabel#kpiTitre{
                font-size:12px;
                color:#64748b;
            }
            QLabel#kpiValeur{
                font-size:24px;
                font-weight:bold;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        entete = QHBoxLayout()
        entete.setSpacing(12)

        # Même repère coloré que les autres écrans.
        bandeau = QFrame()
        bandeau.setObjectName("bandeauAccent")
        bandeau.setFixedWidth(6)
        bandeau.setMinimumHeight(34)

        titre = QLabel("🏦 Trésorerie")
        titre.setObjectName("titre")

        entete.addWidget(bandeau)
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
        self.carteReserve = carte("🛡 Réserve de Trésorerie", "#b35c10")
        self.carteRenouvellementStock = carte("📦 Renouvellement Stock", "#144b8b")

        ligneKpi2.addWidget(self.carteCroissance)
        ligneKpi2.addWidget(self.carteDeveloppement)
        ligneKpi2.addWidget(self.carteReserve)
        ligneKpi2.addWidget(self.carteRenouvellementStock)

        layout.addLayout(ligneKpi2)

        ligneTauxCroissance = QHBoxLayout()
        ligneTauxCroissance.addWidget(QLabel(
            "Taux de contribution au Fonds de Croissance, à "
            "chaque vente encaissée (ne s'applique qu'aux "
            "prochaines ventes, jamais aux anciennes) :"
        ))

        self.champTauxCroissance = QDoubleSpinBox()
        self.champTauxCroissance.setDecimals(1)
        self.champTauxCroissance.setMaximum(100)
        self.champTauxCroissance.setSuffix(" %")
        ligneTauxCroissance.addWidget(self.champTauxCroissance)

        self.btnTauxCroissance = QPushButton("💾 Appliquer le taux")
        self.btnTauxCroissance.clicked.connect(self.enregistrerTauxCroissance)
        ligneTauxCroissance.addWidget(self.btnTauxCroissance)

        ligneTauxCroissance.addStretch()

        layout.addLayout(ligneTauxCroissance)

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
        # Charges récurrentes — écran dédié, en pleine
        # largeur maintenant que le budget pub est ailleurs.
        ####################################################

        titreCharges = QLabel("🧾 Charges récurrentes")
        titreCharges.setObjectName("sousTitre")
        layout.addWidget(titreCharges)

        entêteCharges = QHBoxLayout()

        self.btnAjouterCharge = QPushButton("➕ Nouvelle charge")
        self.btnAjouterCharge.clicked.connect(self.ajouterCharge)
        entêteCharges.addWidget(self.btnAjouterCharge)

        self.btnModifierCharge = QPushButton("✏ Modifier")
        self.btnModifierCharge.clicked.connect(self.modifierCharge)
        entêteCharges.addWidget(self.btnModifierCharge)

        self.btnSupprimerCharge = QPushButton("🗑 Supprimer")
        self.btnSupprimerCharge.setObjectName("btnSupprimer")
        self.btnSupprimerCharge.clicked.connect(self.supprimerCharge)
        entêteCharges.addWidget(self.btnSupprimerCharge)

        entêteCharges.addStretch()

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
        self.table.setMinimumHeight(320)

        layout.addWidget(self.table)

        self.charger()

    def charger(self):

        solde_saisi = self.manager.solde_actuel()

        if solde_saisi is not None:
            self.champSolde.setValue(solde_saisi)

        solde_effectif = self.manager.solde_effectif()

        self.carteSoldeActuel.labelValeur.setText(
            f"{solde_effectif:.2f} €"
            if solde_effectif is not None else "Non renseigné"
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
        self.champTauxCroissance.setValue(
            self.manager.taux_contribution_croissance()
        )

        self._chargerTableCharges(mois_actuel)

    def enregistrerTauxCroissance(self):

        self.manager.definir_taux_contribution_croissance(
            self.champTauxCroissance.value()
        )

        QMessageBox.information(
            self, "Enregistré",
            "Le nouveau taux s'appliquera aux prochaines ventes "
            "cochées payées — les contributions déjà figées ne "
            "changent pas."
        )

    def enregistrerAjustementStock(self):

        self.manager.definir_ajustement_manuel_stock(
            self.champAjustementStock.value()
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