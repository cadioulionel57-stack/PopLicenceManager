"""
Retire les emojis des modèles de fiche produit.

WiziShop échappe les emojis dans un bloc Code HTML : collé
tel quel, un emoji s'affiche « \\ud83d\\udce6 » au milieu du
texte.

Deux cas sont traités, différemment :

  1. L'emoji est SEUL dans sa balise, par exemple
     <span style="font-size:28px;">EMOJI</span>
     La balise entière est supprimée, sinon il resterait un
     bloc vide qui décale la mise en page.

  2. L'emoji est en tête d'un texte, par exemple
     « EMOJI Produit en stock »
     Seul l'emoji est retiré, le texte reste intact.

Les emojis présents dans les COMMENTAIRES HTML ne sont pas
touchés : ils ne s'affichent jamais et servent de repère
pour relire un modèle.

Les variables {{...}} et les blocs {{#si_...}} ne sont
jamais modifiés : le script les recompte avant et après, et
écarte tout modèle dont le compte changerait.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


# Plages Unicode des pictogrammes, hors lettres accentuées.
EMOJI = (
    "\U0001F000-\U0001FAFF"
    "\u2190-\u2BFF"
    "\u2600-\u27BF"
    "\u23E9-\u23FA"
    "\uFE0F"
)

UN_EMOJI = re.compile(f"[{EMOJI}]")

# Balise simple ne contenant que des emojis et des espaces.
BALISE_EMOJI = re.compile(
    r"<(div|span|p|h[1-6]|strong|em)\b[^>]*>"
    r"[\s" + EMOJI + r"]+"
    r"</\1>",
    re.S,
)

COMMENTAIRE = re.compile(r"<!--.*?-->", re.S)

VARIABLE = re.compile(r"\{\{[#/]?[a-zA-Z0-9_]+\}\}")


def compter_variables(html):

    return len(VARIABLE.findall(html))


def corriger(html):
    """
    Renvoie (html corrigé, balises supprimées, emojis
    retirés). Les commentaires HTML sont mis de côté puis
    remis à l'identique.
    """

    gardes = []

    def ranger(m):
        gardes.append(m.group(0))
        return f"\x00{len(gardes) - 1}\x00"

    texte = COMMENTAIRE.sub(ranger, html)

    # 1. balises dont le contenu n'est que de l'emoji

    balises = len(BALISE_EMOJI.findall(texte))
    texte = BALISE_EMOJI.sub("", texte)

    # 2. emojis restants dans du texte

    emojis = len(UN_EMOJI.findall(texte))
    texte = UN_EMOJI.sub("", texte)

    # 3. espaces doubles laissés par les emojis retirés,
    #    uniquement à l'intérieur du texte affiché.

    texte = re.sub(r">[ \t]+([^<\n]*?)[ \t]*<", r"> \1<", texte)
    texte = re.sub(r"[ \t]{2,}", " ", texte)

    for i, garde in enumerate(gardes):
        texte = texte.replace(f"\x00{i}\x00", garde)

    return texte, balises, emojis


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

    print("\n=== EMOJIS À RETIRER ===\n")

    prevus = []
    total_balises = 0
    total_emojis = 0
    alerte = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, balises, emojis = corriger(html)

        if not balises and not emojis:
            continue

        if compter_variables(html) != compter_variables(nouveau_html):
            alerte.append(modele["nom"])
            continue

        print(
            f"   {modele['nom'][:40]:<42} "
            f"{balises:>3} balise(s)   {emojis:>3} emoji(s)"
        )

        prevus.append((modele["id"], nouveau_html))
        total_balises += balises
        total_emojis += emojis

    if alerte:
        print(
            "\n/!\\ ÉCARTÉS, le nombre de variables changeait :"
            "\n   " + "\n   ".join(alerte) + "\n"
        )

    if not prevus:
        print("\nRien à corriger.\n")
        sys.exit(0)

    print(
        f"\n{len(prevus)} modèle(s) concerné(s) : "
        f"{total_balises} balise(s) supprimée(s), "
        f"{total_emojis} emoji(s) retiré(s).\n"
    )

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for modele_id, nouveau_html in prevus:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (nouveau_html, modele_id)
        )

    print(f"\n{len(prevus)} modèle(s) corrigé(s).\n")

    apres = db.lire(
        """
        SELECT nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        """
    )

    restant = sum(
        len(UN_EMOJI.findall(COMMENTAIRE.sub("", l["html_template"])))
        for l in apres
    )

    variables = sum(
        compter_variables(l["html_template"]) for l in apres
    )

    print(f"Variables et blocs conditionnels : {variables}\n")

    if restant:
        print(f"Il reste {restant} emoji(s) visible(s).\n")
    else:
        print("Plus aucun emoji visible dans les modèles.\n")