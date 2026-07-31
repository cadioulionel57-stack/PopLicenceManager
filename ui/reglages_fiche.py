from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
        self.prixEmballageCadeau.setMaximum(9999)
        self.prixEmballageCadeau.setDecimals(2)
        self.prixEmballageCadeau.setSuffix(" € TTC")
        form.addRow(
            "Prix emballage cadeau", self.prixEmballageCadeau
        )

        self.seuilLivraisonStock = QDoubleSpinBox()
        self.seuilLivraisonStock.setMaximum(9999)
        self.seuilLivraisonStock.setDecimals(0)
        self.seuilLivraisonStock.setSuffix(" €")
        form.addRow(
            "Seuil livraison gratuite (Stock, référence)",
            self.seuilLivraisonStock
        )

        self.tarifLivraisonDf = QDoubleSpinBox()
        self.tarifLivraisonDf.setMaximum(9999)
        self.tarifLivraisonDf.setDecimals(2)
        self.tarifLivraisonDf.setSuffix(" € TTC")
        form.addRow(
            "Tarif livraison (Direct Fournisseur)", self.tarifLivraisonDf
        )

        self.seuilLivraisonDf = QDoubleSpinBox()
        self.seuilLivraisonDf.setMaximum(9999)
        self.seuilLivraisonDf.setDecimals(0)
        self.seuilLivraisonDf.setSuffix(" €")
        form.addRow(
            "Seuil livraison gratuite (DF)", self.seuilLivraisonDf
        )

        # Ce que le FOURNISSEUR te facture, pas ce que tu
        # factures au client. Ce montant ne s'affiche nulle
        # part sur la boutique : il entre dans le coût de
        # revient des produits Direct Fournisseur, pour que
        # le prix de vente calculé le couvre déjà.
        self.coutPortDf = QDoubleSpinBox()
        self.coutPortDf.setMaximum(9999)
        self.coutPortDf.setDecimals(2)
        self.coutPortDf.setSuffix(" € HT")
        form.addRow(
            "Coût de port Direct Fournisseur (facturé par le "
            "fournisseur)", self.coutPortDf
        )

        noteCoutPortDf = QLabel(
            "Ce montant est celui que ton fournisseur te "
            "facture par article expédié. Il n'apparaît jamais "
            "sur ta boutique : le moteur l'ajoute au coût de "
            "revient de chaque produit Direct Fournisseur avant "
            "de calculer ta marge.\n"
            "Tu peux ainsi mettre le tarif de livraison DF "
            "ci-dessus à 0 € et annoncer la livraison offerte : "
            "le port est déjà couvert par le prix de vente."
        )
        noteCoutPortDf.setWordWrap(True)
        noteCoutPortDf.setStyleSheet("color:#64748b; font-size:12px;")
        form.addRow("", noteCoutPortDf)

        layout.addWidget(groupe)

        groupeStock = QGroupBox("🚚 Transporteurs — Produits en stock")
        formStock = QFormLayout(groupeStock)

        self.tarifMondialRelay = QDoubleSpinBox()
        self.tarifMondialRelay.setMaximum(9999)
        self.tarifMondialRelay.setDecimals(2)
        self.tarifMondialRelay.setSuffix(" € TTC")
        formStock.addRow(
            "Mondial Relay Point Relais — tarif",
            self.tarifMondialRelay
        )

        self.seuilMondialRelay = QDoubleSpinBox()
        self.seuilMondialRelay.setMaximum(9999)
        self.seuilMondialRelay.setDecimals(0)
        self.seuilMondialRelay.setSuffix(" €")
        formStock.addRow(
            "Mondial Relay Point Relais — offert dès",
            self.seuilMondialRelay
        )

        # La clé en base reste "tarif_colissimo" : la
        # renommer casserait la variable {{tarif_colissimo}}
        # présente dans tous les modèles de fiche. Seule
        # l'étiquette affichée change, pour suivre le
        # changement de transporteur.
        self.tarifColissimo = QDoubleSpinBox()
        self.tarifColissimo.setMaximum(9999)
        self.tarifColissimo.setDecimals(2)
        self.tarifColissimo.setSuffix(" € TTC")
        formStock.addRow(
            "Mondial Relay Domicile — tarif", self.tarifColissimo
        )

        self.seuilColissimo = QDoubleSpinBox()
        self.seuilColissimo.setMaximum(9999)
        self.seuilColissimo.setDecimals(0)
        self.seuilColissimo.setSuffix(" €")
        formStock.addRow(
            "Mondial Relay Domicile — offert dès",
            self.seuilColissimo
        )

        self.tarifChronoRelais = QDoubleSpinBox()
        self.tarifChronoRelais.setMaximum(9999)
        self.tarifChronoRelais.setDecimals(2)
        self.tarifChronoRelais.setSuffix(" € TTC")
        formStock.addRow("Chrono Relais — tarif", self.tarifChronoRelais)

        self.seuilChronoRelais = QDoubleSpinBox()
        self.seuilChronoRelais.setMaximum(9999)
        self.seuilChronoRelais.setDecimals(0)
        self.seuilChronoRelais.setSuffix(" €")
        formStock.addRow(
            "Chrono Relais — offert dès", self.seuilChronoRelais
        )

        layout.addWidget(groupeStock)

        ####################################################
        # Option emballage cadeau proposée au client
        ####################################################

        groupeCadeau = QGroupBox(
            "🎁 Option emballage cadeau proposée au client"
        )
        formCadeau = QFormLayout(groupeCadeau)

        self.libelleCadeauOui = QLineEdit()
        self.libelleCadeauOui.textChanged.connect(self._majApercu)
        formCadeau.addRow(
            "Libellé du choix", self.libelleCadeauOui
        )

        self.libelleCadeauNon = QLineEdit()
        self.libelleCadeauNon.textChanged.connect(self._majApercu)
        formCadeau.addRow(
            "Libellé du refus", self.libelleCadeauNon
        )

        self.prixEmballageCadeau.valueChanged.connect(
            self._majApercu
        )

        self.apercuCadeau = QLabel()
        self.apercuCadeau.setWordWrap(True)
        self.apercuCadeau.setStyleSheet(
            "background:#f7f9fc; border:1px solid #dbe3ee;"
            "border-radius:8px; padding:12px; color:#1c2b3a;"
        )
        formCadeau.addRow("Ce que verra le client", self.apercuCadeau)

        noteCadeau = QLabel(
            "Le prix vient du réglage « Prix emballage cadeau » "
            "ci-dessus — il n'y a qu'un seul endroit où le "
            "changer.\n"
            "Le refus est toujours coché par défaut : on "
            "n'impose jamais une option payante, c'est aussi "
            "ce qu'exige la loi."
        )
        noteCadeau.setWordWrap(True)
        noteCadeau.setStyleSheet("color:#64748b; font-size:12px;")
        formCadeau.addRow("", noteCadeau)

        layout.addWidget(groupeCadeau)

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
        self.coutPortDf.setValue(
            self.manager.obtenir_nombre("cout_port_df_ht", 0)
        )
        self.tarifMondialRelay.setValue(reglages["tarif_mondial_relay"])
        self.seuilMondialRelay.setValue(reglages["seuil_mondial_relay"])
        self.tarifColissimo.setValue(reglages["tarif_colissimo"])
        self.seuilColissimo.setValue(reglages["seuil_colissimo"])
        self.tarifChronoRelais.setValue(reglages["tarif_chrono_relais"])
        self.seuilChronoRelais.setValue(reglages["seuil_chrono_relais"])

        self.libelleCadeauOui.setText(
            self.manager.obtenir(
                "libelle_cadeau_oui",
                "🎁 Je souhaite un emballage cadeau"
            )
        )
        self.libelleCadeauNon.setText(
            self.manager.obtenir("libelle_cadeau_non", "Non, merci.")
        )

        self._majApercu()

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
            "cout_port_df_ht",
            self.coutPortDf.value(),
            "Coût de port HT facturé par le fournisseur sur "
            "chaque article Direct Fournisseur. Ajouté au coût "
            "de revient avant calcul de la marge."
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

        self.manager.definir(
            "libelle_cadeau_oui",
            self.libelleCadeauOui.text().strip()
            or "🎁 Je souhaite un emballage cadeau",
            "Libellé du choix d'emballage cadeau proposé au "
            "client sur la fiche WiziShop."
        )
        self.manager.definir(
            "libelle_cadeau_non",
            self.libelleCadeauNon.text().strip() or "Non, merci.",
            "Libellé du refus d'emballage cadeau. Toujours "
            "sélectionné par défaut."
        )

        QMessageBox.information(
            self, "Enregistré",
            "Ces réglages s'appliquent aux prochaines fiches générées."
        )

    def _majApercu(self):
        """
        Montre exactement ce que le client verra sur la fiche
        produit, prix compris — un supplément découvert à
        l'étape suivante fait abandonner la commande.
        """

        oui = (
            self.libelleCadeauOui.text().strip()
            or "🎁 Je souhaite un emballage cadeau"
        )
        non = self.libelleCadeauNon.text().strip() or "Non, merci."

        prix = self.prixEmballageCadeau.value()
        montant = f"{prix:.2f}".replace(".", ",")

        self.apercuCadeau.setText(
            f"○   {oui} (+{montant} € TTC)\n"
            f"◉   {non}"
        )