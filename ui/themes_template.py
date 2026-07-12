from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage


class ThemesTemplatePage(ReferencePage):
    """
    Gestion des thèmes de template (Vêtements, Figurines,
    Peluches...) — regroupent les modèles de fiche produit
    et permettent de rattacher un produit à un thème pour
    qu'il suive automatiquement le modèle actif de ce thème.
    """

    def __init__(self):

        super().__init__(
            "🎨 Thèmes de template",
            "themes_template",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "Description",
                "Active"
            ]
        )

        self.charger()