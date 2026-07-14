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
    QCheckBox,
    QTextEdit,
)
from PySide6.QtCore import Qt

from modules.modele_fiche_manager import ModeleFicheManager
from modules.reference_manager import ReferenceManager
from modules.bloc_emballage_cadeau_manager import BlocEmballageCadeauManager
from ui.modele_fiche_dialog import ModeleFicheDialog


LIBELLES_TYPE = {
    "stock": "Stock",
    "dropshipping": "Direct Fournisseur",
    "bundle": "Bundle",
    "precommande": "Précommande",
}


class ModelesFichePage(QWidget):
    """
    Gestion des modèles de fiche produit (chartes HTML) par
    thème — chaque modèle couvre un ou plusieurs types de
    produit (stock, dropshipping, bundle, précommande), un
    seul actif à la fois par thème pour chaque type qu'il
    couvre (celui utilisé en mode "Automatique").
    """

    def __init__(self):

        super().__init__()

        self.manager = ModeleFicheManager()
        self.managerThemes = ReferenceManager()
        self.managerEmballageCadeau = BlocEmballageCadeauManager()

        self.setStyleSheet("""
        QWidget{ background:#f4f7fb; font-family:'Segoe UI'; }
        QLabel#titre{ font-size:24px; font-weight:600; color:#0f2f5c; }
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
        QCheckBox::indicator{
            width:20px; height:20px;
            border:2px solid #144b8b; border-radius:5px;
            background:white;
        }
        QCheckBox::indicator:checked{
            background:#144b8b;
            image:none;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        entete = QHBoxLayout()
        titre = QLabel("📄 Modèles de fiche produit")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        info = QLabel(
            "Coche \"Actif\" sur tous les modèles que tu veux rendre "
            "disponibles — plusieurs modèles peuvent être actifs en "
            "même temps, y compris pour un même thème (ex : la "
            "version normale ET la version Noël). Ils apparaîtront "
            "tous ensemble dans la liste déroulante \"Modèle de "
            "fiche\" de chaque fiche produit, où tu choisis "
            "librement lequel utiliser, produit par produit."
        )
        info.setStyleSheet("color:#5a6b7d; font-size:9.5pt;")
        info.setWordWrap(True)
        layout.addWidget(info)

        entêteBoutons = QHBoxLayout()

        self.btnAjouter = QPushButton("➕ Nouveau modèle")
        self.btnAjouter.clicked.connect(self.ajouter)
        entêteBoutons.addWidget(self.btnAjouter)

        self.btnModifier = QPushButton("✏ Modifier")
        self.btnModifier.clicked.connect(self.modifier)
        entêteBoutons.addWidget(self.btnModifier)

        self.btnSupprimer = QPushButton("🗑 Supprimer")
        self.btnSupprimer.setObjectName("btnSupprimer")
        self.btnSupprimer.clicked.connect(self.supprimer)
        entêteBoutons.addWidget(self.btnSupprimer)

        entêteBoutons.addStretch()

        layout.addLayout(entêteBoutons)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Thème", "Types de produit",
            "Types d'articles", "Actif"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        ####################################################
        # Bloc réutilisable : éligibilité emballage cadeau
        ####################################################

        titreBloc = QLabel(
            "🎁 Bloc réutilisable — Éligibilité emballage cadeau"
        )
        titreBloc.setStyleSheet(
            "font-size:15px; font-weight:600; color:#0f2f5c; "
            "margin-top:10px;"
        )
        layout.addWidget(titreBloc)

        infoBloc = QLabel(
            "Ce bloc HTML s'insère automatiquement dans toutes les "
            "fiches Stock des produits cochés \"éligible emballage "
            "cadeau\" — un seul exemplaire à modifier ici, pas besoin "
            "de le dupliquer dans chaque modèle de thème. Variable "
            "disponible : {{prix_emballage_cadeau}}."
        )
        infoBloc.setStyleSheet("color:#5a6b7d; font-size:9.5pt;")
        infoBloc.setWordWrap(True)
        layout.addWidget(infoBloc)

        self.blocEmballageCadeau = QTextEdit()
        self.blocEmballageCadeau.setPlainText(
            self.managerEmballageCadeau.obtenir()
        )
        self.blocEmballageCadeau.setStyleSheet(
            "font-family:Consolas,monospace; font-size:9.5pt;"
        )
        self.blocEmballageCadeau.setMaximumHeight(200)
        layout.addWidget(self.blocEmballageCadeau)

        self.btnEnregistrerBloc = QPushButton(
            "💾 Enregistrer le bloc emballage cadeau"
        )
        self.btnEnregistrerBloc.clicked.connect(
            self.enregistrerBlocEmballageCadeau
        )
        layout.addWidget(self.btnEnregistrerBloc)

        self.charger()

    def enregistrerBlocEmballageCadeau(self):

        self.managerEmballageCadeau.definir(
            self.blocEmballageCadeau.toPlainText()
        )

        QMessageBox.information(
            self, "Enregistré",
            "Le bloc s'appliquera aux prochaines fiches générées."
        )

    def charger(self):

        self.table.setRowCount(0)

        # Référence vers chaque case affichée, indexée par
        # l'id du modèle — permet de mettre à jour l'état
        # coché/décoché sans jamais reconstruire le tableau
        # (voir _rafraichirCasesActif ci-dessous).
        self._cases = {}

        for ligne, modele in enumerate(self.manager.tous()):

            self.table.insertRow(ligne)

            self.table.setItem(
                ligne, 0, QTableWidgetItem(str(modele["id"]))
            )
            self.table.setItem(
                ligne, 1, QTableWidgetItem(modele["nom"] or "")
            )
            self.table.setItem(
                ligne, 2, QTableWidgetItem(modele["nom_theme"] or "")
            )

            libelles_types = ", ".join(
                LIBELLES_TYPE.get(t, t) for t in modele["types"]
            )
            self.table.setItem(
                ligne, 3, QTableWidgetItem(libelles_types)
            )

            self.table.setItem(
                ligne, 4,
                QTableWidgetItem(modele["types_articles_concernes"] or "")
            )

            case = QCheckBox()
            case.setChecked(bool(modele["actif"]))
            case.toggled.connect(
                lambda coche, mid=modele["id"]: self._basculerActif(
                    mid, coche
                )
            )

            self._cases[modele["id"]] = case

            conteneur = QWidget()
            layoutCase = QHBoxLayout(conteneur)
            layoutCase.addWidget(case)
            layoutCase.setAlignment(case, Qt.AlignmentFlag.AlignCenter)
            layoutCase.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(ligne, 5, conteneur)

    def _basculerActif(self, modele_id, coche):

        if coche:
            self.manager.basculer_actif(modele_id)
        else:
            self.manager.desactiver(modele_id)

        # Surtout NE PAS appeler self.charger() ici : ça
        # détruirait la case en cours de clic (celle qui émet
        # encore son propre signal toggled) et ferait remonter
        # toute la liste en haut à chaque bascule. On se
        # contente de mettre à jour l'état coché/décoché des
        # cases déjà affichées, sans toucher au reste du
        # tableau.
        self._rafraichirCasesActif()

    def _rafraichirCasesActif(self):
        """
        Relit les statuts "actif" en base et met à jour l'état
        coché/décoché de chaque case déjà affichée à l'écran,
        sans reconstruire le tableau (pas de perte de
        défilement, pas de destruction de widget en cours de
        clic).

        blockSignals est indispensable ici : sans ça,
        setChecked déclencherait à nouveau toggled → une
        nouvelle bascule en base → un nouvel appel ici, en
        boucle.
        """

        etats_actifs = {
            modele["id"]: bool(modele["actif"])
            for modele in self.manager.tous()
        }

        for modele_id, case in self._cases.items():

            valeur = etats_actifs.get(modele_id, False)

            if case.isChecked() != valeur:

                case.blockSignals(True)
                case.setChecked(valeur)
                case.blockSignals(False)

    def ajouter(self):

        themes = self.managerThemes.tous("themes_template")

        if not themes:
            QMessageBox.information(
                self, "Information",
                "Crée d'abord au moins un thème dans l'écran "
                "\"Thèmes de template\"."
            )
            return

        dialog = ModeleFicheDialog("Nouveau modèle", themes)

        if dialog.exec() != ModeleFicheDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.ajouter(
            nom,
            dialog.themeTemplate.currentData(),
            dialog.types_choisis(),
            dialog.htmlTemplate.toPlainText(),
            dialog.typesArticles.text().strip(),
        )

        self.charger()

    def modifier(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez un modèle.")
            return

        identifiant = int(self.table.item(ligne, 0).text())
        modele = self.manager.obtenir(identifiant)

        themes = self.managerThemes.tous("themes_template")

        dialog = ModeleFicheDialog(
            "Modifier le modèle",
            themes,
            modele["nom"],
            modele["theme_id"],
            modele["types"],
            modele["html_template"],
            modele["types_articles_concernes"] or "",
        )

        if dialog.exec() != ModeleFicheDialog.DialogCode.Accepted:
            return

        nom = dialog.nom.text().strip()

        if nom == "":
            return

        self.manager.modifier(
            identifiant,
            nom,
            dialog.themeTemplate.currentData(),
            dialog.types_choisis(),
            dialog.htmlTemplate.toPlainText(),
            dialog.typesArticles.text().strip(),
        )

        self.charger()

    def supprimer(self):

        ligne = self.table.currentRow()

        if ligne == -1:
            QMessageBox.information(self, "Information", "Sélectionnez un modèle.")
            return

        reponse = QMessageBox.question(
            self, "Confirmation", "Supprimer définitivement ce modèle ?"
        )

        if reponse != QMessageBox.StandardButton.Yes:
            return

        identifiant = int(self.table.item(ligne, 0).text())
        self.manager.supprimer(identifiant)

        self.charger()