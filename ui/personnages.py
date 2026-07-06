from modules.reference_manager import ReferenceManager
from ui.reference_page import ReferencePage


class PersonnagesPage(ReferencePage):

    def __init__(self):

        super().__init__(
            "👤 Gestion des personnages",
            "personnages",
            ReferenceManager(),
            [
                "ID",
                "Nom",
                "Description",
                "Active"
            ]
        )

        self.charger()