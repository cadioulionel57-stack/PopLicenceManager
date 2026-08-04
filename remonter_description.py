r"""
remonter_description.py  (13e version)
------------------------------------------------------------
Termine les deux derniers modeles : SITE PRECOMMANDE et
STOCK Cartes a collectionner.

Ils gardaient leurs questions-reponses parce que
l'information de livraison y etait ecrite. On leur donne
donc le meme pave jaune "Optimisez votre livraison" que les
autres modeles, puis on retire les questions.

Ces deux modeles sont alors alignes sur les 49 autres.

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

MODELES = ["PRECOMMANDE", "CARTES A COLLECTIONNER"]


# Le pave jaune, repris a l'identique des autres modeles.
PAVE = """<div style="
text-align:center;
font-family:Arial,sans-serif;
background:#fffbeb;
border:2px solid #fcd34d;
padding:28px 20px;
border-radius:12px;
margin:30px 0;
box-shadow:0 4px 6px -1px rgba(251,191,36,0.1);
">

  <div style="
  display:flex;
  align-items:center;
  justify-content:center;
  gap:12px;
  margin-bottom:18px;
  ">

    <h4 style="
    margin:0;
    color:#92400e;
    font-size:16px;
    text-transform:uppercase;
    font-weight:800;
    letter-spacing:1px;
    ">

      Optimisez votre livraison

    </h4>

  </div>

  <p style="
  margin:0 auto 22px auto;
  max-width:650px;
  font-size:14px;
  color:#78350f;
  line-height:1.7;
  ">

    Pour un traitement plus rapide, nous vous conseillons de passer des commandes <strong>distinctes</strong> pour les articles "En Stock" et "Livraison sous 5 à 7 jours ouvrés".

  </p>

  <div style="
  max-width:550px;
  margin:0 auto;
  text-align:left;
  ">

    <p style="
    margin:0 0 16px 0;
    font-size:14px;
    color:#78350f;
    line-height:1.7;
    ">

      Les produits <strong>en stock</strong> sont expédiés le jour même si votre commande est validée avant 11h du lundi au vendredi. À défaut, l'envoi est effectué sous 24h ou au premier jour ouvrable.

    </p>

    <p style="
    margin:0;
    font-size:14px;
    color:#78350f;
    line-height:1.7;
    ">

      Les produits <strong>"Livraison sous 5 à 7 jours ouvrés"</strong> sont expédiés sous 24h et livrés à domicile en remise contre signature. <strong>Livraison offerte, sans minimum d'achat.</strong>

    </p>

  </div>

  <div style="
  margin:24px auto;
  width:40px;
  height:2px;
  background:#fcd34d;
  "></div>

  <p style="
  margin:0;
  font-size:13px;
  color:#92400e;
  font-style:italic;
  line-height:1.5;
  ">

    <strong>À noter :</strong> en cas de commande mixte, vos produits seront expédiés séparément et pourront avoir des délais de livraison différents.

  </p>

</div>"""


def concerne(nom_modele):

    majuscules = (
        nom_modele.upper()
        .replace("É", "E").replace("È", "E").replace("À", "A")
    )

    return any(mot in majuscules for mot in MODELES)


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
    """
    Remplace la section des questions-reponses par le pave
    jaune. Renvoie (html, True) si le modele a change.
    """

    if "Optimisez" in html:
        return html, False

    entete, morceaux = sections(html)

    if not morceaux:
        return html, False

    fait = False
    resultat = []

    for titre, texte in morceaux:

        if "FAQ" in titre:
            fait = True
            coupe = texte.find("-->") + len("-->")
            resultat.append((titre, texte[:coupe] + "\n\n" + PAVE + "\n"))
            continue

        resultat.append((titre, texte))

    if not fait:
        return html, False

    return rebobiner(entete + "".join(t for _, t in resultat)), True


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

    print("\n=== LES DEUX DERNIERS MODELES ===\n")

    prevus = []

    for modele in modeles:

        if not concerne(modele["nom"]):
            continue

        nouveau_html, fait = corriger(modele["html_template"])

        if not fait:
            continue

        print(
            f"   {modele['nom'][:44]:<46} "
            f"questions remplacees par le pave livraison"
        )

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

    apres = db.lire(
        "SELECT nom, html_template FROM modeles_fiche_produit "
        "WHERE html_template IS NOT NULL"
    )

    questions = [
        l["nom"] for l in apres
        if "Questions fr" in re.sub(r"<[^>]+>", " ", l["html_template"])
    ]

    casses = sum(
        1 for l in apres
        if l["html_template"].count("<div")
        != l["html_template"].count("</div>")
    )

    print(f"Modeles avec des questions-reponses : {len(questions)}")
    print(f"Modeles au cadre mal ferme : {casses}\n")