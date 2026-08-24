# -*- coding: utf-8 -*-
"""
Prepare les images d'un produit pour WiziShop.

Telecharge les images du fournisseur, les renomme avec le slug SEO du
produit, les depose dans visuels/, les pousse sur GitHub et remplace les
adresses dans la base. WiziShop nomme ensuite l'image d'apres le nom du
fichier recu, ce qui donne une balise ALT correcte sans reprise manuelle.

Usage :
    python -m modules.wizishop_images preparer <id_produit>
    python -m modules.wizishop_images preparer-tout
    python -m modules.wizishop_images etat
"""

import os
import re
import sqlite3
import subprocess
import sys
import unicodedata
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RACINE, "database", "poplicence.db")
DOSSIER = os.path.join(RACINE, "visuels")

DEPOT = "cadioulionel57-stack/PopLicenceManager"
BRANCHE = "main"
PREFIXE = "https://raw.githubusercontent.com/%s/%s/visuels/" % (DEPOT, BRANCHE)

NAVIGATEUR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

COLONNES = ("image_principale", "image_2", "image_3")


def slugifier(texte):
    texte = unicodedata.normalize("NFKD", texte or "")
    texte = texte.encode("ascii", "ignore").decode("ascii").lower()
    texte = re.sub(r"[^a-z0-9]+", "-", texte)
    return texte.strip("-")[:80] or "produit"


def extension(adresse):
    fin = adresse.split("?")[0].lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        if fin.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def telecharger(adresse, destination):
    requete = urllib.request.Request(adresse, headers={"User-Agent": NAVIGATEUR})
    with urllib.request.urlopen(requete, timeout=40) as reponse:
        contenu = reponse.read()
    with open(destination, "wb") as fichier:
        fichier.write(contenu)
    return len(contenu)


def connexion():
    lien = sqlite3.connect(BASE)
    lien.row_factory = sqlite3.Row
    return lien


def base_du_nom(produit):
    slug = produit["url_slug"] or ""
    if not slug:
        slug = slugifier(produit["nom"])
    return slug


def preparer(id_produit, lien=None, silencieux=False):
    """Traite un produit. Renvoie le nombre d'images preparees."""
    ferme = False
    if lien is None:
        lien = connexion()
        ferme = True

    produit = lien.execute(
        "select id, nom, url_slug, image_principale, image_2, image_3 "
        "from produits where id = ?", (id_produit,)).fetchone()

    if produit is None:
        print("Produit %s introuvable." % id_produit)
        return 0

    os.makedirs(DOSSIER, exist_ok=True)
    slug = base_du_nom(produit)
    faites = 0

    for rang, colonne in enumerate(COLONNES, start=1):
        adresse = (produit[colonne] or "").strip()
        if not adresse:
            continue
        if adresse.startswith(PREFIXE):
            continue  # deja preparee

        suffixe = "" if rang == 1 else "-%d" % rang
        nom_fichier = "%s%s%s" % (slug, suffixe, extension(adresse))
        chemin = os.path.join(DOSSIER, nom_fichier)

        try:
            poids = telecharger(adresse, chemin)
        except Exception as erreur:
            print("  ECHEC %s : %s" % (colonne, erreur))
            continue

        nouvelle = PREFIXE + nom_fichier
        lien.execute("update produits set %s = ? where id = ?" % colonne,
                     (nouvelle, id_produit))
        faites += 1
        if not silencieux:
            print("  %-18s -> %s (%d ko)" % (colonne, nom_fichier, poids // 1024))

    lien.commit()
    if ferme:
        lien.close()
    return faites


def pousser_sur_github():
    for commande in (["git", "add", "visuels", "database/poplicence.db"],
                     ["git", "commit", "-m", "Images produits renommees"],
                     ["git", "push"]):
        resultat = subprocess.run(commande, cwd=RACINE,
                                  capture_output=True, text=True)
        if resultat.returncode != 0 and "nothing to commit" not in resultat.stdout:
            print("git %s : %s" % (commande[1], resultat.stderr.strip()))
            return False
    return True


def preparer_tout():
    lien = connexion()
    produits = lien.execute(
        "select id, nom from produits where "
        "(image_principale is not null and image_principale <> '') "
        "or (image_2 is not null and image_2 <> '') "
        "or (image_3 is not null and image_3 <> '') order by id").fetchall()

    total = 0
    for produit in produits:
        faites = preparer(produit["id"], lien, silencieux=True)
        if faites:
            print("%4d  %-55s %d image(s)" % (produit["id"], produit["nom"][:55], faites))
            total += faites
    lien.close()

    print("")
    print("%d image(s) preparee(s)." % total)
    if total:
        print("Envoi sur GitHub...")
        if pousser_sur_github():
            print("Termine. Les fiches peuvent etre poussees vers WiziShop.")


def etat():
    lien = connexion()
    lignes = lien.execute("select image_principale from produits").fetchall()
    lien.close()
    pretes = sum(1 for l in lignes if (l[0] or "").startswith(PREFIXE))
    avec = sum(1 for l in lignes if (l[0] or "").strip())
    print("Produits avec image principale : %d" % avec)
    print("Deja preparees                 : %d" % pretes)
    print("A preparer                     : %d" % (avec - pretes))


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "etat"
    if action == "preparer" and len(sys.argv) > 2:
        preparer(int(sys.argv[2]))
        pousser_sur_github()
    elif action == "preparer-tout":
        preparer_tout()
    else:
        etat()