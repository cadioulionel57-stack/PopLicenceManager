"""
Prepare le logo du menu de PopLicenceManager.

Recadre les marges blanches de l'image d'origine, arrondit
les coins et enregistre le resultat dans
resources/images/logo.png, la ou le logiciel va le chercher.

Le fond du menu etant bleu marine, les coins arrondis evitent
le rectangle blanc disgracieux : le logo devient une pastille
posee sur le fond, ce qui est net et volontaire.

A lancer depuis la racine du projet :
    python preparer_logo.py
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, QColor
from PySide6.QtCore import Qt, QRectF


LARGEUR_FINALE = 600     # resolution du fichier enregistre
MARGE = 0.05             # marge blanche autour du logo, en %
ARRONDI = 0.06           # rayon des coins, en % de la largeur

DESTINATION = Path("resources/images/logo.png")


def cadre_utile(image, seuil=245):
    """
    Trouve la zone reellement occupee par le logo, en
    ignorant les marges blanches autour.
    """

    largeur = image.width()
    hauteur = image.height()

    gauche, droite = largeur, 0
    haut, bas = hauteur, 0

    for y in range(hauteur):
        for x in range(largeur):

            couleur = image.pixelColor(x, y)

            if (
                couleur.red() < seuil
                or couleur.green() < seuil
                or couleur.blue() < seuil
            ):
                if x < gauche:
                    gauche = x
                if x > droite:
                    droite = x
                if y < haut:
                    haut = y
                if y > bas:
                    bas = y

    if droite <= gauche or bas <= haut:
        return None

    return gauche, haut, droite - gauche + 1, bas - haut + 1


def preparer(chemin_source):

    image = QImage(str(chemin_source))

    if image.isNull():
        return None, "Image illisible."

    image = image.convertToFormat(QImage.Format.Format_ARGB32)

    zone = cadre_utile(image)

    if zone is None:
        return None, "Image entierement blanche."

    x, y, largeur, hauteur = zone

    recadree = image.copy(x, y, largeur, hauteur)

    # Marge blanche autour, pour que le logo ne touche pas
    # le bord de la pastille.
    marge = int(max(largeur, hauteur) * MARGE)

    plein_largeur = largeur + 2 * marge
    plein_hauteur = hauteur + 2 * marge

    pastille = QImage(
        plein_largeur, plein_hauteur, QImage.Format.Format_ARGB32
    )
    pastille.fill(Qt.GlobalColor.transparent)

    peintre = QPainter(pastille)
    peintre.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rayon = plein_largeur * ARRONDI

    chemin = QPainterPath()
    chemin.addRoundedRect(
        QRectF(0, 0, plein_largeur, plein_hauteur), rayon, rayon
    )

    peintre.setClipPath(chemin)
    peintre.fillRect(pastille.rect(), QColor("#ffffff"))
    peintre.drawImage(marge, marge, recadree)
    peintre.end()

    finale = pastille.scaledToWidth(
        LARGEUR_FINALE, Qt.TransformationMode.SmoothTransformation
    )

    return finale, None


def main():

    application = QApplication(sys.argv)

    if len(sys.argv) > 1:
        source = sys.argv[1]
    else:
        source, _filtre = QFileDialog.getOpenFileName(
            None,
            "Choisis ton fichier logo",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )

    if not source:
        return

    finale, erreur = preparer(source)

    if erreur:
        QMessageBox.warning(None, "Logo", erreur)
        return

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    finale.save(str(DESTINATION), "PNG")

    QMessageBox.information(
        None,
        "Logo pret",
        f"Logo enregistre : {DESTINATION}\n\n"
        f"Taille : {finale.width()} x {finale.height()} px\n\n"
        "Relance le logiciel pour le voir dans le menu."
    )


if __name__ == "__main__":
    main()