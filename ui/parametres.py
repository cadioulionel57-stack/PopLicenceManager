from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.categories_site import CategoriesSitePage
from ui.modeles_fiche import ModelesFichePage
from ui.reglages_fiche import ReglagesFichePage


class ParametresPage(QWidget):
    """
    Regroupe les écrans de configuration : catégories du
    site (WiziShop), modèles de fiche produit (chartes HTML
    par catégorie + type de produit), et les réglages
    globaux utilisés dans ces modèles.
    """

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        onglets = QTabWidget()

        self.pageCategoriesSite = CategoriesSitePage()
        self.pageModelesFiche = ModelesFichePage()
        self.pageReglagesFiche = ReglagesFichePage()

        onglets.addTab(self.pageCategoriesSite, "🏷 Catégories Site")
        onglets.addTab(self.pageModelesFiche, "📄 Modèles de fiche")
        onglets.addTab(self.pageReglagesFiche, "⚙️ Réglages")

        layout.addWidget(onglets)

    def charger(self):

        self.pageCategoriesSite.charger()
        self.pageModelesFiche.charger()
        self.pageReglagesFiche.charger()