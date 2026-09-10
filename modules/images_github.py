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

07/09/2026 : WIZISHOP NE PREND PAS LE FORMAT WEBP. Une image .webp
etait deposee sur GitHub, envoyee a WiziShop, et silencieusement
ignoree : la fiche arrivait sans photo. Les WebP sont desormais
CONVERTIES EN JPG avant depot, et le nom de fichier suit (.jpg).
Les autres formats passent inchanges.

Utilisation en ligne de commande, depuis C:\\PopLicenceManager :
    python -m modules.images_github test
"""

import base64
import io
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

# Formats que WiziShop refuse et qu'il faut convertir en JPG.
A_CONVERTIR = (".webp",)


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
    """
    Extension du fichier a deposer.

    Une source .webp ressort en .jpg : le fichier sera converti
    avant depot, donc son nom doit deja porter la bonne extension.
    """
    for ext in EXTENSIONS:
        if url.lower().split("?")[0].endswith(ext):
            if ext == ".jpeg":
                return ".jpg"
            if ext in A_CONVERTIR:
                return ".jpg"
            return ext
    return ".jpg"


def _source_a_convertir(url_source):
    base = url_source.lower().split("?")[0]
    return any(base.endswith(ext) for ext in A_CONVERTIR)


def _convertir_en_jpg(contenu):
    """
    Convertit le contenu binaire d'une image en JPG.

    Le fond transparent d'une WebP devient blanc : sans cela, la
    conversion echoue ou produit un fond noir sur les visuels
    detoures des fournisseurs.
    """
    from PIL import Image

    image = Image.open(io.BytesIO(contenu))

    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        fond = Image.new("RGB", image.size, (255, 255, 255))
        fond.paste(image, mask=image.split()[-1])
        image = fond
    else:
        image = image.convert("RGB")

    sortie = io.BytesIO()
    image.save(sortie, format="JPEG", quality=90, optimize=True)
    return sortie.getvalue()


def _telecharger(url):
    requete = urllib.request.Request(
        url,
        headers={"User-Agent": "PopLicenceManager"},
    )
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return reponse.read()


def _sha_existant(jeton, depot, chemin):
    requete = urllib.request.Request(
        API.format(depot=depot, chemin=chemin),
        headers={
            "Authorization": f"Bearer {jeton}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "PopLicenceManager",
        },
    )
    try:
        with urllib.request.urlopen(requete, timeout=60) as reponse:
            return json.loads(reponse.read()).get("sha")
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

    Une source WebP est convertie en JPG avant depot : WiziShop
    ignore les WebP et la fiche arriverait sans photo.

    Passer remplacer=True pour forcer le remplacement (photo
    changee chez le fournisseur).
    """
    jeton, depot = _config()
    chemin = f"produits/{nom_fichier}"

    sha = _sha_existant(jeton, depot, chemin)

    if sha and not remplacer:
        return BRUT.format(depot=depot, chemin=chemin)

    contenu = _telecharger(url_source)

    if _source_a_convertir(url_source):
        contenu = _convertir_en_jpg(contenu)

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


if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        jeton, depot = _config()
        print("Depot :", depot)
        print("Jeton :", "present" if jeton else "ABSENT")
        try:
            from PIL import Image  # noqa: F401
            print("Pillow : present (conversion WebP -> JPG active)")
        except ImportError:
            print("Pillow : ABSENT — les WebP ne pourront pas etre converties")