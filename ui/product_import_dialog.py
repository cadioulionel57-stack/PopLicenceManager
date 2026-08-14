from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)

from modules.product_import_manager import ProductImportManager


class ProductImportDialog(QDialog):
    """
    Fenêtre affichée en cliquant sur "Importer un CSV" dans
    la liste Produits.

    Deux temps :

    1. On choisit un fichier : il est ANALYSÉ, jamais
       importé. Le rapport s'affiche.

    2. Le bouton Importer ne s'active que s'il y a au moins
       une ligne valide.

    Aucun SKU n'est lu dans le fichier : chaque produit reçoit
    le sien via la numérotation du logiciel, exactement comme
    une fiche créée à la main.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.chemin = None
        self.rapport = None
        self.manager = ProductImportManager()

        self.setWindowTitle("Importer des produits depuis un CSV")
        self.setMinimumWidth(680)
        self.setMinimumHeight(520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        ####################################################
        # Choix du fichier
        ####################################################

        groupeFichier = QGroupBox("1. Fichier à importer")
        layoutFichier = QHBoxLayout(groupeFichier)

        self.labelFichier = QLabel("Aucun fichier sélectionné")
        self.labelFichier.setStyleSheet(
            "color:#475569; font-size:10pt;"
        )
        self.labelFichier.setWordWrap(True)

        btnParcourir = QPushButton("📂 Parcourir…")
        btnParcourir.clicked.connect(self.choisir_fichier)

        layoutFichier.addWidget(self.labelFichier, 1)
        layoutFichier.addWidget(btnParcourir)

        layout.addWidget(groupeFichier)

        ####################################################
        # Rapport d'analyse
        ####################################################

        groupeRapport = QGroupBox("2. Analyse du fichier")
        layoutRapport = QVBoxLayout(groupeRapport)

        self.resume = QLabel(
            "Sélectionnez un fichier CSV pour lancer l'analyse."
        )
        self.resume.setStyleSheet("font-size:11pt;")
        self.resume.setWordWrap(True)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setStyleSheet(
            "font-family:Consolas,monospace; font-size:9pt;"
        )

        layoutRapport.addWidget(self.resume)
        layoutRapport.addWidget(self.detail)

        layout.addWidget(groupeRapport, 1)

        ####################################################
        # Boutons
        ####################################################

        note = QLabel(
            "Rien n'est écrit en base tant que vous n'avez pas "
            "cliqué sur Importer. Les lignes en erreur sont "
            "ignorées, les autres sont créées."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color:#475569; font-size:9pt;")
        layout.addWidget(note)

        ligneBoutons = QHBoxLayout()
        ligneBoutons.addStretch()

        btnAnnuler = QPushButton("Fermer")
        btnAnnuler.clicked.connect(self.reject)

        self.btnImporter = QPushButton("✅ Importer les produits")
        self.btnImporter.setEnabled(False)
        self.btnImporter.clicked.connect(self.importer)

        ligneBoutons.addWidget(btnAnnuler)
        ligneBoutons.addWidget(self.btnImporter)

        layout.addLayout(ligneBoutons)

    ########################################################
    # Choix et analyse
    ########################################################

    def choisir_fichier(self):

        chemin, _filtre = QFileDialog.getOpenFileName(
            self,
            "Choisir le fichier CSV",
            "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)"
        )

        if not chemin:
            return

        self.chemin = chemin
        self.labelFichier.setText(chemin)

        self.analyser()

    def analyser(self):

        self.rapport = self.manager.analyser(self.chemin)

        rapport = self.rapport

        lignes = []

        if rapport["marques_a_creer"]:

            lignes.append(
                "MARQUES QUI SERONT CRÉÉES "
                f"({len(rapport['marques_a_creer'])}) :"
            )

            for marque in rapport["marques_a_creer"]:
                lignes.append(f"   + {marque}")

            lignes.append("")

        if rapport["erreurs"]:

            lignes.append(
                f"ERREURS ({len(rapport['erreurs'])}) — "
                "ces lignes ne seront PAS importées :"
            )

            for message in rapport["erreurs"]:
                lignes.append(f"   ✖ {message}")

            lignes.append("")

        if rapport["avertissements"]:

            lignes.append(
                f"AVERTISSEMENTS ({len(rapport['avertissements'])}) — "
                "la ligne est importée, le champ reste vide :"
            )

            for message in rapport["avertissements"]:
                lignes.append(f"   ! {message}")

        if not lignes:
            lignes.append("Aucune anomalie détectée.")

        self.detail.setPlainText("\n".join(lignes))

        self.resume.setText(
            f"<b>{rapport['lignes']}</b> ligne(s) lue(s) — "
            f"<b style='color:#166534;'>{rapport['valides']} "
            f"importable(s)</b> — "
            f"<b style='color:#b91c1c;'>{len(rapport['erreurs'])} "
            f"en erreur</b>"
        )

        self.btnImporter.setEnabled(rapport["valides"] > 0)

    ########################################################
    # Import réel
    ########################################################

    def importer(self):

        reponse = QMessageBox.question(
            self,
            "Confirmer l'import",
            f"{self.rapport['valides']} produit(s) vont être "
            f"créés dans le logiciel.\n\n"
            f"Cette opération n'est pas annulable. Continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reponse != QMessageBox.Yes:
            return

        self.btnImporter.setEnabled(False)

        try:
            rapport = self.manager.importer(self.chemin)

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur pendant l'import",
                f"L'import s'est interrompu :\n\n{erreur}"
            )

            self.btnImporter.setEnabled(True)
            return

        message = f"{rapport['crees']} produit(s) créé(s)."

        if rapport["marques_creees"]:

            message += (
                f"\n\n{len(rapport['marques_creees'])} marque(s) "
                f"créée(s) : "
                + ", ".join(rapport["marques_creees"])
            )

        if rapport["erreurs"]:

            message += (
                f"\n\n{len(rapport['erreurs'])} ligne(s) ignorée(s) "
                f"pour cause d'erreur."
            )

        message += (
            "\n\nToutes les fiches créées sont marquées "
            "\"à terminer\" : il manque le poids, les "
            "descriptions et le SEO."
        )

        QMessageBox.information(
            self, "Import terminé", message
        )

        self.accept()