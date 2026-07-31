"""
Branche l'écran Stock dans le menu principal.

À lancer une seule fois depuis la racine du projet :
    python brancher_stock.py

Le script vérifie chaque point d'insertion avant d'écrire.
Si l'un d'eux est introuvable, rien n'est modifié.
"""

from pathlib import Path

fichier = Path("ui/main_window.py")
texte = fichier.read_text(encoding="utf-8")

if "StockPage" in texte:
    print("Deja branche : rien a faire.")
    raise SystemExit

etapes = [
    (
        "import",
        "from ui.sav import SavPage\n"
        "from modules.commande_manager import CommandeManager",

        "from ui.sav import SavPage\n"
        "from ui.stock import StockPage\n"
        "from modules.commande_manager import CommandeManager",
    ),
    (
        "bouton du menu",
        '            "\U0001f9fe  Achats Stocks",\n',

        '            "\U0001f9fe  Achats Stocks",\n'
        '            "\U0001f5c3\ufe0f  Stock",\n',
    ),
    (
        "page en fin de pile",
        "        self.pages.addWidget(self.pageCategoriesSite)\n",

        "        self.pages.addWidget(self.pageCategoriesSite)\n"
        "\n"
        "        # Ecran Stock ajoute en FIN de pile : il prend\n"
        "        # l'index 20 et aucun index existant ne bouge.\n"
        "        self.pageStock = StockPage()\n"
        "        self.pages.addWidget(self.pageStock)\n",
    ),
    (
        "connexion du bouton",
        "                self.pages.setCurrentIndex(19),\n"
        "                self.pageCategoriesSite.charger()\n"
        "            )\n"
        "        )\n",

        "                self.pages.setCurrentIndex(19),\n"
        "                self.pageCategoriesSite.charger()\n"
        "            )\n"
        "        )\n"
        '        self.boutons["\U0001f5c3\ufe0f  Stock"].clicked.connect(\n'
        "            lambda: (\n"
        "                self.pages.setCurrentIndex(20),\n"
        "                self.pageStock.charger()\n"
        "            )\n"
        "        )\n",
    ),
]

for nom, ancien, _ in etapes:
    if texte.count(ancien) != 1:
        print(
            f"ARRET : point d'insertion '{nom}' trouve "
            f"{texte.count(ancien)} fois au lieu d'une. "
            "Rien n'a ete modifie."
        )
        raise SystemExit

fichier.with_suffix(".py.bak").write_text(texte, encoding="utf-8")

for nom, ancien, nouveau in etapes:
    texte = texte.replace(ancien, nouveau)
    print(f"  ok : {nom}")

fichier.write_text(texte, encoding="utf-8")

print("Ecran Stock branche. Sauvegarde : ui/main_window.py.bak")