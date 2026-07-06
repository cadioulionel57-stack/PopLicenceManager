from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage


class CollectionsPage(ReferencePage):

    def __init__(self):

        super().__init__(
            "📚 Gestion des collections",
            "collections",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "Description",
                "Active"
            ]
        )

        self.charger()