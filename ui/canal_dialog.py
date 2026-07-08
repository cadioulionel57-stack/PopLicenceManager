from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QFrame,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt

from modules.grille_transport_manager import GrilleTransportManager


class CanalDialog(QDialog):

    def __init__(
        self,
        titre,
        nom="",
        type_canal="marketplace",
        commission_pourcentage=0.0,
        frais_fixe_ht=0.0,
        frais_paiement_pourcentage=0.0,
        frais_paiement_fixe_ht=0.0,
        taux_tsn_pourcentage=0.0,
        port_inclus=False,
        utilise_grille_fba=False,
        ordre=0,
        transporteurs_autorises=None,
    ):

        super().__init__()

        self.setWindowTitle(titre)
        self.resize(520, 700)

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

        layout.addWidget(QLabel("Nom du canal (ex : Amazon FBM, Cdiscount, WiziShop...)"))

        self.nom = QLineEdit()
        self.nom.setText(nom)
        layout.addWidget(self.nom)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Type"))

        self.type = QComboBox()
        self.type.addItem("Site (boutique en propre)", "site")
        self.type.addItem("Marketplace", "marketplace")

        index = self.type.findData(type_canal)
        if index != -1:
            self.type.setCurrentIndex(index)

        layout.addWidget(self.type)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Commission de vente (%)"))

        self.commission = QDoubleSpinBox()
        self.commission.setDecimals(2)
        self.commission.setMaximum(100)
        self.commission.setSuffix(" %")
        self.commission.setValue(commission_pourcentage)
        layout.addWidget(self.commission)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Frais fixe par vente (HT)"))

        self.fraisFixe = QDoubleSpinBox()
        self.fraisFixe.setDecimals(2)
        self.fraisFixe.setMaximum(9999)
        self.fraisFixe.setSuffix(" €")
        self.fraisFixe.setValue(frais_fixe_ht)
        layout.addWidget(self.fraisFixe)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Frais de paiement par défaut (% du prix de "
            "vente HT) — ex : PayPal 2,9%, CB 1%, 0% si la "
            "marketplace encaisse elle-même"
        ))

        self.fraisPaiementPourcentage = QDoubleSpinBox()
        self.fraisPaiementPourcentage.setDecimals(2)
        self.fraisPaiementPourcentage.setMaximum(100)
        self.fraisPaiementPourcentage.setSuffix(" %")
        self.fraisPaiementPourcentage.setValue(frais_paiement_pourcentage)
        layout.addWidget(self.fraisPaiementPourcentage)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Frais de paiement fixe par vente (HT) — ex : "
            "0,35€ PayPal par transaction"
        ))

        self.fraisPaiementFixe = QDoubleSpinBox()
        self.fraisPaiementFixe.setDecimals(2)
        self.fraisPaiementFixe.setMaximum(999)
        self.fraisPaiementFixe.setSuffix(" €")
        self.fraisPaiementFixe.setValue(frais_paiement_fixe_ht)
        layout.addWidget(self.fraisPaiementFixe)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Taxe sur les services numériques - TSN (% de "
            "la commission) — ex : Amazon 3,5%, 0 sinon"
        ))

        self.tauxTsn = QDoubleSpinBox()
        self.tauxTsn.setDecimals(2)
        self.tauxTsn.setMaximum(100)
        self.tauxTsn.setSuffix(" %")
        self.tauxTsn.setValue(taux_tsn_pourcentage)
        layout.addWidget(self.tauxTsn)

        layout.addSpacing(10)

        self.portInclus = QCheckBox(
            "Frais de port inclus dans le prix affiché "
            "(le client voit \"livraison gratuite\")"
        )
        self.portInclus.setChecked(port_inclus)
        layout.addWidget(self.portInclus)

        layout.addSpacing(10)

        self.utiliseGrilleFba = QCheckBox(
            "Ce canal utilise la grille FBA (Expédié par "
            "Amazon) — format de colis selon dimensions + "
            "poids, au lieu des transporteurs classiques"
        )
        self.utiliseGrilleFba.setChecked(utilise_grille_fba)
        layout.addWidget(self.utiliseGrilleFba)

        layout.addSpacing(10)

        layout.addWidget(QLabel("Ordre d'affichage"))

        self.ordre = QDoubleSpinBox()
        self.ordre.setDecimals(0)
        self.ordre.setMaximum(999)
        self.ordre.setValue(ordre)
        layout.addWidget(self.ordre)

        layout.addSpacing(10)

        layout.addWidget(QLabel(
            "Transporteurs autorisés pour ce canal "
            "(le moins cher sera automatiquement choisi "
            "selon le poids du produit — utile pour les "
            "marketplaces où le port doit être inclus)"
        ))

        self.listeTransporteurs = QListWidget()
        self.listeTransporteurs.setMaximumHeight(160)

        transporteurs_deja_autorises = {
            (t["transporteur_id"], t["offre"])
            for t in (transporteurs_autorises or [])
        }

        for option in GrilleTransportManager().offres_disponibles():

            item = QListWidgetItem(
                f"{option['transporteur']} — {option['offre']}"
            )
            item.setData(Qt.UserRole, (
                option["transporteur_id"],
                option["offre"]
            ))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            cle = (option["transporteur_id"], option["offre"])

            item.setCheckState(
                Qt.Checked
                if cle in transporteurs_deja_autorises
                else Qt.Unchecked
            )

            self.listeTransporteurs.addItem(item)

        layout.addWidget(self.listeTransporteurs)

        self.utiliseGrilleFba.toggled.connect(
            lambda coche: self.listeTransporteurs.setDisabled(coche)
        )
        self.listeTransporteurs.setDisabled(utilise_grille_fba)

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

    def type_canal(self):
        return self.type.currentData()

    def valeur_ordre(self):
        return int(self.ordre.value())

    def utilise_grille_fba_coche(self):
        return self.utiliseGrilleFba.isChecked()

    def transporteurs_selectionnes(self):
        """
        Renvoie [(transporteur_id, offre), ...] pour tous
        les transporteurs cochés dans la liste.
        """

        resultat = []

        for i in range(self.listeTransporteurs.count()):

            item = self.listeTransporteurs.item(i)

            if item.checkState() == Qt.Checked:
                resultat.append(item.data(Qt.UserRole))

        return resultat