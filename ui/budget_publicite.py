from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QComboBox,
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

from modules.budget_publicitaire_manager import BudgetPublicitaireManager
from ui.budget_pub_ligne_dialog import BudgetPubLigneDialog
from ui.periode_commerciale_dialog import PeriodeCommercialeDialog
from ui.widgets.reference_combobox import ReferenceComboBox
from ui.graphique_ca_vs_pub import GraphiqueCaVsPubWidget


class BudgetPublicitePage(QWidget):
    """
    Suivi complet du budget publicitaire : enveloppes par
    canal, alertes de dépassement, détail mensuel, CA et
    ROAS par canal lié, et périodes commerciales (Noël,
    Rentrée...) avec leur propre retour sur investissement.
    """

    COULEURS_ALERTE = {
        "normal": None,
        "attention": "#e67e22",
        "depasse": "#c0392b",
    }

    def __init__(self):

        super().__init__()

        self.manager = BudgetPublicitaireManager()

        self.setStyleSheet("""
        QWidget{ background:#f4f7fb; font-family:'Segoe UI'; }
        QLabel#titre{ font-size:24px; font-weight:600; color:#0f2f5c; }
        QLabel#sousTitre{ font-size:15px; font-weight:600; color:#0f2f5c; }
        QFrame#card{
            background:white; border:1px solid #e1e8f0;
            border-radius:12px;
        }
        QLabel#kpiTitre{ font-size:12px; color:#888; }
        QLabel#kpiValeur{ font-size:24px; font-weight:bold; }
        QPushButton{
            background:#144b8b; color:white; border:none;
            border-radius:8px; padding:9px 16px; font-weight:500;
        }
        QPushButton:hover{ background:#1d61b4; }
        QPushButton#btnSupprimer{ background:#c0392b; }
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
        titre = QLabel("📣 Budget Publicité")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        ####################################################
        # KPI global
        ####################################################

        def carte(titre_kpi, couleur="#144b8b"):

            cadre = QFrame()
            cadre.setObjectName("card")
            cadre.setMinimumHeight(90)
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

        ligneKpi = QHBoxLayout()
        self.carteRestantGlobal = carte(
            "💰 Restant global (toutes lignes)", "#1e7d32"
        )
        ligneKpi.addWidget(self.carteRestantGlobal)
        layout.addLayout(ligneKpi)

        ####################################################
        # Lignes de budget
        ####################################################

        entêteLignes = QHBoxLayout()
        titreLignes = QLabel("Enveloppes publicitaires")
        titreLignes.setObjectName("sousTitre")
        entêteLignes.addWidget(titreLignes)
        entêteLignes.addStretch()

        self.btnAjouterLigne = QPushButton("➕ Nouvelle enveloppe")
        self.btnAjouterLigne.clicked.connect(self.ajouterLigne)
        entêteLignes.addWidget(self.btnAjouterLigne)

        self.btnModifierLigne = QPushButton("✏ Modifier")
        self.btnModifierLigne.clicked.connect(self.modifierLigne)
        entêteLignes.addWidget(self.btnModifierLigne)

        self.btnSupprimerLigne = QPushButton("🗑 Supprimer")
        self.btnSupprimerLigne.setObjectName("btnSupprimer")
        self.btnSupprimerLigne.clicked.connect(self.supprimerLigne)
        entêteLignes.addWidget(self.btnSupprimerLigne)

        layout.addLayout(entêteLignes)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Enveloppe HT", "Dépensé", "Restant",
            "% consommé", "CA des canaux liés", "ROAS canaux", "Alerte"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._chargerCanauxLies)
        layout.addWidget(self.table)

        ####################################################
        # Canaux liés à la ligne sélectionnée
        ####################################################

        entêteCanaux = QHBoxLayout()
        self.labelCanaux = QLabel(
            "Canaux liés — sélectionne une enveloppe ci-dessus"
        )
        entêteCanaux.addWidget(self.labelCanaux)
        entêteCanaux.addStretch()

        self.comboNouveauCanal = ReferenceComboBox("canaux_vente")
        entêteCanaux.addWidget(self.comboNouveauCanal)

        self.btnLierCanal = QPushButton("🔗 Lier ce canal")
        self.btnLierCanal.clicked.connect(self.lierCanal)
        entêteCanaux.addWidget(self.btnLierCanal)

        layout.addLayout(entêteCanaux)

        self.tableCanaux = QTableWidget()
        self.tableCanaux.setColumnCount(4)
        self.tableCanaux.setHorizontalHeaderLabels([
            "ID lien", "Canal", "Actif", ""
        ])
        self.tableCanaux.setColumnHidden(0, True)
        self.tableCanaux.setMaximumHeight(150)
        self.tableCanaux.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableCanaux.verticalHeader().setVisible(False)
        layout.addWidget(self.tableCanaux)

        ####################################################
        # Détail mensuel de la ligne sélectionnée
        ####################################################

        entêteDetail = QHBoxLayout()
        self.labelDetail = QLabel(
            "Détail mensuel — sélectionne une enveloppe ci-dessus"
        )
        entêteDetail.addWidget(self.labelDetail)
        entêteDetail.addStretch()

        self.btnAjouterMois = QPushButton("➕ Ajouter un mois")
        self.btnAjouterMois.clicked.connect(self.ajouterMoisDetail)
        entêteDetail.addWidget(self.btnAjouterMois)

        layout.addLayout(entêteDetail)

        self.tableDetail = QTableWidget()
        self.tableDetail.setColumnCount(2)
        self.tableDetail.setHorizontalHeaderLabels([
            "Mois (AAAA-MM)", "Montant dépensé HT"
        ])
        self.tableDetail.setMaximumHeight(150)
        self.tableDetail.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tableDetail.verticalHeader().setVisible(False)
        self.tableDetail.itemChanged.connect(self.enregistrerDetailMensuel)
        layout.addWidget(self.tableDetail)

        ####################################################
        # Graphique CA vs pub
        ####################################################

        titreGraphique = QLabel("📊 Évolution CA vs budget publicitaire")
        titreGraphique.setObjectName("sousTitre")
        layout.addWidget(titreGraphique)

        self.graphique = GraphiqueCaVsPubWidget()
        layout.addWidget(self.graphique)

        ####################################################
        # Périodes commerciales
        ####################################################

        entêtePeriodes = QHBoxLayout()
        titrePeriodes = QLabel("🎄 Périodes commerciales")
        titrePeriodes.setObjectName("sousTitre")
        entêtePeriodes.addWidget(titrePeriodes)
        entêtePeriodes.addStretch()

        self.btnAjouterPeriode = QPushButton("➕ Nouvelle période")
        self.btnAjouterPeriode.clicked.connect(self.ajouterPeriode)
        entêtePeriodes.addWidget(self.btnAjouterPeriode)

        self.btnModifierPeriode = QPushButton("✏ Modifier")
        self.btnModifierPeriode.clicked.connect(self.modifierPeriode)
        entêtePeriodes.addWidget(self.btnModifierPeriode)

        self.btnSupprimerPeriode = QPushButton("🗑 Supprimer")
        self.btnSupprimerPeriode.setObjectName("btnSupprimer")
        self.btnSupprimerPeriode.clicked.connect(self.supprimerPeriode)
        entêtePeriodes.addWidget(self.btnSupprimerPeriode)

        layout.addLayout(entêtePeriodes)

        self.tablePeriodes = QTableWidget()
        self.tablePeriodes.setColumnCount(6)
        self.tablePeriodes.setHorizontalHeaderLabels([
            "ID", "Nom", "Dates", "Dépense pub (+ supplément)",
            "CA généré", "ROAS"
        ])
        self.tablePeriodes.setColumnHidden(0, True)
        self.tablePeriodes.setAlternatingRowColors(True)
        self.tablePeriodes.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tablePeriodes.verticalHeader().setVisible(False)
        layout.addWidget(self.tablePeriodes)

        self._ligne_selectionnee = None

        self.charger()

    ########################################################
    # Chargement général
    ########################################################

    def charger(self):

        self.carteRestantGlobal.labelValeur.setText(
            f"{self.manager.total_restant_global():.2f} €"
        )

        self._chargerTableLignes()
        self._chargerTablePeriodes()
        self.graphique.rafraichir()

    def _chargerTableLignes(self):

        self.table.setRowCount(0)

        for ligne, item in enumerate(self.manager.synthese()):

            self.table.insertRow(ligne)

            l = item["ligne"]

            roas_texte = (
                f"{item['roas_canaux']:.2f}"
                if item["roas_canaux"] is not None else "—"
            )

            alerte_texte = {
                "normal": "✅ OK",
                "attention": "⚠ Approche de la limite",
                "depasse": "❌ Dépassé",
            }[item["niveau_alerte"]]

            valeurs = [
                str(l["id"]),
                l["nom"] or "",
                f"{l['enveloppe_totale_ht'] or 0:.2f} €",
                f"{item['depense_ht']:.2f} €",
                f"{item['restant_ht']:.2f} €",
                f"{item['pourcentage_consomme']:.0f} %",
                f"{item['ca_canaux_ht']:.2f} €",
                roas_texte,
                alerte_texte,
            ]

            couleur = self.COULEURS_ALERTE[item["niveau_alerte"]]

            for colonne, valeur in enumerate(valeurs):

                cellule = QTableWidgetItem(valeur)

                if couleur and colonne in (5, 8):

                    cellule.setForeground(QColor(couleur))
                    police = QFont()
                    police.setBold(True)
                    cellule.setFont(police)

                self.table.setItem(ligne, colonne, cellule)

    ########################################################
    # Lignes de budget
    ########################################################

    def ajouterLigne(self):

        dialog = BudgetPubLigneDialog("Nouvelle enveloppe publicitaire")

        if dialog.exec() != BudgetPubLigneDialog.DialogCode.Accepted:
            return

        self.manager.ajouter_ligne(
            dialog.nom.text().strip(),
            dialog.enveloppeTotale.value(),
            dialog.dateDebut.text().strip(),
            dialog.dateFin.text().strip() or None,
        )

        self.charger()

    def modifierLigne(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une ligne.")
            return

        identifiant = int(self.table.item(ligne, 0).text())
        ligne_data = self.manager.obtenir_ligne(identifiant)

        dialog = BudgetPubLigneDialog(
            "Modifier l'enveloppe",
            ligne_data["nom"], ligne_data["enveloppe_totale_ht"],
            ligne_data["date_debut"], ligne_data["date_fin"],
        )

        if dialog.exec() != BudgetPubLigneDialog.DialogCode.Accepted:
            return

        self.manager.modifier_ligne(
            identifiant,
            dialog.nom.text().strip(),
            dialog.enveloppeTotale.value(),
            dialog.dateDebut.text().strip(),
            dialog.dateFin.text().strip() or None,
        )

        self.charger()

    def supprimerLigne(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une ligne.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Supprimer cette enveloppe publicitaire ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())
        self.manager.supprimer_ligne(identifiant)

        self.charger()

    ########################################################
    # Canaux liés
    ########################################################

    def _chargerCanauxLies(self):

        ligne = self.table.currentRow()

        self.tableCanaux.setRowCount(0)
        self.tableDetail.blockSignals(True)
        self.tableDetail.setRowCount(0)
        self.tableDetail.blockSignals(False)

        if ligne == -1:
            self.labelCanaux.setText(
                "Canaux liés — sélectionne une enveloppe ci-dessus"
            )
            self.labelDetail.setText(
                "Détail mensuel — sélectionne une enveloppe ci-dessus"
            )
            self._ligne_selectionnee = None
            return

        identifiant = int(self.table.item(ligne, 0).text())
        ligne_data = self.manager.obtenir_ligne(identifiant)

        self._ligne_selectionnee = identifiant
        self.labelCanaux.setText(f"Canaux liés — {ligne_data['nom']}")
        self.labelDetail.setText(f"Détail mensuel — {ligne_data['nom']}")

        for r, canal in enumerate(self.manager.canaux_lies(identifiant)):

            self.tableCanaux.insertRow(r)

            self.tableCanaux.setItem(
                r, 0, QTableWidgetItem(str(canal["lien_id"]))
            )
            self.tableCanaux.setItem(
                r, 1, QTableWidgetItem(canal["nom_canal"])
            )

            statut = QTableWidgetItem(
                "✅ Actif" if canal["actif"] else "⏸ Inactif"
            )
            self.tableCanaux.setItem(r, 2, statut)

            btnBascule = QPushButton(
                "Désactiver" if canal["actif"] else "Activer"
            )
            btnBascule.clicked.connect(
                lambda _, lid=canal["lien_id"], actif=canal["actif"]:
                    self._basculerCanal(lid, not actif)
            )
            self.tableCanaux.setCellWidget(r, 3, btnBascule)

        depenses = self.manager.depenses_ligne(identifiant)

        self.tableDetail.blockSignals(True)

        for r, depense in enumerate(depenses):

            self.tableDetail.insertRow(r)

            self.tableDetail.setItem(
                r, 0, QTableWidgetItem(depense["mois"] or "")
            )
            self.tableDetail.setItem(
                r, 1, QTableWidgetItem(f"{depense['montant_reel_ht']:.2f}")
            )

        self.tableDetail.blockSignals(False)

    def _basculerCanal(self, lien_id, actif):

        self.manager.basculer_actif_canal(lien_id, actif)

        ligne_sauvegardee = self._ligne_selectionnee
        self.charger()

        for r in range(self.table.rowCount()):
            if int(self.table.item(r, 0).text()) == ligne_sauvegardee:
                self.table.selectRow(r)
                break

    def lierCanal(self):

        if self._ligne_selectionnee is None:
            QMessageBox.information(
                self, "Information",
                "Sélectionne d'abord une enveloppe de budget."
            )
            return

        canal_id = self.comboNouveauCanal.id()

        if canal_id is None:
            QMessageBox.information(
                self, "Information", "Choisis un canal à lier."
            )
            return

        self.manager.ajouter_canal_ligne(self._ligne_selectionnee, canal_id)

        ligne_sauvegardee = self._ligne_selectionnee
        self.charger()

        for r in range(self.table.rowCount()):
            if int(self.table.item(r, 0).text()) == ligne_sauvegardee:
                self.table.selectRow(r)
                break

    ########################################################
    # Détail mensuel
    ########################################################

    def ajouterMoisDetail(self):

        if self._ligne_selectionnee is None:
            QMessageBox.information(
                self, "Information",
                "Sélectionne d'abord une enveloppe en haut."
            )
            return

        ligne = self.tableDetail.rowCount()

        self.tableDetail.blockSignals(True)
        self.tableDetail.insertRow(ligne)
        self.tableDetail.setItem(ligne, 0, QTableWidgetItem(""))
        self.tableDetail.setItem(ligne, 1, QTableWidgetItem("0.00"))
        self.tableDetail.blockSignals(False)

        self.tableDetail.editItem(self.tableDetail.item(ligne, 0))

    def enregistrerDetailMensuel(self, item):

        if self._ligne_selectionnee is None:
            return

        ligne = item.row()

        item_mois = self.tableDetail.item(ligne, 0)
        item_montant = self.tableDetail.item(ligne, 1)

        if item_mois is None or item_montant is None:
            return

        mois = item_mois.text().strip()

        try:
            montant = float(item_montant.text().replace(",", "."))
        except ValueError:
            return

        if not mois:
            return

        self.manager.definir_depense_mois(
            self._ligne_selectionnee, mois, montant
        )

        ligne_sauvegardee = self._ligne_selectionnee

        self.table.blockSignals(True)
        self._chargerTableLignes()
        self.carteRestantGlobal.labelValeur.setText(
            f"{self.manager.total_restant_global():.2f} €"
        )
        self.graphique.rafraichir()

        for r in range(self.table.rowCount()):
            if int(self.table.item(r, 0).text()) == ligne_sauvegardee:
                self.table.selectRow(r)
                break

        self.table.blockSignals(False)

    ########################################################
    # Périodes commerciales
    ########################################################

    def _chargerTablePeriodes(self):

        self.tablePeriodes.setRowCount(0)

        for ligne, item in enumerate(self.manager.synthese_periodes()):

            self.tablePeriodes.insertRow(ligne)

            p = item["periode"]

            roas_texte = (
                f"{item['roas']:.2f}" if item["roas"] is not None else "—"
            )

            dates_texte = f"{p['date_debut']} → {p['date_fin']}"

            valeurs = [
                str(p["id"]),
                p["nom"] or "",
                dates_texte,
                f"{item['depense_pub_ht']:.2f} €",
                f"{item['ca_ht']:.2f} €",
                roas_texte,
            ]

            for colonne, valeur in enumerate(valeurs):
                self.tablePeriodes.setItem(
                    ligne, colonne, QTableWidgetItem(valeur)
                )

    def ajouterPeriode(self):

        dialog = PeriodeCommercialeDialog("Nouvelle période commerciale")

        if dialog.exec() != PeriodeCommercialeDialog.DialogCode.Accepted:
            return

        self.manager.ajouter_periode(
            dialog.nom.text().strip(),
            dialog.dateDebut.text().strip(),
            dialog.dateFin.text().strip(),
            dialog.budgetSupplementaire.value(),
        )

        self.charger()

    def modifierPeriode(self):

        ligne = self.tablePeriodes.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une période.")
            return

        identifiant = int(self.tablePeriodes.item(ligne, 0).text())
        periode = self.manager.obtenir_periode(identifiant)

        dialog = PeriodeCommercialeDialog(
            "Modifier la période",
            periode["nom"], periode["date_debut"], periode["date_fin"],
            periode["budget_supplementaire_ht"],
        )

        if dialog.exec() != PeriodeCommercialeDialog.DialogCode.Accepted:
            return

        self.manager.modifier_periode(
            identifiant,
            dialog.nom.text().strip(),
            dialog.dateDebut.text().strip(),
            dialog.dateFin.text().strip(),
            dialog.budgetSupplementaire.value(),
        )

        self.charger()

    def supprimerPeriode(self):

        ligne = self.tablePeriodes.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez une période.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Supprimer cette période commerciale ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.tablePeriodes.item(ligne, 0).text())
        self.manager.supprimer_periode(identifiant)

        self.charger()