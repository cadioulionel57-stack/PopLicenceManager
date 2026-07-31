import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


db = Database()

modele = db.lire_un(
    """
    SELECT nom, html_template
    FROM modeles_fiche_produit
    WHERE nom LIKE '%DF Peluches%'
    """
)

if modele is None:
    print("\nModèle introuvable.\n")
    sys.exit(0)

html = modele["html_template"] or ""

print()
print("=== " + modele["nom"] + " ===")

motif = re.compile(
    r"tarif_livraison_df|seuil_livraison_gratuite_df"
)

for trouve in motif.finditer(html):

    debut = max(0, trouve.start() - 300)
    fin = min(len(html), trouve.end() + 200)

    extrait = re.sub(r"<[^>]+>", " ", html[debut:fin])
    extrait = re.sub(r"\s+", " ", extrait).strip()

    print()
    print("---")
    print(extrait)

print()