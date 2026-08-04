r"""
remonter_description.py  (7e version)
------------------------------------------------------------
Deux corrections.

  1. LE BLOC BLEU "Livraison partenaire securisee" est
     supprime des modeles Direct Fournisseur. Il fait
     doublon avec le pave jaune du bas, qui explique en
     plus pourquoi separer ses commandes.

  2. MAILLAGE INTERNE. Un bouton renvoie vers la PAGE
     MARQUE de la licence : un jeu Stranger Things menera
     vers /m/stranger-things/, un sac Bluey vers /m/bluey/.
     L'adresse est fabriquee par le logiciel a partir de la
     licence du produit, il n'y a rien a saisir.

     Le bouton se pose dans "Completez la collection" quand
     ce bloc existe, sinon dans la banniere univers : tous
     les types de produits sont ainsi couverts.

     Il n'apparait pas si le produit n'a pas de licence.

Relancable sans risque.

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


BOUTON = (
    "\n\n  {{#si_licence}}\n"
    "  <a href=\"{{lien_licence}}\" style=\"\n"
    "  display:inline-block;\n"
    "  margin-top:18px;\n"
    "  background:#ffffff;\n"
    "  color:#111827 !important;\n"
    "  padding:12px 22px;\n"
    "  border-radius:999px;\n"
    "  font-size:14px;\n"
    "  font-weight:900;\n"
    "  text-decoration:none;\n"
    "  \">\n"
    "    Voir tout l'univers {{licence}}\n"
    "  </a>\n"
    "  {{/si_licence}}\n"
)


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


def ajouter_bouton(texte):
    """
    Glisse le bouton juste avant la derniere balise fermante
    du bloc.
    """

    if "{{lien_licence}}" in texte:
        return texte, False

    position = texte.rfind("</div>")

    if position == -1:
        return texte, False

    return texte[:position] + BOUTON + texte[position:], True


def corriger(html, retirer_livraison):
    """
    Renvoie (html, bloc_retire, bouton_ajoute).
    """

    entete, morceaux = sections(html)

    if not morceaux:
        return html, False, False

    retire = False
    bouton = False

    resultat = []

    for titre, texte in morceaux:

        if retirer_livraison and "LIVRAISON PARTENAIRE" in titre:
            retire = True
            continue

        resultat.append((titre, texte))

    # Le bouton se pose dans "Completez la collection" quand ce
    # bloc existe, sinon dans la banniere univers. Tous les
    # modeles sont ainsi couverts, quel que soit leur type.

    cible = next(
        (i for i, (t, _) in enumerate(resultat)
         if "COMPL" in t and "UNIVERS" in t),
        None
    )

    if cible is None:
        cible = next(
            (i for i, (t, _) in enumerate(resultat)
             if "UNIVERS PRODUIT" in t),
            None
        )

    if cible is not None:

        titre, texte = resultat[cible]
        texte, bouton = ajouter_bouton(texte)
        resultat[cible] = (titre, texte)

    if not (retire or bouton):
        return html, False, False

    return entete + "".join(t for _, t in resultat), retire, bouton


if __name__ == "__main__":

    db = Database()

    types = {}

    for ligne in db.lire(
        "SELECT modele_id, type_produit FROM modeles_fiche_types"
    ):
        types.setdefault(ligne["modele_id"], []).append(
            ligne["type_produit"]
        )

    modeles = db.lire(
        """
        SELECT id, nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        ORDER BY nom
        """
    )

    print("\n=== BLOC BLEU ET MAILLAGE INTERNE ===\n")

    prevus = []

    for modele in modeles:

        est_df = "dropshipping" in types.get(modele["id"], [])

        nouveau_html, retire, bouton = corriger(
            modele["html_template"], retirer_livraison=est_df
        )

        if not (retire or bouton):
            continue

        detail = []

        if retire:
            detail.append("bloc bleu retire")

        if bouton:
            detail.append("bouton vers la page marque")

        print(f"   {modele['nom'][:38]:<40} {', '.join(detail)}")

        prevus.append((modele["id"], nouveau_html))

    if not prevus:
        print("\nRien a corriger.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) concerne(s).\n")

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