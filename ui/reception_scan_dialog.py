from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QColor, QFont

from modules.reception_scan_manager import ReceptionScanManager


class ReceptionScanDialog(QDialog):
    """
    Contrôle d'une livraison fournisseur au collecteur.

    On confronte ce qui a été scanné à ce qui avait été
    commandé. Ce sont les quantités réellement arrivées qui
    entrent en stock, et la commande reste ouverte tant
    qu'il reste un reliquat.
    """

    SEPARATEURS = [
        ("Détection automatique", None),
        ("Point-virgule  ;", ";"),
        ("Tabulation", "\t"),
        ("Virgule  ,", ","),
        ("Barre verticale  |", "|"),
    ]

    def __init__(self, achat_id, numero="", parent=None):

        super().__init__(parent)

        self.manager = ReceptionScanManager()
        self.achat_id = achat_id
        self.lignes = []
        self.intrus = []

        self.setWindowTitle(f"Contrôler la réception — {numero}")
        self.setMinimumSize(1060, 660)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 18, 18, 18)
        principal.setSpacing(14)

        titre = QLabel(f"Contrôler la réception — {numero}")
        police = QFont()
        police.setPointSize(14)
        police.setBold(True)
        titre.setFont(police)
        principal.addWidget(titre)

        explication = QLabel(
            "Scanne les articles reçus au collecteur, puis importe "
            "le fichier ici. Seules les quantités réellement "
            "arrivées entreront en stock ; le reste attendra la "
            "prochaine livraison."
        )
        explication.setWordWrap(True)
        principal.addWidget(explication)

        ####################################################
        # Fichier
        ####################################################

        ligneFichier = QHBoxLayout()

        self.champFichier = QLineEdit()
        self.champFichier.setPlaceholderText("Aucun fichier choisi")
        self.champFichier.setReadOnly(True)
        ligneFichier.addWidget(self.champFichier)

        self.btnParcourir = QPushButton("📂  Parcourir")
        self.btnParcourir.clicked.connect(self._choisirFichier)
        ligneFichier.addWidget(self.btnParcourir)

        principal.addLayout(ligneFichier)

        ####################################################
        # Réglages de lecture
        ####################################################

        reglages = QFormLayout()

        self.separateur = QComboBox()

        for libelle, _ in self.SEPARATEURS:
            self.separateur.addItem(libelle)

        reglages.addRow("Séparateur", self.separateur)

        colonnes = QHBoxLayout()

        self.colonneCode = QSpinBox()
        self.colonneCode.setMinimum(1)
        self.colonneCode.setMaximum(50)
        self.colonneCode.setValue(1)
        colonnes.addWidget(QLabel("Code-barres :"))
        colonnes.addWidget(self.colonneCode)

        self.colonneQuantite = QSpinBox()
        self.colonneQuantite.setMinimum(1)
        self.colonneQuantite.setMaximum(50)
        self.colonneQuantite.setValue(2)
        colonnes.addWidget(QLabel("     Quantité :"))
        colonnes.addWidget(self.colonneQuantite)

        colonnes.addStretch()

        reglages.addRow("Colonnes du fichier", colonnes)

        self.ignorerEntete = QCheckBox(
            "La première ligne est un en-tête"
        )
        reglages.addRow("", self.ignorerEntete)

        principal.addLayout(reglages)

        self.btnLire = QPushButton("🔍  Lire le fichier")
        self.btnLire.clicked.connect(self._lire)
        self.btnLire.setEnabled(False)
        principal.addWidget(self.btnLire)

        ####################################################
        # Tableau
        ####################################################

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(6)
        self.tableau.setHorizontalHeaderLabels([
            "Produit",
            "EAN",
            "Commandé",
            "Déjà reçu",
            "Scanné",
            "Reliquat",
        ])

        entete = self.tableau.horizontalHeader()
        entete.setSectionResizeMode(0, QHeaderView.Stretch)
        entete.setSectionResizeMode(1, QHeaderView.Fixed)
        entete.setSectionResizeMode(2, QHeaderView.Fixed)
        entete.setSectionResizeMode(3, QHeaderView.Fixed)
        entete.setSectionResizeMode(4, QHeaderView.Fixed)
        entete.setSectionResizeMode(5, QHeaderView.Fixed)

        self.tableau.setColumnWidth(1, 150)
        self.tableau.setColumnWidth(2, 95)
        self.tableau.setColumnWidth(3, 95)
        self.tableau.setColumnWidth(4, 95)
        self.tableau.setColumnWidth(5, 95)

        principal.addWidget(self.tableau)

        self.resume = QLabel("")
        self.resume.setWordWrap(True)
        principal.addWidget(self.resume)

        self.alerte = QLabel("")
        self.alerte.setWordWrap(True)
        self.alerte.setStyleSheet(
            "color:#c0392b; font-weight:600;"
        )
        principal.addWidget(self.alerte)

        ####################################################
        # Date et commentaire
        ####################################################

        bas = QFormLayout()

        self.dateReception = QDateEdit()
        self.dateReception.setCalendarPopup(True)
        self.dateReception.setDate(QDate.currentDate())
        bas.addRow("Date de réception", self.dateReception)

        self.commentaire = QLineEdit()
        self.commentaire.setPlaceholderText(
            "Facultatif : n° de bon de livraison, colis abîmé..."
        )
        bas.addRow("Commentaire", self.commentaire)

        principal.addLayout(bas)

        ####################################################
        # Boutons
        ####################################################

        boutons = QHBoxLayout()
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnAnnuler.setObjectName("btnSecondaire")
        self.btnAnnuler.clicked.connect(self.reject)
        boutons.addWidget(self.btnAnnuler)

        self.btnValider = QPushButton("💾  Valider la réception")
        self.btnValider.clicked.connect(self._valider)
        self.btnValider.setEnabled(False)
        boutons.addWidget(self.btnValider)

        principal.addLayout(boutons)

        self._afficherCommande()

    ########################################################
    # Affichage initial
    ########################################################

    def _afficherCommande(self):
        """
        Montre la commande telle qu'elle est avant tout scan :
        l'utilisateur voit ce qui est attendu, même s'il n'a
        pas encore de fichier.
        """

        commandees = self.manager.lignes_commande(self.achat_id)

        self.tableau.setRowCount(0)

        for ligne in commandees:

            index = self.tableau.rowCount()
            self.tableau.insertRow(index)

            commande = ligne["quantite"] or 0
            deja = ligne["quantite_recue"] or 0

            valeurs = [
                ligne["nom_produit"] or ligne["nom_fiche"] or "",
                ligne["ean"] or "",
                str(commande),
                str(deja),
                "0",
                str(commande - deja),
            ]

            for colonne, valeur in enumerate(valeurs):
                self.tableau.setItem(
                    index, colonne, QTableWidgetItem(valeur)
                )

        self.resume.setText(
            f"{self.tableau.rowCount()} ligne(s) attendue(s). "
            "Choisis le fichier du collecteur pour comparer."
        )

    ########################################################
    # Fichier
    ########################################################

    def _choisirFichier(self):

        chemin, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le fichier du collecteur",
            "",
            "Fichiers de comptage (*.csv *.txt *.tsv);;"
            "Tous les fichiers (*.*)",
        )

        if not chemin:
            return

        self.champFichier.setText(chemin)
        self.btnLire.setEnabled(True)
        self.btnValider.setEnabled(False)
        self.alerte.setText("")

    ########################################################
    # Lecture
    ########################################################

    def _lire(self):

        chemin = self.champFichier.text().strip()

        if chemin == "":
            return

        separateur = self.SEPARATEURS[
            self.separateur.currentIndex()
        ][1]

        try:

            lectures = self.manager.lire_fichier(
                chemin,
                colonne_code=self.colonneCode.value() - 1,
                colonne_quantite=self.colonneQuantite.value() - 1,
                separateur=separateur,
                ignorer_premiere_ligne=self.ignorerEntete.isChecked(),
            )

        except OSError as erreur:

            QMessageBox.warning(
                self,
                "Fichier illisible",
                f"Impossible d'ouvrir le fichier :\n\n{erreur}"
            )
            return

        if not lectures:

            QMessageBox.information(
                self,
                "Fichier vide",
                "Aucun code-barres n'a été trouvé.\n\n"
                "Vérifie le séparateur et le numéro de la "
                "colonne du code-barres."
            )
            return

        self.lignes, self.intrus = self.manager.preparer(
            self.achat_id, lectures
        )

        self._remplirTableau()

    def _remplirTableau(self):

        self.tableau.setRowCount(0)

        complets = 0
        partiels = 0
        surplus = 0
        scannes = 0

        for ligne in self.lignes:

            index = self.tableau.rowCount()
            self.tableau.insertRow(index)

            valeurs = [
                ligne["nom"],
                ligne["ean"],
                str(ligne["commande"]),
                str(ligne["deja_recue"]),
                str(ligne["scanne"]),
                str(ligne["reliquat"]),
            ]

            for colonne, valeur in enumerate(valeurs):
                self.tableau.setItem(
                    index, colonne, QTableWidgetItem(valeur)
                )

            scannes += ligne["scanne"]

            if ligne["reliquat"] < 0:
                surplus += 1
                self._colorer(index, QColor(254, 226, 226))

            elif ligne["reliquat"] == 0:
                complets += 1
                self._colorer(index, QColor(220, 252, 231))

            else:
                partiels += 1
                self._colorer(index, QColor(254, 243, 199))

        messages = [
            f"{scannes} article(s) scanné(s)",
            f"{complets} ligne(s) complète(s)",
            f"{partiels} avec reliquat",
        ]

        if surplus:
            messages.append(f"{surplus} livrée(s) en trop")

        self.resume.setText("   •   ".join(messages))

        if self.intrus:

            details = " ; ".join(
                f"{i['code']} ({i['quantite']})"
                for i in self.intrus
            )

            self.alerte.setText(
                f"⚠ {len(self.intrus)} code(s) scanné(s) ne "
                f"figurent pas dans cette commande : {details}. "
                "Ces articles n'entreront pas en stock."
            )

        else:
            self.alerte.setText("")

        self.btnValider.setEnabled(scannes > 0)

    def _colorer(self, index, couleur):

        for colonne in range(self.tableau.columnCount()):

            cellule = self.tableau.item(index, colonne)

            if cellule is not None:
                cellule.setBackground(couleur)

    ########################################################
    # Validation
    ########################################################

    def _valider(self):

        a_entrer = [
            l for l in self.lignes if (l.get("scanne") or 0) > 0
        ]

        if not a_entrer:

            QMessageBox.information(
                self,
                "Rien à enregistrer",
                "Aucun article scanné ne correspond à cette "
                "commande."
            )
            return

        reste = sum(
            max(0, l["reliquat"]) for l in self.lignes
        )

        message = (
            f"{len(a_entrer)} ligne(s) vont entrer en stock."
        )

        if reste > 0:
            message += (
                f"\n\nIl restera {reste} article(s) attendu(s) : "
                "la commande restera ouverte."
            )
        else:
            message += "\n\nLa commande sera soldée."

        reponse = QMessageBox.question(
            self, "Valider la réception", message + "\n\nContinuer ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        entrees, statut = self.manager.appliquer(
            self.achat_id,
            self.lignes,
            date_reception=self.dateReception.date().toString(
                "yyyy-MM-dd"
            ),
            commentaire=self.commentaire.text(),
        )

        QMessageBox.information(
            self,
            "Réception enregistrée",
            f"{entrees} ligne(s) entrée(s) en stock.\n"
            f"Statut de la commande : {statut or 'inchangé'}."
        )

        self.accept()