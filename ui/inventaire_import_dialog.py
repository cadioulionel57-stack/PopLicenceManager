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

from modules.inventaire_import_manager import InventaireImportManager


class InventaireImportDialog(QDialog):
    """
    Import d'un comptage réalisé au collecteur de données.

    Le fichier est relu, confronté au stock théorique, et
    affiché ligne à ligne. Rien n'est écrit en base tant que
    l'utilisateur n'a pas validé : c'est le tableau des
    écarts qui décide, pas le fichier.
    """

    SEPARATEURS = [
        ("Détection automatique", None),
        ("Point-virgule  ;", ";"),
        ("Tabulation", "\t"),
        ("Virgule  ,", ","),
        ("Barre verticale  |", "|"),
    ]

    def __init__(self, parent=None):

        super().__init__(parent)

        self.manager = InventaireImportManager()
        self.lignes = []

        self.setWindowTitle("Importer un inventaire")
        self.setMinimumSize(1000, 620)

        principal = QVBoxLayout(self)
        principal.setContentsMargins(18, 18, 18, 18)
        principal.setSpacing(14)

        titre = QLabel("Importer un inventaire")
        police = QFont()
        police.setPointSize(14)
        police.setBold(True)
        titre.setFont(police)
        principal.addWidget(titre)

        explication = QLabel(
            "Choisis le fichier sorti du collecteur, vérifie les "
            "écarts, puis valide. Les mouvements de stock ne sont "
            "écrits qu'à la validation."
        )
        explication.setWordWrap(True)
        principal.addWidget(explication)

        ####################################################
        # Choix du fichier
        ####################################################

        ligneFichier = QHBoxLayout()

        self.champFichier = QLineEdit()
        self.champFichier.setPlaceholderText(
            "Aucun fichier choisi"
        )
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
        # Tableau des écarts
        ####################################################

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(5)
        self.tableau.setHorizontalHeaderLabels([
            "Code-barres",
            "Produit",
            "Compté",
            "En stock",
            "Écart",
        ])

        entete = self.tableau.horizontalHeader()
        entete.setSectionResizeMode(0, QHeaderView.Fixed)
        entete.setSectionResizeMode(1, QHeaderView.Stretch)
        entete.setSectionResizeMode(2, QHeaderView.Fixed)
        entete.setSectionResizeMode(3, QHeaderView.Fixed)
        entete.setSectionResizeMode(4, QHeaderView.Fixed)

        self.tableau.setColumnWidth(0, 160)
        self.tableau.setColumnWidth(2, 90)
        self.tableau.setColumnWidth(3, 90)
        self.tableau.setColumnWidth(4, 90)

        principal.addWidget(self.tableau)

        self.resume = QLabel("")
        self.resume.setWordWrap(True)
        principal.addWidget(self.resume)

        ####################################################
        # Date et commentaire
        ####################################################

        bas = QFormLayout()

        self.dateInventaire = QDateEdit()
        self.dateInventaire.setCalendarPopup(True)
        self.dateInventaire.setDate(QDate.currentDate())
        bas.addRow("Date du comptage", self.dateInventaire)

        self.commentaire = QLineEdit()
        self.commentaire.setPlaceholderText(
            "Facultatif : inventaire annuel, recomptage rayon..."
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

        self.btnValider = QPushButton("💾  Valider l'inventaire")
        self.btnValider.clicked.connect(self._valider)
        self.btnValider.setEnabled(False)
        boutons.addWidget(self.btnValider)

        principal.addLayout(boutons)

    ########################################################
    # Choix du fichier
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

        self.tableau.setRowCount(0)
        self.lignes = []
        self.btnValider.setEnabled(False)
        self.resume.setText("")

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

        self.lignes = self.manager.preparer(lectures)

        self._remplirTableau()

    def _remplirTableau(self):

        self.tableau.setRowCount(0)

        inconnus = 0
        justes = 0
        ecarts = 0

        for ligne in self.lignes:

            index = self.tableau.rowCount()
            self.tableau.insertRow(index)

            self.tableau.setItem(
                index, 0, QTableWidgetItem(ligne["code"])
            )
            self.tableau.setItem(
                index, 1, QTableWidgetItem(ligne["nom"])
            )
            self.tableau.setItem(
                index,
                2,
                QTableWidgetItem(str(ligne["quantite_comptee"])),
            )

            if not ligne["connu"]:

                inconnus += 1

                self.tableau.setItem(
                    index, 3, QTableWidgetItem("—")
                )
                self.tableau.setItem(
                    index, 4, QTableWidgetItem("—")
                )

                self._colorer(index, QColor(254, 226, 226))

                continue

            self.tableau.setItem(
                index,
                3,
                QTableWidgetItem(str(ligne["quantite_theorique"])),
            )

            ecart = ligne["ecart"]

            self.tableau.setItem(
                index, 4, QTableWidgetItem(f"{ecart:+d}")
            )

            if ecart == 0:
                justes += 1
                self._colorer(index, QColor(220, 252, 231))
            else:
                ecarts += 1
                self._colorer(index, QColor(254, 243, 199))

        messages = [
            f"{len(self.lignes)} référence(s) lue(s)",
            f"{justes} sans écart",
            f"{ecarts} à régulariser",
        ]

        if inconnus:
            messages.append(
                f"⚠ {inconnus} code(s) inconnu(s) — ces lignes "
                "seront ignorées à la validation"
            )

        self.resume.setText("   •   ".join(messages))

        self.btnValider.setEnabled(ecarts > 0)

    def _colorer(self, index, couleur):

        for colonne in range(self.tableau.columnCount()):

            cellule = self.tableau.item(index, colonne)

            if cellule is not None:
                cellule.setBackground(couleur)

    ########################################################
    # Validation
    ########################################################

    def _valider(self):

        a_regulariser = [
            l for l in self.lignes
            if l["connu"] and (l["ecart"] or 0) != 0
        ]

        if not a_regulariser:

            QMessageBox.information(
                self,
                "Rien à faire",
                "Aucun écart à régulariser."
            )
            return

        reponse = QMessageBox.question(
            self,
            "Valider l'inventaire",
            f"{len(a_regulariser)} mouvement(s) de stock vont "
            "être écrits.\n\nCette opération ne peut pas être "
            "annulée automatiquement. Continuer ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        ecrits, sans_ecart = self.manager.appliquer(
            self.lignes,
            date_inventaire=self.dateInventaire.date().toString(
                "yyyy-MM-dd"
            ),
            commentaire=self.commentaire.text(),
        )

        QMessageBox.information(
            self,
            "Inventaire enregistré",
            f"{ecrits} mouvement(s) écrit(s).\n"
            f"{sans_ecart} référence(s) étaient déjà justes.\n\n"
            "Les mouvements sont visibles dans l'historique de "
            "chaque produit."
        )

        self.accept()