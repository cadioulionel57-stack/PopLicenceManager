"""
Fenetre d'import des emplacements de stockage depuis le collecteur (PTC).

L'utilisateur choisit son fichier, controle le tableau, puis valide.
Rien n'est ecrit en base avant le clic sur "Appliquer".
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from modules.emplacement_import_manager import EmplacementImportManager


VERT = QColor(212, 237, 218)
ORANGE = QColor(255, 234, 199)
ROUGE = QColor(248, 215, 218)
GRIS = QColor(233, 236, 239)


class EmplacementImportDialog(QDialog):
    """Import du fichier PTC de rangement : produit puis emplacement."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importer les emplacements de rangement")
        self.resize(900, 600)

        self._manager = EmplacementImportManager()
        self._lignes = []

        principal = QVBoxLayout(self)

        explication = QLabel(
            "Le collecteur doit avoir scanne, dans cet ordre : le code du "
            "produit, puis le code de son emplacement, et ainsi de suite.\n"
            "Un emplacement commence par une lettre (exemple A01-01-07), "
            "un code produit est numerique."
        )
        explication.setWordWrap(True)
        principal.addWidget(explication)

        barre = QHBoxLayout()
        self.labelFichier = QLabel("Aucun fichier choisi")
        self.btnChoisir = QPushButton("Choisir le fichier du collecteur")
        self.btnChoisir.clicked.connect(self.choisirFichier)
        barre.addWidget(self.btnChoisir)
        barre.addWidget(self.labelFichier, 1)
        principal.addLayout(barre)

        self.tableau = QTableWidget(0, 5)
        self.tableau.setHorizontalHeaderLabels(
            ["Code scanne", "Produit", "Emplacement actuel",
             "Nouvel emplacement", "Etat"]
        )
        self.tableau.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tableau.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        principal.addWidget(self.tableau, 1)

        self.zoneAnomalies = QTextEdit()
        self.zoneAnomalies.setReadOnly(True)
        self.zoneAnomalies.setMaximumHeight(90)
        self.zoneAnomalies.setPlaceholderText("Aucune anomalie")
        principal.addWidget(self.zoneAnomalies)

        self.labelResume = QLabel("")
        principal.addWidget(self.labelResume)

        boutons = QHBoxLayout()
        boutons.addStretch(1)
        self.btnAnnuler = QPushButton("Annuler")
        self.btnAnnuler.clicked.connect(self.reject)
        self.btnAppliquer = QPushButton("Appliquer les emplacements")
        self.btnAppliquer.setEnabled(False)
        self.btnAppliquer.clicked.connect(self.appliquer)
        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnAppliquer)
        principal.addLayout(boutons)

    # ------------------------------------------------------------------
    def choisirFichier(self):
        chemin, _ = QFileDialog.getOpenFileName(
            self,
            "Fichier du collecteur",
            "",
            "Fichiers texte et CSV (*.txt *.csv *.tsv);;Tous les fichiers (*)",
        )
        if not chemin:
            return

        try:
            resultat = self._manager.analyser(chemin)
        except Exception as erreur:
            QMessageBox.critical(
                self, "Lecture impossible",
                "Le fichier n'a pas pu etre lu :\n\n%s" % erreur
            )
            return

        self.labelFichier.setText(chemin)
        self._lignes = resultat["lignes"]
        self._remplirTableau(resultat["anomalies"])

    # ------------------------------------------------------------------
    def _remplirTableau(self, anomalies):
        self.tableau.setRowCount(0)

        libelles = {
            "nouveau": "Premier rangement",
            "deplace": "Deplace",
            "inchange": "Inchange",
            "inconnu": "Produit introuvable",
        }
        couleurs = {
            "nouveau": VERT,
            "deplace": ORANGE,
            "inchange": GRIS,
            "inconnu": ROUGE,
        }

        compteurs = {"nouveau": 0, "deplace": 0, "inchange": 0, "inconnu": 0}

        for ligne in self._lignes:
            etat = ligne["etat"]
            compteurs[etat] = compteurs.get(etat, 0) + 1

            rang = self.tableau.rowCount()
            self.tableau.insertRow(rang)

            valeurs = [
                ligne["code"],
                ligne["nom"],
                ligne["ancien"],
                ligne["emplacement"],
                libelles.get(etat, etat),
            ]
            for colonne, valeur in enumerate(valeurs):
                cellule = QTableWidgetItem(str(valeur))
                cellule.setBackground(couleurs.get(etat, GRIS))
                self.tableau.setItem(rang, colonne, cellule)

        self.tableau.resizeColumnsToContents()
        self.tableau.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

        if anomalies:
            self.zoneAnomalies.setPlainText("\n".join(anomalies))
        else:
            self.zoneAnomalies.setPlainText("")

        a_appliquer = compteurs["nouveau"] + compteurs["deplace"]
        self.labelResume.setText(
            "%d a ranger, %d deplacements, %d inchanges, "
            "%d produits introuvables" % (
                compteurs["nouveau"], compteurs["deplace"],
                compteurs["inchange"], compteurs["inconnu"],
            )
        )
        self.btnAppliquer.setEnabled(a_appliquer > 0)

    # ------------------------------------------------------------------
    def appliquer(self):
        introuvables = sum(
            1 for l in self._lignes if l["etat"] == "inconnu"
        )
        if introuvables:
            reponse = QMessageBox.question(
                self,
                "Produits introuvables",
                "%d code(s) scanne(s) ne correspondent a aucun produit "
                "et seront ignores.\n\nContinuer ?" % introuvables,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reponse != QMessageBox.StandardButton.Yes:
                return

        try:
            modifies = self._manager.appliquer(self._lignes)
        except Exception as erreur:
            QMessageBox.critical(
                self, "Enregistrement impossible",
                "Les emplacements n'ont pas pu etre enregistres :\n\n%s"
                % erreur
            )
            return

        QMessageBox.information(
            self, "Emplacements mis a jour",
            "%d produit(s) ont recu leur emplacement." % modifies
        )
        self.accept()