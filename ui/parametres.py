from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.categories_site import CategoriesSitePage
from ui.themes_template import ThemesTemplatePage
from ui.modeles_fiche import ModelesFichePage
from ui.reglages_fiche import ReglagesFichePage
from ui.attributs import AttributsPage
from ui.regles_template import ReglesTemplatePage


class ParametresPage(QWidget):
    """
    Regroupe les écrans de configuration : catégories du
    site (WiziShop), thèmes de template, modèles de fiche
    produit (chartes HTML par thème + type de produit), les
    règles de template par période commerciale, les critères
    de variation (couleurs, tailles, pointures) et les
    réglages globaux utilisés dans ces modèles.
    """

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        onglets = QTabWidget()

        self.pageCategoriesSite = CategoriesSitePage()
        self.pageThemesTemplate = ThemesTemplatePage()
        self.pageModelesFiche = ModelesFichePage()
        self.pageReglagesFiche = ReglagesFichePage()
        self.pageAttributs = AttributsPage()
        self.pageReglesTemplate = ReglesTemplatePage()

        onglets.addTab(self.pageCategoriesSite, "🏷 Catégories Site")
        onglets.addTab(self.pageThemesTemplate, "🎨 Thèmes de template")
        onglets.addTab(self.pageModelesFiche, "📄 Modèles de fiche")
        onglets.addTab(self.pageReglesTemplate, "📅 Templates par période")
        onglets.addTab(self.pageAttributs, "🎨 Variations")
        onglets.addTab(self.pageReglagesFiche, "⚙️ Réglages")

        layout.addWidget(onglets)

    def charger(self):

        self.pageCategoriesSite.charger()
        self.pageThemesTemplate.charger()
        self.pageModelesFiche.charger()
        self.pageReglesTemplate.charger()
        self.pageAttributs.charger()
        self.pageReglagesFiche.charger()