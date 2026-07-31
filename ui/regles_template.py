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
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QFrame,
    QSizePolicy,
    QDateEdit,
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QColor, QFont

from modules.regle_template_manager import (
    RegleTemplateManager,
    normaliser_date,
    LIBELLES_TYPES,
)


def date_fr(valeur):

    if not valeur:
        return ""

    morceaux = str(valeur)[:10].split("-")

    if len(morceaux) != 3:
        return str(valeur)

    return f"{morceaux[2]}/{morceaux[1]}/{morceaux[0]}"


class PeriodeDialog(QDialog):
    """
    Création d'une période commerciale, avec de vrais
    calendriers.

    L'ancien écran laissait taper la date à la main dans un
    champ libre : une date écrite « 01/12/2026 » passait
    sans broncher puis ne servait à rien. Ici le choix se
    fait dans un calendrier, il n'y a plus de format à
    respecter.
    """

    def __init__(self, titre, periode=None, parent=None):

        super().__init__(parent)

        self.setWindowTitle(titre)
        self.setMinimumWidth(460)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 18, 18, 18)
        principal.setSpacing(14)

        entete = QLabel(titre)
        police = QFont()
        police.setPointSize(13)
        police.setBold(True)
        entete.setFont(police)
        principal.addWidget(entete)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Noël, Soldes d'hiver, Halloween...")
        formulaire.addRow("Nom de la période", self.nom)

        self.dateDebut = QDateEdit()
        self.dateDebut.setCalendarPopup(True)
        self.dateDebut.setDisplayFormat("dd/MM/yyyy")
        self.dateDebut.setDate(QDate.currentDate())
        formulaire.addRow("Du", self.dateDebut)

        self.dateFin = QDateEdit()
        self.dateFin.setCalendarPopup(True)
        self.dateFin.setDisplayFormat("dd/MM/yyyy")
        self.dateFin.setDate(QDate.currentDate().addDays(30))
        formulaire.addRow("Au", self.dateFin)

        principal.addLayout(formulaire)

        aide = QLabel(
            "Cette période servira aussi dans l'écran Budget "
            "Publicité, où tu peux lui affecter un budget "
            "supplémentaire."
        )
        aide.setWordWrap(True)
        aide.setStyleSheet("color:#64748b; font-size:12px;")
        principal.addWidget(aide)

        boutons = QHBoxLayout()
        boutons.addStretch()

        annuler = QPushButton("Annuler")
        annuler.setObjectName("btnSecondaire")
        annuler.clicked.connect(self.reject)
        boutons.addWidget(annuler)

        valider = QPushButton("Enregistrer")
        valider.clicked.connect(self._valider)
        boutons.addWidget(valider)

        principal.addLayout(boutons)

        if periode is not None:

            self.nom.setText(periode["nom"] or "")

            debut = normaliser_date(periode["date_debut"])
            fin = normaliser_date(periode["date_fin"])

            if debut:
                self.dateDebut.setDate(
                    QDate.fromString(debut, "yyyy-MM-dd")
                )
            if fin:
                self.dateFin.setDate(
                    QDate.fromString(fin, "yyyy-MM-dd")
                )

    def _valider(self):

        if not self.nom.text().strip():

            QMessageBox.warning(
                self, "Nom manquant",
                "Donne un nom à cette période — « Noël », "
                "« Soldes d'hiver »..."
            )
            return

        if self.dateFin.date() < self.dateDebut.date():

            QMessageBox.warning(
                self, "Dates inversées",
                "La date de fin est avant la date de début."
            )
            return

        self.accept()

    def valeurs(self):

        return {
            "nom": self.nom.text().strip(),
            "date_debut": self.dateDebut.date().toString("yyyy-MM-dd"),
            "date_fin": self.dateFin.date().toString("yyyy-MM-dd"),
        }


