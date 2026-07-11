from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
)

from modules.canal_manager import CanalManager


STATUTS = [
    "Brouillon",
    "Prêt à publier",
    "Publié",
]


class PublicationTab(QWidget):
    """
    Détermine sur quels canaux de vente un produit est
    vendu (WiziShop, Amazon, Cdiscount...), avec sa
    référence externe et son statut sur ce canal.

    Une ligne par canal actif, générée automatiquement :
    ajouter ou retirer un canal dans l'écran "Canaux de
    vente" change ce qui s'affiche ici sans toucher au
    code.

    Règle métier : les canaux de type "marketplace"
    (envoyés via Base.com) ne sont proposés que pour les
    produits de type "stock". Le dropshipping, les bundles
    et les lots ne peuvent être vendus que sur un canal de
    type "site" (WiziShop).
    """

    def __init__(self, type_produit=None):

        super().__init__()

        self.type_produit = type_produit

        exterieur = QVBoxLayout(self)
        exterieur.setContentsMargins(0, 0, 0, 0)

        zoneDefilement = QScrollArea()
        zoneDefilement.setWidgetResizable(True)
        zoneDefilement.setStyleSheet(
            "QScrollArea{border:none; background:transparent;}"
        )

        contenuDefilant = QWidget()
        layout = QVBoxLayout(contenuDefilant)

        zoneDefilement.setWidget(contenuDefilant)
        exterieur.addWidget(zoneDefilement)

        groupe = QGroupBox("🚀 Canaux de vente")

        grille = QGridLayout(groupe)

        entete = ["Canal", "Vendu ici", "Référence externe", "Statut"]

        for colonne, texte in enumerate(entete):

            libelle = QLabel(texte)
            libelle.setStyleSheet("font-weight:bold;")
            grille.addWidget(libelle, 0, colonne)

        self.lignesCanaux = {}

        canaux = CanalManager().tous()

        for ligne, canal in enumerate(canaux, start=1):

            compatible = (
                canal["type"] != "marketplace"
                or self.type_produit == "stock"
            )

            texteCanal = canal["nom"]
            if not compatible:
                texteCanal += " (produits en stock uniquement)"

            nomCanal = QLabel(texteCanal)

            if not compatible:
                nomCanal.setStyleSheet("color:#a0a0a0;")

            venduIci = QCheckBox()
            reference = QLineEdit()
            statut = QComboBox()
            statut.addItems(STATUTS)

            reference.setEnabled(False)
            statut.setEnabled(False)

            venduIci.toggled.connect(reference.setEnabled)
            venduIci.toggled.connect(statut.setEnabled)

            if not compatible:
                venduIci.setEnabled(False)

            grille.addWidget(nomCanal, ligne, 0)
            grille.addWidget(venduIci, ligne, 1)
            grille.addWidget(reference, ligne, 2)
            grille.addWidget(statut, ligne, 3)

            self.lignesCanaux[canal["id"]] = {
                "venduIci": venduIci,
                "reference": reference,
                "statut": statut,
            }

        layout.addWidget(groupe)
        layout.addStretch()

    def canaux_selectionnes(self):
        """
        Renvoie la liste des canaux à enregistrer :
        uniquement ceux où "Vendu ici" est coché.
        """

        resultat = []

        for canal_id, widgets in self.lignesCanaux.items():

            if not widgets["venduIci"].isChecked():
                continue

            resultat.append({
                "canal_id": canal_id,
                "publie": True,
                "reference_externe": widgets["reference"].text(),
                "statut": widgets["statut"].currentText(),
            })

        return resultat

    def charger(self, canaux_produit):
        """
        Pré-remplit l'onglet à partir des canaux déjà
        enregistrés pour ce produit.

        canaux_produit : {canal_id: {publie, reference_externe, statut}}
        """

        for canal_id, widgets in self.lignesCanaux.items():

            info = canaux_produit.get(canal_id)

            if info is None:
                continue

            widgets["venduIci"].setChecked(info["publie"])
            widgets["reference"].setText(info["reference_externe"] or "")

            index = widgets["statut"].findText(info["statut"] or "")
            if index != -1:
                widgets["statut"].setCurrentIndex(index)