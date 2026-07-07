from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from modules.canal_manager import CanalManager
from modules.categorie_manager import CategorieManager


class CategorieDialog(QDialog):

    def __init__(
        self,
        titre,
        nom="",
        canal_id=None,
        commission_pourcentage=None,
        paliers=None,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(560, 620)

        self.setStyleSheet("""
            QDialog{
                background:#edf3fa;
                font-family:"Segoe UI";
            }

            QFrame#card{
                background:white;
                border:1px solid #d8e1ed;
                border-radius:12px;
            }

            QLabel#titre{
                font-size:22px;
                font-weight:bold;
                color:#144b8b;
            }

            QLabel{
                color:#2d3436;
                font-size:11pt;
            }

            QLineEdit,
            QComboBox,
            QDoubleSpinBox{
                background:white;
                border:1px solid #cfd8e3;
                border-radius:8px;
                padding:8px;
                font-size:11pt;
            }

            QPushButton{
                background:#144b8b;
                color:white;
                border:none;
                border-radius:8px;
                padding:10px 18px;
                min-width:120px;
            }

            QPushButton:hover{
                background:#1d61b4;
            }

            QTableWidget{
                background:white;
                border:1px solid #cfd8e3;
                border-radius:8px;
                gridline-color:#e8edf5;
            }

            QHeaderView::section{
                background:#144b8b;
                color:white;
                font-weight:bold;
                border:none;
                padding:6px;
            }
        """)

        principal = QVBoxLayout(self)

        carte = QFrame()
        carte.setObjectName("card")
        principal.addWidget(carte)

        layout = QVBoxLayout(carte)

        titreLabel = QLabel(titre)
        titreLabel.setObjectName("titre")
        layout.addWidget(titreLabel)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Nom de la catégorie"))

        self.nom = QLineEdit()
        self.nom.setText(nom)
        layout.addWidget(self.nom)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Rattachée à (laisser vide = catégorie "
            "interne Pop Licence)"
        ))

        self.canal = QComboBox()
        self.canal.addItem(
            "— Catégorie interne Pop Licence —",
            None
        )

        self.canaux = CanalManager().tous()

        for canal in self.canaux:
            self.canal.addItem(canal["nom"], canal["id"])

        index = self.canal.findData(canal_id)
        if index != -1:
            self.canal.setCurrentIndex(index)

        layout.addWidget(self.canal)

        layout.addSpacing(10)

        ####################################################
        # Commission spécifique à cette catégorie
        ####################################################
        #
        # Ne concerne que les catégories rattachées à un
        # canal (une catégorie interne Pop Licence n'a pas
        # de commission de vente). Si la case n'est pas
        # cochée, c'est la commission par défaut du canal
        # qui s'applique automatiquement.
        #
        ####################################################

        self.commissionSpecifique = QCheckBox(
            "Commission spécifique à cette catégorie "
            "(sinon, celle du canal s'applique)"
        )

        layout.addWidget(self.commissionSpecifique)

        self.commission = QDoubleSpinBox()
        self.commission.setDecimals(2)
        self.commission.setMaximum(100)
        self.commission.setSuffix(" %")

        layout.addWidget(self.commission)

        if commission_pourcentage is not None:
            self.commissionSpecifique.setChecked(True)
            self.commission.setValue(commission_pourcentage)

        self.commissionSpecifique.toggled.connect(
            self.commission.setEnabled
        )

        layout.addSpacing(15)

        ####################################################
        # Paliers de commission selon le prix de vente
        ####################################################
        #
        # Ex : Amazon Vêtements = 5% jusqu'à 15€, 10%
        # jusqu'à 20€, 17% au-delà. Si activé, remplace
        # la commission simple ci-dessus.
        #
        ####################################################

        self.utiliserPaliers = QCheckBox(
            "Utiliser des paliers de prix (taux différent "
            "selon le prix de vente)"
        )

        layout.addWidget(self.utiliserPaliers)

        self.tablePaliers = QTableWidget()
        self.tablePaliers.setColumnCount(2)
        self.tablePaliers.setHorizontalHeaderLabels([
            "Jusqu'à (€) — vide = sans limite",
            "Commission (%)"
        ])
        self.tablePaliers.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tablePaliers.setMaximumHeight(150)

        layout.addWidget(self.tablePaliers)

        boutonsPaliers = QHBoxLayout()

        self.btnAjouterPalier = QPushButton("+ Ajouter un palier")
        self.btnRetirerPalier = QPushButton("- Retirer le dernier")

        boutonsPaliers.addWidget(self.btnAjouterPalier)
        boutonsPaliers.addWidget(self.btnRetirerPalier)
        boutonsPaliers.addStretch()

        layout.addLayout(boutonsPaliers)

        self.btnAjouterPalier.clicked.connect(
            lambda: self._ajouterLignePalier()
        )
        self.btnRetirerPalier.clicked.connect(self._retirerLignePalier)

        if paliers:

            self.utiliserPaliers.setChecked(True)

            for palier in paliers:

                self._ajouterLignePalier(
                    seuil=palier["seuil_prix_max"],
                    commission=palier["commission_pourcentage"]
                )

        self.utiliserPaliers.toggled.connect(
            self._actualiserDisponibilitePaliers
        )

        self.canal.currentIndexChanged.connect(
            self._actualiserDisponibiliteCommission
        )

        self._actualiserDisponibiliteCommission()
        self._actualiserDisponibilitePaliers()

        layout.addStretch()

        boutons = QHBoxLayout()
        boutons.addStretch()

        self.btnAnnuler = QPushButton("Annuler")
        self.btnEnregistrer = QPushButton("Enregistrer")

        boutons.addWidget(self.btnAnnuler)
        boutons.addWidget(self.btnEnregistrer)

        layout.addLayout(boutons)

        self.btnAnnuler.clicked.connect(self.reject)
        self.btnEnregistrer.clicked.connect(self.accept)

    def _actualiserDisponibiliteCommission(self):
        """
        Désactive le réglage de commission si la
        catégorie est interne à Pop Licence (aucun
        canal sélectionné) : une commission n'a de
        sens que pour une catégorie de canal de vente.
        """

        est_liee_a_un_canal = self.canal.currentData() is not None

        self.commissionSpecifique.setEnabled(est_liee_a_un_canal)
        self.utiliserPaliers.setEnabled(est_liee_a_un_canal)

        if not est_liee_a_un_canal:
            self.commissionSpecifique.setChecked(False)
            self.utiliserPaliers.setChecked(False)

        self.commission.setEnabled(
            est_liee_a_un_canal
            and self.commissionSpecifique.isChecked()
            and not self.utiliserPaliers.isChecked()
        )

    def _actualiserDisponibilitePaliers(self):
        """
        Quand les paliers sont activés, ils remplacent
        la commission simple (les deux ne peuvent pas
        s'appliquer en même temps).
        """

        actif = self.utiliserPaliers.isChecked()

        self.tablePaliers.setEnabled(actif)
        self.btnAjouterPalier.setEnabled(actif)
        self.btnRetirerPalier.setEnabled(actif)

        if actif:
            self.commissionSpecifique.setChecked(False)
            self.commissionSpecifique.setEnabled(False)
            self.commission.setEnabled(False)
        else:
            self.commissionSpecifique.setEnabled(
                self.canal.currentData() is not None
            )

    def _ajouterLignePalier(self, seuil=None, commission=None):

        ligne = self.tablePaliers.rowCount()
        self.tablePaliers.insertRow(ligne)

        itemSeuil = QTableWidgetItem(
            "" if seuil is None else str(seuil)
        )
        itemCommission = QTableWidgetItem(
            "" if commission is None else str(commission)
        )

        self.tablePaliers.setItem(ligne, 0, itemSeuil)
        self.tablePaliers.setItem(ligne, 1, itemCommission)

    def _retirerLignePalier(self):

        ligne = self.tablePaliers.rowCount()

        if ligne > 0:
            self.tablePaliers.removeRow(ligne - 1)

    def canal_id(self):
        return self.canal.currentData()

    def commission_pourcentage(self):

        if not self.commissionSpecifique.isChecked():
            return None

        return self.commission.value()

    def paliers_saisis(self):
        """
        Renvoie la liste des paliers saisis dans le
        tableau, sous la forme attendue par
        CategorieManager.definir_paliers(), triés par
        seuil croissant (le palier sans limite en
        dernier).

        Renvoie une liste vide si l'option "paliers" 
        n'est pas cochée.
        """

        if not self.utiliserPaliers.isChecked():
            return []

        resultat = []

        for ligne in range(self.tablePaliers.rowCount()):

            itemSeuil = self.tablePaliers.item(ligne, 0)
            itemCommission = self.tablePaliers.item(ligne, 1)

            texteSeuil = itemSeuil.text().strip() if itemSeuil else ""
            texteCommission = (
                itemCommission.text().strip() if itemCommission else ""
            )

            try:
                commission = float(texteCommission)
            except ValueError:
                continue

            try:
                seuil = (
                    float(texteSeuil) if texteSeuil != "" else None
                )
            except ValueError:
                seuil = None

            resultat.append({
                "seuil_prix_max": seuil,
                "commission_pourcentage": commission
            })

        resultat.sort(
            key=lambda p: (
                p["seuil_prix_max"] is None,
                p["seuil_prix_max"] or 0
            )
        )

        return resultat