from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QInputDialog,
    QFrame,
    QSizePolicy,
)
from PySide6.QtGui import QColor, QFont

from modules.attribut_manager import AttributManager


class AttributsPage(QWidget):

    def __init__(self):

        super().__init__()

        self.manager = AttributManager()

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 16, 18, 16)
        principal.setSpacing(12)

        aide = QLabel(
            "Les critères servent à décliner un produit. Un "
            "t-shirt peut croiser Couleur et Taille, une "
            "casquette n'avoir que des tailles. L'ordre des "
            "valeurs est celui qui s'affichera sur ta boutique "
            "— range S avant M, pas dans l'ordre alphabétique."
        )
        aide.setWordWrap(True)
        aide.setStyleSheet("color:#64748b;")
        principal.addWidget(aide)

        colonnes = QHBoxLayout()
        colonnes.setSpacing(14)

        ####################################################
        # Colonne de gauche : les critères
        ####################################################

        carteCriteres = QFrame()
        carteCriteres.setObjectName("card")

        layoutCriteres = QVBoxLayout(carteCriteres)
        layoutCriteres.setContentsMargins(14, 12, 14, 12)
        layoutCriteres.setSpacing(10)

        titreCriteres = QLabel("Critères")
        police = QFont()
        police.setBold(True)
        police.setPointSize(11)
        titreCriteres.setFont(police)
        layoutCriteres.addWidget(titreCriteres)

        barreCriteres = QHBoxLayout()
        barreCriteres.setSpacing(8)

        self.btnNouveauCritere = QPushButton("➕ Nouveau")
        self.btnRenommerCritere = QPushButton("✏ Renommer")
        self.btnRenommerCritere.setObjectName("btnSecondaire")
        self.btnSupprimerCritere = QPushButton("🗑 Supprimer")
        self.btnSupprimerCritere.setObjectName("btnSupprimer")

        for bouton in (
            self.btnNouveauCritere,
            self.btnRenommerCritere,
            self.btnSupprimerCritere,
        ):
            bouton.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            barreCriteres.addWidget(bouton)

        barreCriteres.addStretch()
        layoutCriteres.addLayout(barreCriteres)

        self.tableCriteres = QTableWidget()
        self.tableCriteres.setColumnCount(3)
        self.tableCriteres.setHorizontalHeaderLabels([
            "ID", "Critère", "Valeurs"
        ])
        self.tableCriteres.setColumnHidden(0, True)
        self.tableCriteres.verticalHeader().setVisible(False)
        self.tableCriteres.setAlternatingRowColors(True)
        self.tableCriteres.setShowGrid(False)
        self.tableCriteres.verticalHeader().setDefaultSectionSize(38)
        self.tableCriteres.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tableCriteres.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        entete = self.tableCriteres.horizontalHeader()
        entete.setSectionResizeMode(1, QHeaderView.Stretch)
        entete.setSectionResizeMode(2, QHeaderView.Fixed)
        self.tableCriteres.setColumnWidth(2, 90)

        self.tableCriteres.itemSelectionChanged.connect(
            self.chargerValeurs
        )

        layoutCriteres.addWidget(self.tableCriteres)

        colonnes.addWidget(carteCriteres, 1)

        ####################################################
        # Colonne de droite : les valeurs
        ####################################################

        carteValeurs = QFrame()
        carteValeurs.setObjectName("card")

        layoutValeurs = QVBoxLayout(carteValeurs)
        layoutValeurs.setContentsMargins(14, 12, 14, 12)
        layoutValeurs.setSpacing(10)

        self.titreValeurs = QLabel("Valeurs")
        self.titreValeurs.setFont(police)
        layoutValeurs.addWidget(self.titreValeurs)

        barreValeurs = QHBoxLayout()
        barreValeurs.setSpacing(8)

        self.btnNouvelleValeur = QPushButton("➕ Nouvelle")
        self.btnRenommerValeur = QPushButton("✏ Renommer")
        self.btnRenommerValeur.setObjectName("btnSecondaire")
        self.btnSupprimerValeur = QPushButton("🗑 Supprimer")
        self.btnSupprimerValeur.setObjectName("btnSupprimer")
        self.btnMonter = QPushButton("▲ Monter")
        self.btnMonter.setObjectName("btnSecondaire")
        self.btnDescendre = QPushButton("▼ Descendre")
        self.btnDescendre.setObjectName("btnSecondaire")

        for bouton in (
            self.btnNouvelleValeur,
            self.btnRenommerValeur,
            self.btnSupprimerValeur,
            self.btnMonter,
            self.btnDescendre,
        ):
            bouton.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            barreValeurs.addWidget(bouton)

        barreValeurs.addStretch()
        layoutValeurs.addLayout(barreValeurs)

        self.tableValeurs = QTableWidget()
        self.tableValeurs.setColumnCount(4)
        self.tableValeurs.setHorizontalHeaderLabels([
            "ID", "Ordre", "Valeur", "Utilisée par"
        ])
        self.tableValeurs.setColumnHidden(0, True)
        self.tableValeurs.verticalHeader().setVisible(False)
        self.tableValeurs.setAlternatingRowColors(True)
        self.tableValeurs.setShowGrid(False)
        self.tableValeurs.verticalHeader().setDefaultSectionSize(38)
        self.tableValeurs.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tableValeurs.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        enteteValeurs = self.tableValeurs.horizontalHeader()
        enteteValeurs.setSectionResizeMode(1, QHeaderView.Fixed)
        enteteValeurs.setSectionResizeMode(2, QHeaderView.Stretch)
        enteteValeurs.setSectionResizeMode(3, QHeaderView.Fixed)
        self.tableValeurs.setColumnWidth(1, 70)
        self.tableValeurs.setColumnWidth(3, 130)

        layoutValeurs.addWidget(self.tableValeurs)

        colonnes.addWidget(carteValeurs, 2)

        principal.addLayout(colonnes)

        ####################################################
        # Connexions
        ####################################################

        self.btnNouveauCritere.clicked.connect(self.nouveauCritere)
        self.btnRenommerCritere.clicked.connect(self.renommerCritere)
        self.btnSupprimerCritere.clicked.connect(self.supprimerCritere)

        self.btnNouvelleValeur.clicked.connect(self.nouvelleValeur)
        self.btnRenommerValeur.clicked.connect(self.renommerValeur)
        self.btnSupprimerValeur.clicked.connect(self.supprimerValeur)
        self.btnMonter.clicked.connect(lambda: self.deplacer(-1))
        self.btnDescendre.clicked.connect(lambda: self.deplacer(1))

        self.charger()

    ########################################################
    # Chargement
    ########################################################

    def charger(self):

        selection = self.critereSelectionne(silencieux=True)

        self.tableCriteres.setRowCount(0)

        for critere in self.manager.attributs():

            ligne = self.tableCriteres.rowCount()
            self.tableCriteres.insertRow(ligne)

            self.tableCriteres.setItem(
                ligne, 0, QTableWidgetItem(str(critere["id"]))
            )

            itemNom = QTableWidgetItem(critere["nom"] or "")

            if not critere["actif"]:
                itemNom.setText(f"{critere['nom']} (désactivé)")
                itemNom.setForeground(QColor("#767676"))

            self.tableCriteres.setItem(ligne, 1, itemNom)

            itemNombre = QTableWidgetItem(
                str(critere["nombre_valeurs"])
            )
            self.tableCriteres.setItem(ligne, 2, itemNombre)

        if self.tableCriteres.rowCount() == 0:
            self.chargerValeurs()
            return

        # On retrouve la ligne qui était sélectionnée avant
        # le rechargement, plutôt que de repartir en haut.
        cible = 0

        if selection is not None:
            for ligne in range(self.tableCriteres.rowCount()):
                if int(self.tableCriteres.item(ligne, 0).text()) == selection:
                    cible = ligne
                    break

        self.tableCriteres.selectRow(cible)

    def chargerValeurs(self):

        self.tableValeurs.setRowCount(0)

        critere = self.critereSelectionne(silencieux=True)

        if critere is None:
            self.titreValeurs.setText("Valeurs")
            return

        nom = self.manager.obtenir_attribut(critere)

        self.titreValeurs.setText(
            f"Valeurs de « {nom['nom']} »" if nom else "Valeurs"
        )

        for valeur in self.manager.valeurs(critere):

            ligne = self.tableValeurs.rowCount()
            self.tableValeurs.insertRow(ligne)

            self.tableValeurs.setItem(
                ligne, 0, QTableWidgetItem(str(valeur["id"]))
            )
            self.tableValeurs.setItem(
                ligne, 1, QTableWidgetItem(str(valeur["ordre"] or ""))
            )

            itemValeur = QTableWidgetItem(valeur["valeur"] or "")

            if not valeur["actif"]:
                itemValeur.setText(f"{valeur['valeur']} (désactivée)")
                itemValeur.setForeground(QColor("#767676"))

            self.tableValeurs.setItem(ligne, 2, itemValeur)

            utilisations = self.manager.valeur_utilisee(valeur["id"])

            itemUsage = QTableWidgetItem(
                f"{utilisations} variation(s)" if utilisations else "—"
            )

            if utilisations:
                itemUsage.setForeground(QColor("#15803d"))

            self.tableValeurs.setItem(ligne, 3, itemUsage)

    ########################################################
    # Sélection
    ########################################################

    def critereSelectionne(self, silencieux=False):

        ligne = self.tableCriteres.currentRow()

        if ligne < 0 or self.tableCriteres.item(ligne, 0) is None:

            if not silencieux:
                QMessageBox.information(
                    self, "Aucun critère",
                    "Sélectionne d'abord un critère à gauche."
                )
            return None

        return int(self.tableCriteres.item(ligne, 0).text())

    def valeurSelectionnee(self, silencieux=False):

        ligne = self.tableValeurs.currentRow()

        if ligne < 0 or self.tableValeurs.item(ligne, 0) is None:

            if not silencieux:
                QMessageBox.information(
                    self, "Aucune valeur",
                    "Sélectionne d'abord une valeur à droite."
                )
            return None

        return int(self.tableValeurs.item(ligne, 0).text())

    ########################################################
    # Critères
    ########################################################

    def nouveauCritere(self):

        nom, valide = QInputDialog.getText(
            self, "Nouveau critère",
            "Nom du critère (Couleur, Taille, Pointure...) :"
        )

        if not valide or not nom.strip():
            return

        try:
            self.manager.ajouter_attribut(nom)
        except ValueError as erreur:
            QMessageBox.warning(self, "Critère refusé", str(erreur))
            return

        self.charger()

    def renommerCritere(self):

        critere = self.critereSelectionne()

        if critere is None:
            return

        actuel = self.manager.obtenir_attribut(critere)

        nom, valide = QInputDialog.getText(
            self, "Renommer le critère",
            "Nom du critère :", text=actuel["nom"] or ""
        )

        if not valide or not nom.strip():
            return

        try:
            self.manager.modifier_attribut(
                critere, nom, bool(actuel["actif"])
            )
        except ValueError as erreur:
            QMessageBox.warning(self, "Renommage refusé", str(erreur))
            return

        self.charger()

    def supprimerCritere(self):

        critere = self.critereSelectionne()

        if critere is None:
            return

        actuel = self.manager.obtenir_attribut(critere)

        reponse = QMessageBox.question(
            self, "Supprimer le critère",
            f"Supprimer « {actuel['nom']} » et toutes ses "
            f"valeurs ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        try:
            self.manager.supprimer_attribut(critere)
        except ValueError as erreur:
            QMessageBox.warning(
                self, "Suppression impossible", str(erreur)
            )
            return

        self.charger()

    ########################################################
    # Valeurs
    ########################################################

    def nouvelleValeur(self):

        critere = self.critereSelectionne()

        if critere is None:
            return

        actuel = self.manager.obtenir_attribut(critere)

        saisie, valide = QInputDialog.getText(
            self, f"Nouvelle valeur — {actuel['nom']}",
            "Valeur (une seule, ou plusieurs séparées par des "
            "virgules) :"
        )

        if not valide or not saisie.strip():
            return

        # On accepte « S, M, L, XL » d'un coup : saisir les
        # tailles une par une serait fastidieux.
        refusees = []

        for valeur in saisie.split(","):

            valeur = valeur.strip()

            if not valeur:
                continue

            try:
                self.manager.ajouter_valeur(critere, valeur)
            except ValueError:
                refusees.append(valeur)

        if refusees:
            QMessageBox.warning(
                self, "Valeurs refusées",
                "Ces valeurs n'ont pas été ajoutées :\n\n"
                + "\n".join(f"   • {v}" for v in refusees)
            )

        self.charger()

    def renommerValeur(self):

        valeur_id = self.valeurSelectionnee()

        if valeur_id is None:
            return

        ligne = self.tableValeurs.currentRow()
        actuel = self.tableValeurs.item(ligne, 2).text()
        actuel = actuel.replace(" (désactivée)", "")

        nom, valide = QInputDialog.getText(
            self, "Renommer la valeur", "Valeur :", text=actuel
        )

        if not valide or not nom.strip():
            return

        try:
            self.manager.modifier_valeur(valeur_id, nom)
        except ValueError as erreur:
            QMessageBox.warning(self, "Renommage refusé", str(erreur))
            return

        self.charger()

    def supprimerValeur(self):

        valeur_id = self.valeurSelectionnee()

        if valeur_id is None:
            return

        ligne = self.tableValeurs.currentRow()
        libelle = self.tableValeurs.item(ligne, 2).text()

        reponse = QMessageBox.question(
            self, "Supprimer la valeur",
            f"Supprimer « {libelle} » ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        try:
            self.manager.supprimer_valeur(valeur_id)
        except ValueError as erreur:
            QMessageBox.warning(
                self, "Suppression impossible", str(erreur)
            )
            return

        self.charger()

    def deplacer(self, sens):

        valeur_id = self.valeurSelectionnee()

        if valeur_id is None:
            return

        self.manager.deplacer_valeur(valeur_id, sens)

        self.chargerValeurs()

        # On garde la valeur déplacée sélectionnée, pour
        # pouvoir la monter plusieurs fois d'affilée.
        for ligne in range(self.tableValeurs.rowCount()):
            if int(self.tableValeurs.item(ligne, 0).text()) == valeur_id:
                self.tableValeurs.selectRow(ligne)
                break