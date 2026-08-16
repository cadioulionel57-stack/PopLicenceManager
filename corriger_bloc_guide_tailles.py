r"""
corriger_bloc_guide_tailles.py
------------------------------------------------------------
Retire des modeles de fiche l'encart bleu "Guide des tailles
disponible" / "Guide des pointures disponible" et son bouton
"Voir le guide", dont le lien renvoie une 404.

La grille du produit reste affichee par le bloc repliable
"Trouver sa taille", genere par modules/grilles_tailles.py.

La PAGE Guide des tailles (modele 57) n'est pas touchee :
le bloc retire doit contenir un lien guide-des-tailles.

    python corriger_bloc_guide_tailles.py
------------------------------------------------------------
"""

import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent / "database" / "poplicence.db"

MOTIF = re.compile(
    r"<!--\s*=+\s*[^\w<]*GUIDE DES (?:TAILLES|POINTURES)\s*=+\s*-->",
    re.I,
)


def retirer(html):

    m = MOTIF.search(html)

    if not m:
        return html, 0

    reste = html[m.end():]

    ouverture = re.search(r"<(section|div)\b", reste, re.I)

    if not ouverture:
        return html, 0

    balise = ouverture.group(1).lower()
    pos = ouverture.end()
    profondeur = 1
    jeton = re.compile(rf"<(/?){balise}\b", re.I)

    while profondeur > 0:

        t = jeton.search(reste, pos)

        if not t:
            return html, 0

        profondeur += -1 if t.group(1) else 1
        pos = t.end()

    ferme = reste.find(">", pos)

    if ferme < 0:
        return html, 0

    coupe = m.end() + ferme + 1
    bloc = html[m.start():coupe]

    if "guide-des-tailles" not in bloc:
        return html, 0

    return html[:m.start()] + html[coupe:], len(bloc)


if __name__ == "__main__":

    horodatage = datetime.now().strftime("%Y%m%d_%H%M")
    sauvegarde = BASE.parent / f"poplicence_avant_guide_{horodatage}.db"
    shutil.copy(BASE, sauvegarde)
    print(f"\nSauvegarde : {sauvegarde.name}")

    connexion = sqlite3.connect(str(BASE))
    connexion.row_factory = sqlite3.Row

    lignes = connexion.execute(
        "SELECT id, nom, html_template FROM modeles_fiche_produit"
    ).fetchall()

    a_corriger = []

    for ligne in lignes:

        nouveau, taille = retirer(ligne["html_template"] or "")

        if taille:
            a_corriger.append((ligne["id"], ligne["nom"], nouveau, taille))

    if not a_corriger:
        print("\nAucun modele a corriger.\n")
        raise SystemExit(0)

    print(f"\n{len(a_corriger)} modele(s) a corriger :\n")

    for identifiant, nom, _, taille in a_corriger:
        print(f"   {identifiant:>3}  {nom[:50]:<52} {taille} caracteres")

    reponse = input("\nRetirer ces blocs ? (tape oui) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnule, rien n'a ete modifie.\n")
        raise SystemExit(0)

    for identifiant, nom, nouveau, _ in a_corriger:
        connexion.execute(
            "UPDATE modeles_fiche_produit SET html_template = ? "
            "WHERE id = ?",
            (nouveau, identifiant),
        )

    connexion.commit()

    restants = connexion.execute(
        "SELECT COUNT(*) FROM modeles_fiche_produit "
        "WHERE html_template LIKE '%Voir le guide%'"
    ).fetchone()[0]

    connexion.close()

    print(f"\n{len(a_corriger)} modele(s) corrige(s).")
    print(f"Modeles contenant encore 'Voir le guide' : {restants}\n")