class RegleDialog(QDialog):
    """
    Saisie d'une règle. Tout est choisi dans des listes :
    rien à taper sauf le nom.
    """

    def __init__(self, titre, manager, regle=None, parent=None):

        super().__init__(parent)

        self.manager = manager
        self.regle = regle

        self.setWindowTitle(titre)
        self.setMinimumWidth(600)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 18, 18, 18)
        principal.setSpacing(14)

        entete = QLabel(titre)
        police = QFont()
        police.setPointSize(13)
        police.setBold(True)
        entete.setFont(police)
        principal.addWidget(entete)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Noël sur le textile")
        formulaire.addRow("Nom de la règle", self.nom)

        self.periode = QComboBox()

        for periode in self.manager.db.lire(
            """
            SELECT id, nom, date_debut, date_fin
            FROM periodes_commerciales
            WHERE actif = 1
            ORDER BY date_debut
            """
        ):
            self.periode.addItem(
                f"{periode['nom']} "
                f"({date_fr(normaliser_date(periode['date_debut']))} → "
                f"{date_fr(normaliser_date(periode['date_fin']))})",
                periode["id"]
            )

        # Une liste vide a l'air d'un bug alors qu'il ne
        # manque qu'une donnée : on le dit franchement.
        if self.periode.count() == 0:
            self.periode.addItem(
                "— aucune période : clique sur ➕ —", None
            )

        lignePeriode = QHBoxLayout()
        lignePeriode.setSpacing(8)
        lignePeriode.addWidget(self.periode)

        self.btnNouvellePeriode = QPushButton("➕ Nouvelle")
        self.btnNouvellePeriode.setObjectName("btnSecondaire")
        self.btnNouvellePeriode.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.btnNouvellePeriode.setToolTip(
            "Créer une période sans quitter cette fenêtre"
        )
        self.btnNouvellePeriode.clicked.connect(self._creerPeriode)
        lignePeriode.addWidget(self.btnNouvellePeriode)

        formulaire.addRow("Période", lignePeriode)

        self.modele = QComboBox()

        for modele in self.manager.db.lire(
            """
            SELECT m.id, m.nom, t.nom AS theme
            FROM modeles_fiche_produit m
            LEFT JOIN themes_template t ON t.id = m.theme_id
            WHERE m.actif = 1
            ORDER BY m.nom
            """
        ):
            self.modele.addItem(
                f"{modele['theme'] or '—'} — {modele['nom']}",
                modele["id"]
            )

        if self.modele.count() == 0:
            self.modele.addItem("— aucun modèle actif —", None)
            self.modele.setEnabled(False)

        self.modele.currentIndexChanged.connect(self._majPortee)

        formulaire.addRow("Modèle à appliquer", self.modele)

        # Ce que couvre le modèle choisi, en clair. On ne le
        # redemande pas : c'est écrit dans sa définition.
        self.portee = QLabel()
        self.portee.setWordWrap(True)
        self.portee.setStyleSheet(
            "background:#eef4fb; border:1px solid #cfe0f2;"
            "border-radius:8px; padding:10px; color:#0f2f5c;"
        )
        formulaire.addRow("", self.portee)

        self.categorie = QComboBox()
        self.categorie.addItem("Toutes les catégories", None)

        for categorie in self.manager.db.lire(
            """
            SELECT id, nom FROM categories_site
            WHERE actif = 1 ORDER BY nom
            """
        ):
            self.categorie.addItem(categorie["nom"], categorie["id"])

        formulaire.addRow("Restreindre à une catégorie", self.categorie)

        self._majPortee()

        self.priorite = QSpinBox()
        self.priorite.setMaximum(999)
        formulaire.addRow("Priorité", self.priorite)

        principal.addLayout(formulaire)

        aide = QLabel(
            "Laisse la catégorie sur « Toutes » si le modèle "
            "doit couvrir tout ton catalogue : son type suffit "
            "déjà à écarter les produits qui ne le concernent "
            "pas.\n\n"
            "La priorité ne sert qu'en cas de chevauchement — "
            "zéro convient dans la plupart des cas."
        )
        aide.setWordWrap(True)
        aide.setStyleSheet("color:#64748b; font-size:12px;")
        principal.addWidget(aide)

        boutons = QHBoxLayout()
        boutons.addStretch()

        annuler = QPushButton("Annuler")
        annuler.setObjectName("btnSecondaire")
        annuler.clicked.connect(self.reject)
        boutons.addWidget(annuler)

        valider = QPushButton("Enregistrer")
        valider.clicked.connect(self._valider)
        boutons.addWidget(valider)

        principal.addLayout(boutons)

        if regle is not None:
            self._charger()

    def _majPortee(self):
        """
        Dit en clair sur quoi le modèle choisi va s'appliquer.

        Le type de produit n'est jamais demandé : il est écrit
        dans la définition du modèle. Un « Template STOCK
        Vêtements » ne touchera jamais un produit Direct
        Fournisseur, même si la règle vise toute la catégorie.
        """

        modele_id = self.modele.currentData()

        if not modele_id:
            self.portee.setText(
                "Choisis un modèle pour voir ce qu'il couvre."
            )
            return

        types = self.manager.types_du_modele(modele_id)

        if not types:

            self.portee.setText(
                "⚠ Ce modèle n'est rattaché à aucun type de "
                "produit : il s'appliquera à tous. Si ce n'est "
                "pas voulu, coche les types dans l'onglet "
                "« 📄 Modèles de fiche »."
            )
            return

        libelles = " ou ".join(
            LIBELLES_TYPES.get(t, t) for t in types
        )

        self.portee.setText(
            f"Ce modèle ne s'applique qu'aux produits "
            f"{libelles}. Les autres garderont le modèle de "
            f"leur fiche, même s'ils sont dans la catégorie "
            f"choisie ci-dessous."
        )

    def _rechargerPeriodes(self, selectionner=None):

        self.periode.clear()

        for periode in self.manager.db.lire(
            """
            SELECT id, nom, date_debut, date_fin
            FROM periodes_commerciales
            WHERE actif = 1
            ORDER BY date_debut
            """
        ):
            self.periode.addItem(
                f"{periode['nom']} "
                f"({date_fr(normaliser_date(periode['date_debut']))} → "
                f"{date_fr(normaliser_date(periode['date_fin']))})",
                periode["id"]
            )

        if self.periode.count() == 0:
            self.periode.addItem("— aucune période : clique sur ➕ —", None)
            return

        if selectionner is not None:

            index = self.periode.findData(selectionner)

            if index >= 0:
                self.periode.setCurrentIndex(index)

    def _creerPeriode(self):
        """
        Crée une période sans quitter la fenêtre : on ne
        renvoie pas l'utilisateur dans un autre écran au
        milieu d'une saisie.
        """

        dialog = PeriodeDialog("Nouvelle période", parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        saisie = dialog.valeurs()

        curseur = self.manager.db.executer(
            """
            INSERT INTO periodes_commerciales
                (nom, date_debut, date_fin,
                 budget_supplementaire_ht, actif)
            VALUES (?, ?, ?, 0, 1)
            """,
            (saisie["nom"], saisie["date_debut"], saisie["date_fin"])
        )

        self._rechargerPeriodes(selectionner=curseur.lastrowid)

    def _charger(self):

        self.nom.setText(self.regle["nom"] or "")

        index = self.periode.findData(self.regle["periode_id"])
        if index >= 0:
            self.periode.setCurrentIndex(index)

        index = self.modele.findData(self.regle["modele_fiche_id"])
        if index >= 0:
            self.modele.setCurrentIndex(index)

        self._majPortee()

        index = self.categorie.findData(self.regle["categorie_site_id"])
        if index >= 0:
            self.categorie.setCurrentIndex(index)

        self.priorite.setValue(self.regle["priorite"] or 0)

    def _valider(self):

        if self.periode.currentData() is None:

            QMessageBox.warning(
                self,
                "Aucune période",
                "Clique sur ➕ Nouvelle à côté de la liste pour "
                "créer ta période — Noël, les soldes, etc."
            )
            return

        if self.modele.currentData() is None:

            QMessageBox.warning(
                self,
                "Aucun modèle",
                "Crée d'abord un modèle de fiche dans l'onglet "
                "« 📄 Modèles de fiche »."
            )
            return

        self.accept()

    def valeurs(self):

        return {
            "nom": self.nom.text().strip(),
            "periode_id": self.periode.currentData(),
            "modele_fiche_id": self.modele.currentData(),
            "categorie_site_id": self.categorie.currentData(),
            "priorite": self.priorite.value(),
        }


class ReglesTemplatePage(QWidget):

    def __init__(self):

        super().__init__()

        self.manager = RegleTemplateManager()

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 16, 18, 16)
        principal.setSpacing(12)

        aide = QLabel(
            "Une règle applique un modèle de fiche à une "
            "période donnée. Le type de produit vient du "
            "modèle lui-même : un modèle Stock ne touchera "
            "jamais un produit Direct Fournisseur. En dehors "
            "de la période, chaque produit reprend le modèle "
            "choisi dans sa fiche."
        )
        aide.setWordWrap(True)
        aide.setStyleSheet("color:#64748b;")
        principal.addWidget(aide)

        ####################################################
        # Ce qui s'applique aujourd'hui
        ####################################################

        self.carteJour = QFrame()
        self.carteJour.setObjectName("card")

        layoutJour = QVBoxLayout(self.carteJour)
        layoutJour.setContentsMargins(14, 12, 14, 12)
        layoutJour.setSpacing(6)

        titreJour = QLabel("📅 En vigueur aujourd'hui")
        police = QFont()
        police.setBold(True)
        titreJour.setFont(police)
        layoutJour.addWidget(titreJour)

        self.detailJour = QLabel()
        self.detailJour.setWordWrap(True)
        layoutJour.addWidget(self.detailJour)

        principal.addWidget(self.carteJour)

        ####################################################
        # Barre d'outils
        ####################################################

        barre = QHBoxLayout()
        barre.setSpacing(8)

        self.btnNouvelle = QPushButton("➕ Nouvelle règle")
        self.btnModifier = QPushButton("✏ Modifier")
        self.btnModifier.setObjectName("btnSecondaire")
        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnSupprimer.setObjectName("btnSupprimer")

        for bouton in (
            self.btnNouvelle, self.btnModifier, self.btnSupprimer
        ):
            bouton.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            barre.addWidget(bouton)

        barre.addStretch()
        principal.addLayout(barre)

        ####################################################
        # Tableau
        ####################################################

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Règle", "Période", "Du → au",
            "Modèle appliqué", "Sur quoi", "Priorité",
        ])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        entete = self.table.horizontalHeader()
        entete.setSectionResizeMode(1, QHeaderView.Stretch)
        entete.setSectionResizeMode(2, QHeaderView.Fixed)
        entete.setSectionResizeMode(3, QHeaderView.Fixed)
        entete.setSectionResizeMode(4, QHeaderView.Stretch)
        entete.setSectionResizeMode(5, QHeaderView.Fixed)
        entete.setSectionResizeMode(6, QHeaderView.Fixed)

        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 190)
        self.table.setColumnWidth(5, 260)
        self.table.setColumnWidth(6, 80)

        self.table.doubleClicked.connect(self.modifier)

        principal.addWidget(self.table)

        self.btnNouvelle.clicked.connect(self.nouvelle)
        self.btnModifier.clicked.connect(self.modifier)
        self.btnSupprimer.clicked.connect(self.supprimer)

        self.charger()

    ########################################################
    # Chargement
    ########################################################

    def charger(self):

        self._majApercuJour()

        self.table.setRowCount(0)

        for regle in self.manager.regles():

            ligne = self.table.rowCount()
            self.table.insertRow(ligne)

            morceaux = []

            types = self.manager.types_du_modele(
                regle["modele_fiche_id"]
            )

            if types:
                morceaux.append(
                    " ou ".join(
                        LIBELLES_TYPES.get(t, t) for t in types
                    )
                )

            if regle["categorie_site_id"]:
                morceaux.append(regle["nom_categorie"] or "?")

            cible = " + ".join(morceaux) or "Tous les produits"

            valeurs = [
                str(regle["id"]),
                regle["nom"] or "(sans nom)",
                regle["nom_periode"] or "—",
                f"{date_fr(normaliser_date(regle['date_debut']))} → "
                f"{date_fr(normaliser_date(regle['date_fin']))}",
                regle["nom_modele"] or "—",
                cible,
                str(regle["priorite"] or 0),
            ]

            for colonne, valeur in enumerate(valeurs):

                cellule = QTableWidgetItem(valeur)

                if not regle["actif"]:
                    cellule.setForeground(QColor("#767676"))

                self.table.setItem(ligne, colonne, cellule)

    def _majApercuJour(self):

        lignes = self.manager.apercu()

        if not lignes:

            self.detailJour.setText(
                "Aucune règle en cours : chaque produit utilise "
                "le modèle choisi dans sa fiche."
            )
            self.detailJour.setStyleSheet("color:#64748b;")
            return

        self.detailJour.setText("\n".join(f"• {l}" for l in lignes))
        self.detailJour.setStyleSheet(
            "color:#15803d; font-weight:600;"
        )

    ########################################################
    # Actions
    ########################################################

    def _selection(self):

        ligne = self.table.currentRow()

        if ligne < 0 or self.table.item(ligne, 0) is None:

            QMessageBox.information(
                self,
                "Aucune règle",
                "Sélectionne d'abord une règle dans la liste."
            )
            return None

        return int(self.table.item(ligne, 0).text())

    def nouvelle(self):

        dialog = RegleDialog("Nouvelle règle", self.manager, parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        saisie = dialog.valeurs()

        try:
            self.manager.ajouter(**saisie)
        except ValueError as erreur:
            QMessageBox.warning(self, "Règle refusée", str(erreur))
            return

        self.charger()

    def modifier(self):

        identifiant = self._selection()

        if identifiant is None:
            return

        regle = self.manager.obtenir(identifiant)

        dialog = RegleDialog(
            "Modifier la règle", self.manager, regle=regle, parent=self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        saisie = dialog.valeurs()

        try:
            self.manager.modifier(identifiant, **saisie)
        except ValueError as erreur:
            QMessageBox.warning(self, "Règle refusée", str(erreur))
            return

        self.charger()

    def supprimer(self):

        identifiant = self._selection()

        if identifiant is None:
            return

        ligne = self.table.currentRow()
        libelle = self.table.item(ligne, 1).text()

        reponse = QMessageBox.question(
            self,
            "Supprimer la règle",
            f"Supprimer « {libelle} » ?\n\n"
            "Les produits concernés reprendront le modèle "
            "choisi dans leur fiche."
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        self.manager.supprimer(identifiant)

        self.charger()