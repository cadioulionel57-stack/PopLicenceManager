from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage


class UniversPage(ReferencePage):

    def __init__(self):

        super().__init__(
            "🌍 Gestion des univers",
            "univers",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "Description",
                "Active"
            ]
        )

        self.charger()