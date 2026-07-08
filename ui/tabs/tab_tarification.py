from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from modules.canal_manager import CanalManager
from modules.moteur_prix import MoteurPrix
from modules.parametre_manager import ParametreManager


class TarificationTab(QWidget):
    """
    Calcule et affiche, canal par canal, le prix de vente
    du produit (méthode marge de contribution), le seuil
    de rentabilité, et une comparaison avec le prix de
    marché constaté pour indiquer si le canal est viable.

    La marge peut être différente sur chaque canal (ex :
    40% visés sur le site, 20% acceptés sur une marketplace
    pour rester compétitif) : la "marge par défaut" en haut
    de l'onglet s'applique partout sauf si tu modifies la
    marge directement dans la ligne d'un canal précis.
    """

    def __init__(self, type_produit=None):

        super().__init__()

        self.type_produit = type_produit
        self.moteur = MoteurPrix()
        self.parametres = ParametreManager()

        layout = QVBoxLayout(self)

        ####################################################
        # Marge par défaut
        ####################################################

        margeGroupe = QGroupBox("🎯 Marge par défaut")

        formMarge = QFormLayout(margeGroupe)

        self.margeVisee = QDoubleSpinBox()
        self.margeVisee.setDecimals(1)
        self.margeVisee.setMaximum(95)
        self.margeVisee.setSuffix(" %")
        self.margeVisee.setValue(30)

        formMarge.addRow(
            "Marge par défaut (utilisée si aucune marge "
            "spécifique n'est définie sur un canal)",
            self.margeVisee
        )

        layout.addWidget(margeGroupe)

        ####################################################
        # Seuil transport maximum (réglable, pas figé)
        ####################################################

        seuilGroupe = QGroupBox("⚙️ Réglage de la décision automatique")

        formSeuil = QFormLayout(seuilGroupe)

        self.seuilTransport = QDoubleSpinBox()
        self.seuilTransport.setDecimals(0)
        self.seuilTransport.setMaximum(100)
        self.seuilTransport.setSuffix(" %")
        self.seuilTransport.setValue(
            self.parametres.obtenir_nombre(
                MoteurPrix.CLE_SEUIL_TRANSPORT,
                MoteurPrix.SEUIL_TRANSPORT_DEFAUT
            )
        )
        self.seuilTransport.valueChanged.connect(
            self._sauvegarderSeuilTransport
        )

        formSeuil.addRow(
            "Transport max toléré (% du prix de vente)",
            self.seuilTransport
        )

        layout.addWidget(seuilGroupe)

        ####################################################
        # Tableau des canaux
        ####################################################

        canauxGroupe = QGroupBox("💰 Prix par canal de vente")

        layoutCanaux = QVBoxLayout(canauxGroupe)

        self.btnCalculer = QPushButton("🔄 Calculer les prix")
        layoutCanaux.addWidget(self.btnCalculer)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Canal",
            "Marge (%)",
            "Gain net (€)",
            "Prix calculé TTC",
            "Seuil rentable TTC",
            "Prix marché constaté",
            "Décision",
            "Détail",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.setMinimumHeight(300)

        layoutCanaux.addWidget(self.table)

        layout.addWidget(canauxGroupe)

        self.btnCalculer.clicked.connect(self.calculer)
        self.table.cellDoubleClicked.connect(self._afficherDetail)

        # {canal_id: QDoubleSpinBox de la marge de ce canal}
        self.champsMarge = {}

        # {canal_id: QDoubleSpinBox du prix marché}
        self.champsPrixMarche = {}

        # {canal_id: dernier résultat de calcul}
        self.derniersResultats = {}

        # {numéro de ligne du tableau: canal_id}
        self.ligneVersCanal = {}

        # {canal_id: marge spécifique déjà enregistrée}
        # (préremplie par charger(), voir plus bas)
        self._marges_existantes = {}

    def _canaux_compatibles(self):
        """
        Ne montre que les canaux compatibles avec le type
        de produit (même règle que l'onglet Publication :
        les marketplaces ne sont proposées qu'aux produits
        de type "stock").
        """

        canaux = CanalManager().tous()

        return [
            c for c in canaux
            if c["type"] != "marketplace" or self.type_produit == "stock"
        ]

    def _sauvegarderSeuilTransport(self, valeur):

        self.parametres.definir(
            MoteurPrix.CLE_SEUIL_TRANSPORT,
            valeur,
            "Pourcentage maximum du prix de vente que le "
            "transport peut représenter avant qu'un produit "
            "soit signalé non recommandé sur un canal."
        )

    def calculer(self):

        canaux = self._canaux_compatibles()

        self.table.setRowCount(0)
        self.champsMarge = {}
        self.champsPrixMarche = {}
        self.derniersResultats = {}
        self.ligneVersCanal = {}

        for ligne, canal in enumerate(canaux):

            self.table.insertRow(ligne)

            self.ligneVersCanal[ligne] = canal["id"]

            self.table.setItem(
                ligne, 0, QTableWidgetItem(canal["nom"])
            )

            # Champ marge, propre à ce canal
            champMarge = QDoubleSpinBox()
            champMarge.setDecimals(1)
            champMarge.setMaximum(95)
            champMarge.setSuffix(" %")
            champMarge.setValue(
                self._marges_existantes.get(
                    canal["id"], self.margeVisee.value()
                )
            )
            champMarge.valueChanged.connect(
                lambda _, l=ligne: self._recalculerLigne(l)
            )

            self.champsMarge[canal["id"]] = champMarge
            self.table.setCellWidget(ligne, 1, champMarge)

            # Champ prix marché, propre à ce canal
            champPrixMarche = QDoubleSpinBox()
            champPrixMarche.setDecimals(2)
            champPrixMarche.setMaximum(99999)
            champPrixMarche.setSuffix(" €")
            champPrixMarche.valueChanged.connect(
                lambda _, l=ligne: self._actualiserDecision(l)
            )

            self.champsPrixMarche[canal["id"]] = champPrixMarche
            self.table.setCellWidget(ligne, 5, champPrixMarche)

            self._recalculerLigne(ligne)

    def _recalculerLigne(self, ligne):
        """
        Recalcule uniquement la ligne concernée, avec sa
        propre marge (celle du canal, ou la marge par
        défaut si non modifiée).
        """

        canal_id = self.ligneVersCanal.get(ligne)

        if canal_id is None:
            return

        champMarge = self.champsMarge.get(canal_id)

        marge = (
            champMarge.value()
            if champMarge is not None
            else self.margeVisee.value()
        )

        produit = {
            "prix_fournisseur_ht": self._prix_achat_ht(),
            "famille_produit_id": self._famille_produit_id(),
            "marge_visee_pourcentage": marge,
            "poids": self._poids(),
            "longueur": self._longueur(),
            "largeur": self._largeur(),
            "hauteur": self._hauteur(),
            "longueur_expedition": self._longueur_expedition(),
            "largeur_expedition": self._largeur_expedition(),
            "hauteur_expedition": self._hauteur_expedition(),
        }

        categorie_id = self._categorie_pour_canal(canal_id)

        resultat = self.moteur.calculer(produit, canal_id, categorie_id)

        self.derniersResultats[canal_id] = resultat

        if resultat["erreur"]:

            self.table.setItem(ligne, 2, QTableWidgetItem("—"))
            self.table.setItem(ligne, 3, QTableWidgetItem("—"))
            self.table.setItem(ligne, 4, QTableWidgetItem("—"))

            itemErreur = QTableWidgetItem(resultat["erreur"])
            itemErreur.setForeground(QColor("#c0392b"))
            self.table.setItem(ligne, 7, itemErreur)

            self.table.setItem(ligne, 6, QTableWidgetItem(""))

            return

        # Gain net en euros : la marge visée appliquée au
        # prix de vente HT (ce qu'il te reste réellement,
        # pas juste le pourcentage abstrait).
        gain_net_ht = resultat["prix_vente_ht"] * (marge / 100)

        self.table.setItem(
            ligne, 2,
            QTableWidgetItem(f"{gain_net_ht:.2f} €")
        )

        self.table.setItem(
            ligne, 3,
            QTableWidgetItem(f"{resultat['prix_vente_ttc']:.2f} €")
        )

        seuil = self.moteur.seuil_rentable(produit, canal_id, categorie_id)

        seuil_ttc = (
            seuil["prix_vente_ttc"] if not seuil["erreur"] else None
        )

        self.table.setItem(
            ligne, 4,
            QTableWidgetItem(
                f"{seuil_ttc:.2f} €" if seuil_ttc else "—"
            )
        )

        itemDecision = QTableWidgetItem(resultat["decision"])

        if resultat["decision"].startswith("❌"):
            itemDecision.setForeground(QColor("#c0392b"))
        else:
            itemDecision.setForeground(QColor("#1e7d32"))

        self.table.setItem(ligne, 6, itemDecision)

        detail = ""

        if resultat["ratio_transport_pourcentage"] is not None:
            detail = (
                f"Transport : {resultat['ratio_transport_pourcentage']}% "
                "du prix de vente HT"
            )

        self.table.setItem(ligne, 7, QTableWidgetItem(detail))

        # Si un prix marché est déjà saisi sur cette ligne,
        # on met à jour la décision en conséquence.
        self._actualiserDecision(ligne)

    def _actualiserDecision(self, ligne):

        canal_id = self.ligneVersCanal.get(ligne)

        if canal_id is None:
            return

        resultat = self.derniersResultats.get(canal_id)

        if resultat is None or resultat["erreur"]:
            return

        champ = self.champsPrixMarche.get(canal_id)

        if champ is None:
            return

        prix_marche = champ.value()

        # La décision automatique (ratio transport) reste
        # prioritaire : si elle est négative, ça ne change
        # jamais, quel que soit le prix marché constaté.
        if resultat["decision"].startswith("❌"):

            itemDecision = QTableWidgetItem(resultat["decision"])
            itemDecision.setForeground(QColor("#c0392b"))
            self.table.setItem(ligne, 6, itemDecision)
            return

        itemDecision = QTableWidgetItem()

        if prix_marche <= 0:

            itemDecision.setText(resultat["decision"])
            itemDecision.setForeground(QColor("#1e7d32"))

        elif prix_marche >= resultat["prix_vente_ttc"]:

            itemDecision.setText("✅ Recommandé (vs marché)")
            itemDecision.setForeground(QColor("#1e7d32"))

        else:

            itemDecision.setText("⚠️ Prix marché trop bas")
            itemDecision.setForeground(QColor("#e67e22"))

        self.table.setItem(ligne, 6, itemDecision)

    def _afficherDetail(self, ligne, colonne):

        canal_id = self.ligneVersCanal.get(ligne)

        if canal_id is None:
            return

        resultat = self.derniersResultats.get(canal_id)

        if resultat is None:
            return

        nom_canal = self.table.item(ligne, 0).text()

        if resultat["erreur"]:

            QMessageBox.information(
                self,
                f"Détail du calcul — {nom_canal}",
                resultat["erreur"]
            )
            return

        lignes_detail = [
            f"Coût produit (achat + emballage + provision retour) : "
            f"{resultat['cout_produit']:.2f} € HT",
        ]

        if resultat["transport"]:

            transport_ht = resultat["transport"]["prix_ht"]
            reste_frais_fixe = (
                resultat["cout_fixe_total"]
                - resultat["cout_produit"]
                - transport_ht
            )

            lignes_detail.append(
                f"+ Frais fixes du canal : {reste_frais_fixe:.2f} € HT"
            )
            lignes_detail.append(
                f"+ Transport ({resultat['transport']['transporteur']} — "
                f"{resultat['transport']['offre']}) : "
                f"{transport_ht:.2f} € HT"
            )

        else:

            reste_frais_fixe = (
                resultat["cout_fixe_total"] - resultat["cout_produit"]
            )
            lignes_detail.append(
                f"+ Frais fixes du canal : {reste_frais_fixe:.2f} € HT"
            )
            lignes_detail.append(
                "+ Transport : non inclus dans le prix "
                "(payé séparément par le client)"
            )

        lignes_detail.append(
            f"= Coût direct total : {resultat['cout_fixe_total']:.2f} € HT"
        )
        lignes_detail.append("")
        lignes_detail.append(
            f"Marge visée : {resultat['marge_pourcentage']:.1f} %"
        )
        lignes_detail.append(
            f"Commission de vente : {resultat['commission_pourcentage']:.1f} %"
        )

        if resultat["taux_paiement_pourcentage"]:
            lignes_detail.append(
                f"Frais de paiement : "
                f"{resultat['taux_paiement_pourcentage']:.1f} %"
            )

        if resultat["taux_tsn_effectif"]:
            lignes_detail.append(
                f"TSN effective : {resultat['taux_tsn_effectif']:.2f} %"
            )

        lignes_detail.append("")
        lignes_detail.append(
            f"Prix de vente HT : {resultat['prix_vente_ht']:.2f} €"
        )
        lignes_detail.append(
            f"Prix de vente TTC (TVA 20%) : "
            f"{resultat['prix_vente_ttc']:.2f} €"
        )

        if resultat["ratio_transport_pourcentage"] is not None:
            lignes_detail.append("")
            lignes_detail.append(
                f"Le transport représente "
                f"{resultat['ratio_transport_pourcentage']}% "
                "du prix de vente HT."
            )

        QMessageBox.information(
            self,
            f"Détail du calcul — {nom_canal}",
            "\n".join(lignes_detail)
        )

    def marges_saisies(self):
        """
        Renvoie {canal_id: marge_pourcentage} pour tous les
        canaux dont la marge diffère de la marge par défaut
        (donc à enregistrer comme marge spécifique).
        """

        resultat = {}

        for canal_id, champ in self.champsMarge.items():

            if champ.value() != self.margeVisee.value():
                resultat[canal_id] = champ.value()

        return resultat

    # ------------------------------------------------------
    # Méthodes à relier aux autres onglets de la fiche
    # produit (Général / Caractéristiques). Le dialogue
    # parent les redéfinit pour pointer vers les vrais
    # champs — voir product_dialog_v2.py.
    # ------------------------------------------------------

    def _prix_achat_ht(self):
        return 0

    def _famille_produit_id(self):
        return None

    def _poids(self):
        return 0

    def _longueur(self):
        return 0

    def _largeur(self):
        return 0

    def _hauteur(self):
        return 0

    def _longueur_expedition(self):
        return 0

    def _largeur_expedition(self):
        return 0

    def _hauteur_expedition(self):
        return 0

    def _categorie_pour_canal(self, canal_id):
        return None

    def charger(self, produit, categories_canaux=None, marche=None, marges=None):
        """
        Pré-remplit l'onglet à partir d'un produit existant
        (mode modification).
        """

        if produit["marge_visee_pourcentage"] is not None:
            self.margeVisee.setValue(produit["marge_visee_pourcentage"])

        self._marges_existantes = marges or {}

        self.calculer()

        if marche:

            for canal_id, prix in marche.items():

                champ = self.champsPrixMarche.get(canal_id)

                if champ is not None and prix is not None:
                    champ.setValue(prix)