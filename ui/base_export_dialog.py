from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QMessageBox,
)


class BaseExportDialog(QDialog):
    """
    Fenêtre affichée en cliquant sur "Export Base.com" dans
    la liste Produits.

    Pas de colonnes facultatives à choisir ici (contrairement
    à WiziShop) : Base.com acceptant n'importe quelle
    structure de CSV, toutes les colonnes utiles sont
    toujours incluses — le tri/mapping se fait une seule fois
    côté Base.com, pas ici.

    Ne s'occupe QUE des produits passés en paramètre (ceux
    cochés/sélectionnés dans la liste au moment du clic sur
    Export) — jamais de tout le catalogue.
    """

    def __init__(self, identifiants_produits, parent=None):

        super().__init__(parent)

        self.identifiants_produits = identifiants_produits

        self.setWindowTitle("Export vers Base.com")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        ####################################################
        # Résumé
        ####################################################

        nombre = len(self.identifiants_produits)

        resume = QLabel(
            f"📤 <b>{nombre} produit(s)</b> sélectionné(s) seront "
            f"exportés."
        )
        resume.setStyleSheet("font-size:11pt;")
        layout.addWidget(resume)

        ####################################################
        # Colonnes incluses — informatif, non modifiable
        ####################################################

        groupeColonnes = QGroupBox("✔ Colonnes incluses")
        layoutColonnes = QVBoxLayout(groupeColonnes)

        texteColonnes = QLabel(
            "SKU, EAN, EAN colis, Nom du produit, Description "
            "courte, Description longue, Marque, Poids, "
            "Longueur, Largeur, Hauteur, Stock, Photo 1/2/3, "
            "puis un Prix TTC et une Catégorie pour chaque "
            "canal de vente actif (hors canal Site, réservé à "
            "l'export WiziShop)."
        )
        texteColonnes.setWordWrap(True)
        texteColonnes.setStyleSheet("color:#475569; font-size:9.5pt;")

        layoutColonnes.addWidget(texteColonnes)

        noteMapping = QLabel(
            "ℹ️ Base.com accepte n'importe quelle structure de "
            "CSV — associe chaque colonne à son champ lors du "
            "premier import (cette association reste ensuite "
            "réutilisable automatiquement)."
        )
        noteMapping.setWordWrap(True)
        noteMapping.setStyleSheet(
            "color:#1d4ed8; font-size:9pt; font-style:italic;"
        )
        layoutColonnes.addWidget(noteMapping)

        layout.addWidget(groupeColonnes)

        ####################################################
        # Boutons d'action
        ####################################################

        barreBoutons = QHBoxLayout()

        btnAnnuler = QPushButton("Annuler")
        btnAnnuler.setObjectName("btnSecondaire")
        btnAnnuler.clicked.connect(self.reject)

        btnExporter = QPushButton("📤 Générer le fichier CSV")
        btnExporter.clicked.connect(self._genererExport)

        barreBoutons.addStretch()
        barreBoutons.addWidget(btnAnnuler)
        barreBoutons.addWidget(btnExporter)

        layout.addLayout(barreBoutons)

    def _genererExport(self):

        chemin, _filtre = QFileDialog.getSaveFileName(
            self,
            "Enregistrer l'export Base.com",
            "export_base.csv",
            "Fichiers CSV (*.csv)"
        )

        if not chemin:
            return

        from modules.base_export_manager import BaseExportManager

        gestionnaire = BaseExportManager()

        try:

            resultat = gestionnaire.exporter(
                identifiants_produits=self.identifiants_produits,
                chemin_fichier=chemin,
            )

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur d'export",
                f"L'export a échoué :\n{erreur}"
            )
            return

        message = (
            f"{resultat['nombre_lignes']} produit(s) exporté(s) avec "
            f"succès vers :\n{chemin}"
        )

        if resultat["fichier_trop_lourd"]:

            taille_mo = resultat["taille_octets"] / (1024 * 1024)
            message += (
                f"\n\n⚠️ Le fichier généré pèse {taille_mo:.1f} Mo, "
                f"au-delà de la limite de 2 Mo par import annoncée "
                f"par Base.com — exporte en plusieurs lots plus "
                f"petits si l'import échoue."
            )

        if resultat["produits_sans_gabarit"]:

            liste = "\n".join(
                f"• {nom}" for nom in resultat["produits_sans_gabarit"]
            )
            message += (
                f"\n\n⚠️ Attention : {len(resultat['produits_sans_gabarit'])} "
                f"produit(s) n'ont aucun modèle de fiche actif pour leur "
                f"thème — leur Description longue utilise le texte de "
                f"secours au lieu du HTML mis en forme :\n{liste}"
            )

        QMessageBox.information(
            self,
            "Export terminé",
            message
        )

        self.accept()