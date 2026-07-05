from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage


class MarquesPage(ReferencePage):

    def __init__(self):

        super().__init__(
            "™️ Gestion des marques",
            "marques",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "Description",
                "Active"
            ]
        )

        self.charger()