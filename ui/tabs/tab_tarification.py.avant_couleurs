from PySide6.QtWidgets import (
    QScrollArea,
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
from PySide6.QtGui import QColor, QFont

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

        # Pas de zone de défilement ici, volontairement : le
        # tableau de résultats gère déjà son propre défilement
        # nativement — l'envelopper cassait sa largeur (les
        # champs marge/prix marché s'écrasaient en bandes
        # minuscules).
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
        # Largeurs adaptées au contenu : les colonnes de
        # chiffres n'ont pas besoin de la même place que la
        # décision ou le détail, qui sont du texte. Tout
        # étirer à l'identique coupait « CANAL NON RECOMMANDÉ »
        # et les explications de transport.
        entete = self.table.horizontalHeader()

        entete.setSectionResizeMode(0, QHeaderView.Fixed)   # Canal
        entete.setSectionResizeMode(1, QHeaderView.Fixed)   # Marge
        entete.setSectionResizeMode(2, QHeaderView.Fixed)   # Gain net
        entete.setSectionResizeMode(3, QHeaderView.Fixed)   # Prix TTC
        entete.setSectionResizeMode(4, QHeaderView.Fixed)   # Seuil
        entete.setSectionResizeMode(5, QHeaderView.Fixed)   # Prix marché
        entete.setSectionResizeMode(6, QHeaderView.Fixed)   # Décision
        entete.setSectionResizeMode(7, QHeaderView.Stretch)  # Détail

        self.table.setColumnWidth(0, 165)
        self.table.setColumnWidth(1, 105)
        self.table.setColumnWidth(2, 105)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 140)
        self.table.setColumnWidth(5, 150)
        self.table.setColumnWidth(6, 235)

        # Un mot coupé n'apprend rien : on montre la fin du
        # texte plutôt que de le tronquer au milieu, et
        # l'infobulle donne toujours la phrase entière.
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.ElideRight)

        # Pas de colonne de numéros : c'est le nom du canal
        # qui identifie la ligne. Elle est masquée partout
        # ailleurs dans le logiciel, et c'était elle qui se
        # faisait rogner en bas du tableau.
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setMinimumHeight(300)

        # Le tableau ne doit JAMAIS défiler à l'intérieur :
        # on risquerait d'oublier un canal de vente au
        # moment de fixer les prix. Sa hauteur est donc
        # recalculée sur son contenu après chaque
        # remplissage (voir _ajusterHauteur).
        self.table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

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

        # {canal_id: texte de détail "de base", sans la
        # note de comparaison croisée, pour ne jamais
        # dupliquer cette note en cas de recalcul répété}
        self.detailsBase = {}

        # {numéro de ligne du tableau: canal_id}
        self.ligneVersCanal = {}

        # {canal_id: marge spécifique déjà enregistrée}
        # (préremplie par charger(), voir plus bas)
        self._marges_existantes = {}
        self._marche_existant = {}

    def _couleurLisible(self, couleur):
        """
        Assombrit une couleur jusqu'à ce qu'elle soit lisible
        sur fond blanc.

        Les couleurs de marque des canaux sont faites pour des
        logos, pas pour du texte : l'orange d'Amazon et le
        jaune de la Fnac tombent à un contraste de 2 sur 21,
        très en dessous du minimum lisible de 4,5. On garde
        la teinte, on descend juste la luminosité.
        """

        couleur = (couleur or "#144b8b").lstrip("#")

        if len(couleur) != 6:
            couleur = "144b8b"

        composantes = [
            int(couleur[i:i + 2], 16) for i in (0, 2, 4)
        ]

        def contraste(rvb):

            canaux = []

            for valeur in rvb:
                v = valeur / 255
                canaux.append(
                    v / 12.92 if v <= 0.03928
                    else ((v + 0.055) / 1.055) ** 2.4
                )

            luminance = (
                0.2126 * canaux[0]
                + 0.7152 * canaux[1]
                + 0.0722 * canaux[2]
            )

            return 1.05 / (luminance + 0.05)

        # 12 passes suffisent largement pour atteindre 4,5
        # depuis n'importe quelle couleur claire.
        for _ in range(12):

            if contraste(composantes) >= 4.5:
                break

            composantes = [int(c * 0.85) for c in composantes]

        return "#%02x%02x%02x" % tuple(composantes)

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

    def _ajusterHauteur(self):
        """
        Donne au tableau exactement la hauteur de son contenu,
        pour que tous les canaux de vente soient visibles d'un
        seul coup d'œil, sans défilement interne.
        """

        lignes = self.table.rowCount()

        # Hauteur réelle de chaque ligne plutôt qu'une valeur
        # théorique : c'est la seule mesure fiable, une ligne
        # pouvant être plus haute que la valeur par défaut.
        hauteur_lignes = sum(
            self.table.rowHeight(l) for l in range(lignes)
        )

        entete = self.table.horizontalHeader()

        hauteur_entete = max(
            entete.height(), entete.sizeHint().height()
        )

        # Bordures du cadre, plus la place de la barre de
        # défilement horizontale : sans elle, elle vient
        # manger le bas du tableau et la dernière ligne se
        # retrouve tronquée.
        cadre = 2 * self.table.frameWidth()

        barre_horizontale = (
            self.table.horizontalScrollBar().sizeHint().height()
        )

        hauteur = (
            hauteur_entete
            + hauteur_lignes
            + cadre
            + barre_horizontale
            + 4
        )

        self.table.setMinimumHeight(max(120, hauteur))
        self.table.setMaximumHeight(max(120, hauteur))

    def calculer(self):

        # Mémorise les prix marché actuellement saisis avant
        # de reconstruire le tableau — sinon une modification
        # manuelle suivie d'un "Calculer les prix" perdait la
        # saisie (et l'ancienne valeur restait seule en base
        # à l'enregistrement, sans que l'utilisateur s'en
        # rende compte).
        # Mémorise les marges par canal actuellement saisies
        # avant de reconstruire le tableau — même bug que
        # pour le prix marché : sans ça, une marge modifiée
        # à la main puis suivie d'un "Calculer les prix"
        # perdait la saisie et retombait sur la marge par
        # défaut, silencieusement.
        for canal_id, champ in self.champsMarge.items():

            if champ.value() != self.margeVisee.value():
                self._marges_existantes[canal_id] = champ.value()

        for canal_id, champ in self.champsPrixMarche.items():

            if champ.value() > 0:
                self._marche_existant[canal_id] = champ.value()

        canaux = self._canaux_compatibles()

        self._derniersCanaux = canaux

        self.table.setRowCount(0)
        self.champsMarge = {}
        self.champsPrixMarche = {}
        self.derniersResultats = {}
        self.ligneVersCanal = {}
        self.detailsBase = {}

        for ligne, canal in enumerate(canaux):

            self.table.insertRow(ligne)

            self.ligneVersCanal[ligne] = canal["id"]

            itemCanal = QTableWidgetItem(canal["nom"])

            couleurCanal = QColor(
                self._couleurLisible(canal["couleur"])
            )
            itemCanal.setForeground(couleurCanal)

            policeCanal = QFont()
            policeCanal.setBold(True)
            itemCanal.setFont(policeCanal)

            self.table.setItem(ligne, 0, itemCanal)

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
            champPrixMarche.setValue(
                self._marche_existant.get(canal["id"]) or 0
            )
            champPrixMarche.valueChanged.connect(
                lambda _, l=ligne: self._actualiserDecision(l)
            )

            self.champsPrixMarche[canal["id"]] = champPrixMarche
            self.table.setCellWidget(ligne, 5, champPrixMarche)

            self._recalculerLigne(ligne)

        self._comparerCanauxSimilaires(canaux)

        # Tous les canaux visibles d'un coup, sans défilement
        # interne : c'est ici qu'on fixe la hauteur du tableau
        # sur son contenu réel.
        self._ajusterHauteur()

    def _comparerCanauxSimilaires(self, canaux):
        """
        Compare les canaux qui semblent être la même
        marketplace sous différentes formes (ex : "Amazon
        FBA" et "Amazon FBM" partagent le mot "Amazon"),
        et signale dans la colonne Détail lequel est le
        plus avantageux, pour que la comparaison n'ait pas
        besoin d'être faite à la main.
        """

        # Regroupe les canaux par mot commun dans leur nom
        # (ex : tous les noms contenant "Amazon" ensemble).
        groupes = {}

        for canal in canaux:

            resultat = self.derniersResultats.get(canal["id"])

            if resultat is None or resultat["erreur"]:
                continue

            for mot in canal["nom"].split():

                if len(mot) < 4:
                    continue

                groupes.setdefault(mot, []).append({
                    "canal_id": canal["id"],
                    "nom": canal["nom"],
                    "prix_ttc": resultat["prix_vente_ttc"],
                    "utilise_grille_fba": bool(
                        canal["utilise_grille_fba"]
                    ),
                })

        for mot, membres in groupes.items():

            if len(membres) < 2:
                continue

            moins_cher = min(membres, key=lambda m: m["prix_ttc"])

            for membre in membres:

                if membre["canal_id"] == moins_cher["canal_id"]:
                    continue

                ligne = next(
                    (
                        l for l, cid in self.ligneVersCanal.items()
                        if cid == membre["canal_id"]
                    ),
                    None
                )

                if ligne is None:
                    continue

                ecart = membre["prix_ttc"] - moins_cher["prix_ttc"]

                note = (
                    f"💡 {moins_cher['nom']} moins cher de "
                    f"{ecart:.2f}€ pour le même type de vente"
                )

                base = self.detailsBase.get(membre["canal_id"], "")

                texteFinal = f"{base} — {note}" if base else note

                self.table.setItem(
                    ligne, 7, QTableWidgetItem(texteFinal)
                )

                # Cas spécifique FBA plus cher que FBM : pas
                # juste une note discrète en colonne Détail,
                # une vraie alerte visible en colonne Décision
                # — c'est l'info la plus utile pour savoir si
                # ce produit a intérêt à passer en FBA.
                if membre.get("utilise_grille_fba"):

                    itemDecision = QTableWidgetItem(
                        f"⚠️ FBA plus cher que FBM (+{ecart:.2f}€)"
                    )
                    self._appliquerStyleAlerte(itemDecision, "attention")
                    self.table.setItem(ligne, 6, itemDecision)

    def _appliquerStyleAlerte(self, item, niveau):
        """
        Applique un style "badge" fort à une cellule de
        décision : fond plein et saturé + texte blanc en
        gras — pas un simple fond pastel avec texte coloré,
        trop discret pour se remarquer d'un coup d'œil dans
        un tableau dense.

        niveau : "erreur" (rouge, canal non recommandé ou
        décision bloquante), "attention" (orange, comparaison
        défavorable mais pas rédhibitoire), "ok" (vert).
        """

        police = QFont()
        police.setBold(True)
        police.setPointSize(police.pointSize() + 1)
        item.setFont(police)

        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(QColor("#ffffff"))

        if niveau == "erreur":
            item.setBackground(QColor("#e74c3c"))
        elif niveau == "attention":
            item.setBackground(QColor("#f39c12"))
        else:
            item.setBackground(QColor("#27ae60"))

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
            # Sans le type, le moteur ne peut pas savoir qu'il
            # s'agit d'un produit Direct Fournisseur, et le
            # port facturé par le fournisseur n'entre jamais
            # dans le coût de revient.
            "type_produit": self.type_produit,
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
            "emballage_id": self._emballage_id(),
        }

        categorie_id = self._categorie_pour_canal(canal_id)

        resultat = self.moteur.calculer(produit, canal_id, categorie_id)

        self.derniersResultats[canal_id] = resultat

        if resultat["erreur"]:

            self.table.setItem(ligne, 2, QTableWidgetItem("—"))
            self.table.setItem(ligne, 3, QTableWidgetItem("—"))
            self.table.setItem(ligne, 4, QTableWidgetItem("—"))

            itemDecision = QTableWidgetItem("🚫 CANAL NON RECOMMANDÉ")
            self._appliquerStyleAlerte(itemDecision, "erreur")
            self.table.setItem(ligne, 6, itemDecision)

            itemDetail = QTableWidgetItem(resultat["erreur"])
            itemDetail.setToolTip(resultat["erreur"])
            itemDetail.setForeground(QColor("#c0392b"))
            self.table.setItem(ligne, 7, itemDetail)

            return

        # Gain net en euros : la marge visée appliquée au
        # prix de vente HT (ce qu'il te reste réellement,
        # pas juste le pourcentage abstrait).
        gain_net_ht = resultat["prix_vente_ht"] * (marge / 100)

        itemGainNet = QTableWidgetItem(f"{gain_net_ht:.2f} €")
        itemGainNet.setForeground(QColor("#1e7d32"))

        policeGainNet = QFont()
        policeGainNet.setBold(True)
        itemGainNet.setFont(policeGainNet)

        self.table.setItem(ligne, 2, itemGainNet)

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
        itemDecision.setToolTip(resultat["decision"])

        if resultat["decision"].startswith("❌"):
            self._appliquerStyleAlerte(itemDecision, "erreur")
        elif resultat["decision"].startswith("⚠️"):
            self._appliquerStyleAlerte(itemDecision, "attention")
        else:
            self._appliquerStyleAlerte(itemDecision, "ok")

        self.table.setItem(ligne, 6, itemDecision)

        detail = ""

        if resultat["ratio_transport_pourcentage"] is not None:
            detail = (
                f"Transport : {resultat['ratio_transport_pourcentage']}% "
                "du prix de vente HT"
            )

        self.detailsBase[canal_id] = detail

        itemDetail = QTableWidgetItem(detail)
        itemDetail.setToolTip(detail)
        self.table.setItem(ligne, 7, itemDetail)

        # Si un prix marché est déjà saisi sur cette ligne,
        # on met à jour la décision en conséquence.
        self._actualiserDecision(ligne)

        if hasattr(self, "_derniersCanaux"):
            self._comparerCanauxSimilaires(self._derniersCanaux)

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
            self._appliquerStyleAlerte(itemDecision, "erreur")
            self.table.setItem(ligne, 6, itemDecision)
            return

        itemDecision = QTableWidgetItem()

        if prix_marche <= 0:

            itemDecision.setText(resultat["decision"])
            self._appliquerStyleAlerte(itemDecision, "ok")

        elif prix_marche >= resultat["prix_vente_ttc"]:

            itemDecision.setText("✅ Recommandé (vs marché)")
            self._appliquerStyleAlerte(itemDecision, "ok")

        else:

            itemDecision.setText("⚠️ Prix marché trop bas")
            self._appliquerStyleAlerte(itemDecision, "attention")

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

        # Le port du fournisseur est déjà compté dans le coût
        # produit, mais on le montre à part : sinon on cherche
        # en vain d'où vient l'écart de prix.
        port_fournisseur = resultat.get("cout_port_fournisseur", 0) or 0

        if port_fournisseur:

            lignes_detail = [
                f"Coût produit (achat + emballage + provision "
                f"retour) : "
                f"{resultat['cout_produit'] - port_fournisseur:.2f} € HT",
                f"+ Port facturé par le fournisseur : "
                f"{port_fournisseur:.2f} € HT",
                f"= Coût produit total : "
                f"{resultat['cout_produit']:.2f} € HT",
            ]

        else:

            lignes_detail = [
                f"Coût produit (achat + emballage + provision "
                f"retour) : "
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

        # Les pourcentages seuls ne suffisent pas à retrouver
        # l'écart entre le coût et le prix : la marge se
        # calcule sur le HT, tandis que la commission et les
        # frais de paiement se prélèvent sur le TTC. On donne
        # donc le montant en euros à côté de chaque taux.
        prix_ht = resultat["prix_vente_ht"]
        prix_ttc = resultat["prix_vente_ttc"]

        montant_marge = prix_ht * resultat["marge_pourcentage"] / 100

        lignes_detail.append(
            f"Ta marge : {resultat['marge_pourcentage']:.1f} % "
            f"du prix HT  =  {montant_marge:.2f} €"
        )

        montant_commission = (
            prix_ttc * resultat["commission_pourcentage"] / 100
        )

        lignes_detail.append(
            f"Commission de vente : "
            f"{resultat['commission_pourcentage']:.1f} % "
            f"du prix TTC  =  {montant_commission:.2f} €"
        )

        montant_paiement = 0

        if resultat["taux_paiement_pourcentage"]:

            montant_paiement = (
                prix_ttc * resultat["taux_paiement_pourcentage"] / 100
            )

            lignes_detail.append(
                f"Frais de paiement : "
                f"{resultat['taux_paiement_pourcentage']:.1f} % "
                f"du prix TTC  =  {montant_paiement:.2f} €"
            )

        montant_tsn = 0

        if resultat["taux_tsn_effectif"]:

            montant_tsn = prix_ht * resultat["taux_tsn_effectif"] / 100

            lignes_detail.append(
                f"TSN effective : {resultat['taux_tsn_effectif']:.2f} % "
                f"=  {montant_tsn:.2f} €"
            )

        # Le total, pour que l'écart entre le coût direct et
        # le prix de vente se vérifie d'un coup d'œil.
        lignes_detail.append(
            f"    → total prélevé : "
            f"{montant_marge + montant_commission + montant_paiement + montant_tsn:.2f} €"
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

    def _emballage_id(self):
        return None

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
        self._marche_existant = marche or {}

        self.calculer()