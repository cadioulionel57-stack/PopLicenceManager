r"""
remonter_description.py  (16e version)
------------------------------------------------------------
Compacte le bloc PRECOMMANDE, qui poussait tout le reste de
la fiche vers le bas.

Le nouveau bloc garde toutes les informations utiles — date
de sortie, remise, quantites limitees — mais les met COTE A
COTE au lieu de les empiler.

Seul le modele PRECOMMANDE est touche.

Usage :
    python remonter_description.py
------------------------------------------------------------
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


MARQUEUR = re.compile(r"<!--\s*=+\s*(.{0,80}?)\s*=+\s*-->", re.S)

MODELE = "PRECOMMANDE"

SECTION = "BADGE"


BLOC = """<section style="
display:flex;
justify-content:center;
margin-bottom:24px;
">

  <div style="
  max-width:620px;
  width:100%;
  border:2px solid #f59e0b;
  border-radius:16px;
  overflow:hidden;
  box-shadow:0 8px 20px rgba(0,0,0,0.08);
  background:#ffffff;
  ">

    <div style="
    background:linear-gradient(135deg,#581C87,#9333EA);
    color:#ffffff !important;
    text-align:center;
    padding:10px;
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:1px;
    font-weight:900;
    ">
      Précommande officielle
    </div>

    <div style="
    padding:16px 18px;
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:14px;
    align-items:center;
    text-align:center;
    ">

      <div>
        <div style="
        font-size:11px;
        color:#64748b !important;
        text-transform:uppercase;
        letter-spacing:0.6px;
        font-weight:800;
        ">
          Sortie prévue
        </div>
        <div style="
        font-size:24px;
        font-weight:900;
        color:#7E22CE !important;
        margin-top:2px;
        line-height:1.1;
        ">
          {{date_sortie_precommande}}
        </div>
      </div>

      {{#si_remise_precommande}}
      <div>
        <div style="
        font-size:24px;
        font-weight:900;
        color:#dc2626 !important;
        line-height:1.1;
        ">
          -{{remise_precommande}}%
        </div>
        <div style="
        font-size:11px;
        font-weight:700;
        color:#111827 !important;
        margin-top:2px;
        line-height:1.4;
        ">
          Remise déjà incluse dans le prix
        </div>
      </div>
      {{/si_remise_precommande}}

    </div>

    <div style="
    padding:0 18px 14px 18px;
    text-align:center;
    font-size:11px;
    line-height:1.6;
    color:#9a3412 !important;
    ">
      Quantités limitées chez le distributeur. Date indicative communiquée par le fabricant.
    </div>

  </div>

</section>"""


def sections(html):

    reperes = list(MARQUEUR.finditer(html))

    if not reperes:
        return "", []

    entete = html[: reperes[0].start()]

    morceaux = []

    for i, m in enumerate(reperes):

        fin = (
            reperes[i + 1].start()
            if i + 1 < len(reperes)
            else len(html)
        )

        titre = re.sub(r"\s+", " ", m.group(1)).strip().upper()

        morceaux.append((titre, html[m.start(): fin]))

    return entete, morceaux


def rebobiner(html):

    ecart = html.count("<div") - html.count("</div>")

    if ecart > 0:
        return html + "\n" + ("</div>\n" * ecart)

    for _ in range(-ecart):

        position = html.rfind("</div>")

        if position == -1:
            break

        html = html[:position] + html[position + len("</div>"):]

    return html


def corriger(html):

    entete, morceaux = sections(html)

    if not morceaux:
        return html, 0

    gagne = 0
    resultat = []

    for titre, texte in morceaux:

        if SECTION in titre:

            coupe = texte.find("-->") + len("-->")
            nouveau = texte[:coupe] + "\n\n" + BLOC + "\n"
            gagne = len(texte) - len(nouveau)
            texte = nouveau

        resultat.append((titre, texte))

    if not gagne:
        return html, 0

    return rebobiner(entete + "".join(t for _, t in resultat)), gagne


if __name__ == "__main__":

    db = Database()

    modeles = db.lire(
        """
        SELECT id, nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        ORDER BY nom
        """
    )

    print("\n=== BLOC PRECOMMANDE COMPACTE ===\n")

    prevus = []

    for modele in modeles:

        if MODELE not in modele["nom"].upper():
            continue

        nouveau_html, gagne = corriger(modele["html_template"])

        if not gagne:
            continue

        print(f"   {modele['nom'][:44]:<46} -{gagne} caracteres")

        prevus.append((modele["id"], nouveau_html))

    if not prevus:
        print("\nRien a corriger.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) a corriger.\n")

    reponse = input("Appliquer ? (tape oui puis Entree) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnule. Rien n'a ete modifie.\n")
        sys.exit(0)

    for modele_id, nouveau_html in prevus:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (nouveau_html, modele_id)
        )

    print(f"\n{len(prevus)} modele(s) corrige(s).\n")