"""
Depose les images produit sur GitHub avec un nom de fichier lisible,
et renvoie les URL brutes a envoyer a WiziShop.

WiziShop recopie l'image sur son CDN et REPREND LE NOM DU FICHIER :
c'est ce nom qui devient la balise ALT. En envoyant
pyjama-long-polaire-bluey-enfant-1.jpg au lieu de 2900002967.jpg,
l'ALT est correct des le depart.

20/08/2026 : un fichier DEJA EN LIGNE n'est plus redepose. L'adresse
renvoyee est alors la meme que la fois precedente, donc WiziShop n'a
rien de neuf a telecharger et ne peut pas creer de doublon dans le
gestionnaire d'images.

Utilisation en ligne de commande, depuis C:\\PopLicenceManager :
    python -m modules.images_github test
"""

import base64
import json
import re
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "config_api.json"
API = "https://api.github.com/repos/{depot}/contents/{chemin}"
BRUT = "https://raw.githubusercontent.com/{depot}/main/{chemin}"

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def _config():
    donnees = json.loads(CONFIG.read_text(encoding="utf-8"))
    jeton = donnees.get("jeton_github")
    depot = donnees.get("depot_github")
    if not jeton or not depot:
        raise RuntimeError(
            "jeton_github ou depot_github absent de config_api.json"
        )
    return jeton, depot


def slug(texte):
    """Pyjama long polaire Bluey - Enfant -> pyjama-long-polaire-bluey-enfant"""
    texte = unicodedata.normalize("NFKD", str(texte or ""))
    texte = texte.encode("ascii", "ignore").decode("ascii").lower()
    texte = re.sub(r"[^a-z0-9]+", "-", texte)
    texte = re.sub(r"-+", "-", texte).strip("-") or "image"
    if len(texte) > 70:
        texte = texte[:70].rsplit("-", 1)[0]
    return texte


def extension(url):
    for ext in EXTENSIONS:
        if url.lower().split("?")[0].endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def _telecharger(url):
    requete = urllib.request.Request(
        url, headers={"User-Agent": "PopLicenceManager"}
    )
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return reponse.read()


def _sha_existant(jeton, depot, chemin):
    """Renvoie le sha du fichier s'il est deja en ligne, sinon None."""
    requete = urllib.request.Request(
        API.format(depot=depot, chemin=chemin),
        headers={
            "Authorization": f"Bearer {jeton}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "PopLicenceManager",
        },
    )
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return json.loads(reponse.read())["sha"]
    except urllib.error.HTTPError as erreur:
        if erreur.code == 404:
            return None
        raise


def deposer(url_source, nom_fichier, remplacer=False):
    """
    Telecharge l'image et la depose sur GitHub sous nom_fichier,
    puis renvoie l'URL brute.

    Si le fichier est DEJA EN LIGNE, il n'est PAS redepose : on
    renvoie simplement son adresse. WiziShop recoit alors la meme
    adresse qu'avant et ne cree aucun doublon.

    Passer remplacer=True pour forcer le remplacement (photo
    changee chez le fournisseur).
    """
    jeton, depot = _config()
    chemin = f"produits/{nom_fichier}"

    sha = _sha_existant(jeton, depot, chemin)

    if sha and not remplacer:
        return BRUT.format(depot=depot, chemin=chemin)

    contenu = _telecharger(url_source)

    corps = {
        "message": f"image {nom_fichier}",
        "content": base64.b64encode(contenu).decode("ascii"),
    }

    if sha:
        corps["sha"] = sha

    requete = urllib.request.Request(
        API.format(depot=depot, chemin=chemin),
        data=json.dumps(corps).encode("utf-8"),
        method="PUT",
        headers={
            "Authorization": f"Bearer {jeton}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "PopLicenceManager",
        },
    )
    with urllib.request.urlopen(requete, timeout=120):
        pass

    return BRUT.format(depot=depot, chemin=chemin)


def deja_en_ligne(nom_fichier):
    """Dit si le fichier est deja sur le depot."""
    jeton, depot = _config()
    return _sha_existant(jeton, depot, f"produits/{nom_fichier}") is not None


def urls_lisibles(nom_produit, urls, remplacer=False):
    """
    Prend le nom du produit et ses URL fournisseur,
    renvoie la liste des URL GitHub renommees.
    """
    base = slug(nom_produit)
    resultat = []
    for rang, url in enumerate(urls, start=1):
        if not url:
            continue
        nom = f"{base}-{rang}{extension(url)}"
        resultat.append(deposer(url, nom, remplacer=remplacer))
    return resultat


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        source = (
            "https://s3.eu-central-1.amazonaws.com/"
            "images.cerdagroup.net/big/2900002967.jpg"
        )
        print("Depot en cours...")
        print(deposer(source, "pyjama-long-polaire-bluey-enfant-1.jpg"))
    else:
        print(__doc__)