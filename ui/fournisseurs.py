from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage


class FournisseursPage(ReferencePage):

    def __init__(self):

        super().__init__(
            "🚚 Gestion des fournisseurs",
            "fournisseurs",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "Description",
                "Active"
            ]
        )

        self.charger()