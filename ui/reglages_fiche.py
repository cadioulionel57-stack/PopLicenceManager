from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)

from modules.generateur_fiche_html import GenerateurFicheHtml
from modules.parametre_manager import ParametreManager


class ReglagesFichePage(QWidget):
    """
    Réglages globaux utilisés dans les modèles de fiche
    produit (au lieu d'être codés en dur dans chaque
    charte HTML) — un changement ici s'applique à toutes
    les fiches généreées ensuite, sans toucher aux modèles.
    """

    def __init__(self):

        super().__init__()

        self.manager = ParametreManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        groupe = QGroupBox("⚙️ Réglages des fiches produit")
        form = QFormLayout(groupe)

        self.prixEmballageCadeau = QDoubleSpinBox()
        self.prixEmballageCadeau.setDecimals(2)
        self.prixEmballageCadeau.setSuffix(" € TTC")
        form.addRow(
            "Prix emballage cadeau", self.prixEmballageCadeau
        )

        self.seuilLivraisonStock = QDoubleSpinBox()
        self.seuilLivraisonStock.setDecimals(0)
        self.seuilLivraisonStock.setSuffix(" €")
        form.addRow(
            "Seuil livraison gratuite (Stock, référence)",
            self.seuilLivraisonStock
        )

        self.tarifLivraisonDf = QDoubleSpinBox()
        self.tarifLivraisonDf.setDecimals(2)
        self.tarifLivraisonDf.setSuffix(" € TTC")
        form.addRow(
            "Tarif livraison (Direct Fournisseur)", self.tarifLivraisonDf
        )

        self.seuilLivraisonDf = QDoubleSpinBox()
        self.seuilLivraisonDf.setDecimals(0)
        self.seuilLivraisonDf.setSuffix(" €")
        form.addRow(
            "Seuil livraison gratuite (DF)", self.seuilLivraisonDf
        )

        layout.addWidget(groupe)

        groupeStock = QGroupBox("🚚 Transporteurs — Produits en stock")
        formStock = QFormLayout(groupeStock)

        self.tarifMondialRelay = QDoubleSpinBox()
        self.tarifMondialRelay.setDecimals(2)
        self.tarifMondialRelay.setSuffix(" € TTC")
        formStock.addRow("Mondial Relay — tarif", self.tarifMondialRelay)

        self.seuilMondialRelay = QDoubleSpinBox()
        self.seuilMondialRelay.setDecimals(0)
        self.seuilMondialRelay.setSuffix(" €")
        formStock.addRow(
            "Mondial Relay — offert dès", self.seuilMondialRelay
        )

        self.tarifColissimo = QDoubleSpinBox()
        self.tarifColissimo.setDecimals(2)
        self.tarifColissimo.setSuffix(" € TTC")
        formStock.addRow("Colissimo — tarif", self.tarifColissimo)

        self.seuilColissimo = QDoubleSpinBox()
        self.seuilColissimo.setDecimals(0)
        self.seuilColissimo.setSuffix(" €")
        formStock.addRow("Colissimo — offert dès", self.seuilColissimo)

        self.tarifChronoRelais = QDoubleSpinBox()
        self.tarifChronoRelais.setDecimals(2)
        self.tarifChronoRelais.setSuffix(" € TTC")
        formStock.addRow("Chrono Relais — tarif", self.tarifChronoRelais)

        self.seuilChronoRelais = QDoubleSpinBox()
        self.seuilChronoRelais.setDecimals(0)
        self.seuilChronoRelais.setSuffix(" €")
        formStock.addRow(
            "Chrono Relais — offert dès", self.seuilChronoRelais
        )

        layout.addWidget(groupeStock)

        self.btnEnregistrer = QPushButton("💾 Enregistrer")
        self.btnEnregistrer.clicked.connect(self.enregistrer)
        layout.addWidget(self.btnEnregistrer)

        layout.addStretch()

        self.charger()

    def charger(self):

        reglages = GenerateurFicheHtml.reglages_globaux()

        self.prixEmballageCadeau.setValue(
            reglages["prix_emballage_cadeau"]
        )
        self.seuilLivraisonStock.setValue(
            reglages["seuil_livraison_gratuite_stock"]
        )
        self.tarifLivraisonDf.setValue(
            reglages["tarif_livraison_df"]
        )
        self.seuilLivraisonDf.setValue(
            reglages["seuil_livraison_gratuite_df"]
        )
        self.tarifMondialRelay.setValue(reglages["tarif_mondial_relay"])
        self.seuilMondialRelay.setValue(reglages["seuil_mondial_relay"])
        self.tarifColissimo.setValue(reglages["tarif_colissimo"])
        self.seuilColissimo.setValue(reglages["seuil_colissimo"])
        self.tarifChronoRelais.setValue(reglages["tarif_chrono_relais"])
        self.seuilChronoRelais.setValue(reglages["seuil_chrono_relais"])

    def enregistrer(self):

        self.manager.definir(
            "prix_emballage_cadeau", self.prixEmballageCadeau.value()
        )
        self.manager.definir(
            "seuil_livraison_gratuite_stock",
            self.seuilLivraisonStock.value()
        )
        self.manager.definir(
            "tarif_livraison_df", self.tarifLivraisonDf.value()
        )
        self.manager.definir(
            "seuil_livraison_gratuite_df", self.seuilLivraisonDf.value()
        )
        self.manager.definir(
            "tarif_mondial_relay", self.tarifMondialRelay.value()
        )
        self.manager.definir(
            "seuil_mondial_relay", self.seuilMondialRelay.value()
        )
        self.manager.definir(
            "tarif_colissimo", self.tarifColissimo.value()
        )
        self.manager.definir(
            "seuil_colissimo", self.seuilColissimo.value()
        )
        self.manager.definir(
            "tarif_chrono_relais", self.tarifChronoRelais.value()
        )
        self.manager.definir(
            "seuil_chrono_relais", self.seuilChronoRelais.value()
        )

        QMessageBox.information(
            self, "Enregistré",
            "Ces réglages s'appliquent aux prochaines fiches générées."
        )