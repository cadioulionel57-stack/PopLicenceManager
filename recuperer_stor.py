# -*- coding: utf-8 -*-
# Recuperation automatique des images, du poids et des dimensions
# des 44 references Stor, et generation du CSV d'import PopLicenceManager.

import csv, re, html, time, os, urllib.request

DONNEES = """
8412497317868|Mug thermor\xe9actif Stitch Aloha 325 ml|Stitch|31786|7,14|12|Mugs|Template STOCK Mugs Vaisselle|https://storline.com/es/tazas/1686-taza-ceramica-325-ml-changing-color-en-caja-regalo-stitch-aloha-8412497317868.html
8412497310661|Mug thermor\xe9actif Harry Potter Magic & Mayhem 325 ml|Harry Potter|31066|7,14|12|Mugs|Template STOCK Mugs Vaisselle|https://storline.com/es/tazas/1549-taza-ceramica-325-ml-changing-color-en-caja-regalo-harry-potter-magic-mayhem-8412497310661.html
8412497316663|Mug thermor\xe9actif Pok\xe9mon Metal Meltdown 325 ml|Pok\xe9mon|31666|7,14|12|Mugs|Template STOCK Mugs Vaisselle|https://storline.com/es/tazas/1659-taza-ceramica-325-ml-changing-color-en-caja-regalo-pokemon-metal-meltdown-8412497316663.html
8412497787401|Mug thermor\xe9actif Super Mario 325 ml|Super Mario|78740|7,14|12|Mugs|Template STOCK Mugs Vaisselle|https://storline.com/es/tazas/1727-taza-ceramica-325-ml-changing-color-en-caja-regalo-super-mario-inlc-8412497787401.html
8412497317097|Gourde isotherme en inox Stitch Aloha 515 ml|Stitch|31709|12,86|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas/1669-botella-termo-acero-inoxidable-515-ml-stitch-aloha--8412497317097.html
8412497310098|Gourde isotherme en inox Harry Potter Magic & Mayhem 515 ml|Harry Potter|31009|12,86|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas/1537-botella-termo-acero-inoxidable-515-ml-harry-potter-magic-mayhem-8412497310098.html
8412497317646|Bol \xe0 ramen avec baguettes Stitch Aloha|Stitch|31764|11,04|6|Bols|Template STOCK Mugs Vaisselle|https://storline.com/es/cuencos/1683-cuenco-ramen-con-palillos-en-caja-regalo-stitch-aloha-8412497317646.html
8412497798339|Boule \xe0 neige en verre Harry Potter|Harry Potter|79833|5,53|6|Boules \xe0 neige|Template STOCK D\xe9corations|https://storline.com/es/bolas-nieve/1353-globo-de-nieve-harry-potter-en-caja-de-regalo-8412497798339.html
8412497798322|Boule \xe0 neige en verre Stitch|Stitch|79832|5,53|6|Boules \xe0 neige|Template STOCK D\xe9corations|https://storline.com/es/bolas-nieve/1352-globo-de-nieve-stitch-en-caja-de-regalo-8412497798322.html
8412497798308|Boule \xe0 neige en verre Mickey|Mickey|79830|5,53|6|Boules \xe0 neige|Template STOCK D\xe9corations|https://storline.com/es/bolas-nieve/1350-globo-de-nieve-mickey-en-caja-de-regalo-8412497798308.html
8412497004072|Mug petit-d\xe9jeuner Dragon Ball 400 ml|Dragon Ball|407|5,84|12|Mugs|Template STOCK Mugs Vaisselle|https://storline.com/es/tazas/11-taza-ceramica-desayuno-400-ml-en-caja-regalo-dragon-ball-8412497004072.html
8412497101092|Gourde figurine 3D Bluey 560 ml|Bluey|10109|5,41|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas-cantimploras-infantiles/1181-botella-figurita-3d-560-ml-bluey-8412497101092.html
8412497816545|Gourde figurine 3D Pat' Patrouille Rescue Pups 560 ml|Pat Patrouille|81654|5,41|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas-cantimploras-infantiles/803-botella-figurita-3d-560-ml-paw-patrol-boy-rescue-pups-8412497816545.html
8412497835546|Gourde figurine 3D Spider-Man Moving Target 560 ml|Spider-Man|83554|5,41|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas-cantimploras-infantiles/924-botella-figurita-3d-560-ml-spiderman-moving-target-8412497835546.html
8412497810543|Gourde figurine 3D La Reine des Neiges Snowy Tale 560 ml|La Reine des Neiges|81054|5,41|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas-cantimploras-infantiles/672-botella-figurita-3d-560-ml-frozen-snowy-tale-8412497810543.html
8412497748600|Gourde figurine 3D Stitch Flowers 560 ml|Stitch|74860|5,41|6|Gourdes|Template STOCK Mugs Vaisselle|https://storline.com/es/botellas-cantimploras-infantiles/1269-botella-figurita-3d-560-ml-stitch-flowers-8412497748600.html
8412497506378|Bo\xeete \xe0 go\xfbter multi-compartiments Bluey|Bluey|50637|3,88|6|Lunch box|Template STOCK Mugs Vaisselle|https://storline.com/es/sandwicheras-fiambreras-infantiles/454-sandwichera-multiple-suprema-bluey-8412497506378.html
8412497816378|Bo\xeete \xe0 go\xfbter multi-compartiments Pat' Patrouille Rescue Pups|Pat Patrouille|81637|3,88|6|Lunch box|Template STOCK Mugs Vaisselle|https://storline.com/es/sandwicheras-fiambreras-infantiles/790-sandwichera-multiple-suprema-paw-patrol-boy-rescue-pups-8412497816378.html
8412497835379|Bo\xeete \xe0 go\xfbter multi-compartiments Spider-Man Moving Target|Spider-Man|83537|3,88|6|Lunch box|Template STOCK Mugs Vaisselle|https://storline.com/es/sandwicheras-fiambreras-infantiles/911-sandwichera-multiple-suprema-spiderman-moving-target-8412497835379.html
8412497750375|Bo\xeete \xe0 go\xfbter multi-compartiments Stitch Drawing|Stitch|75037|3,88|6|Lunch box|Template STOCK Mugs Vaisselle|https://storline.com/es/sandwicheras-fiambreras-infantiles/1106-sandwichera-multiple-suprema-stitch-drawing-8412497750375.html
8412497808373|Bo\xeete \xe0 go\xfbter multi-compartiments Pok\xe9mon Blue Team|Pok\xe9mon|80837|3,88|6|Lunch box|Template STOCK Mugs Vaisselle|https://storline.com/es/sandwicheras-fiambreras-infantiles/1749-sandwichera-multiple-suprema-pokemon-blue-team-8412497808373.html
8412497212507|Set de vaisselle 5 pi\xe8ces Gabby et la Maison Magique|Gabby|21250|5,11|6|Sets de vaisselle|Template STOCK Mugs Vaisselle|https://storline.com/es/vajillas-infantiles/294-set-micro-5-pcs-plato-cuenco-vaso-y-cubiertos-en-caja-gabby-s-dollhouse-bab-8412497212507.html
8412497818501|Set de vaisselle 5 pi\xe8ces Pat' Patrouille Superpowers|Pat Patrouille|81850|5,11|6|Sets de vaisselle|Template STOCK Mugs Vaisselle|https://storline.com/es/vajillas-infantiles/852-set-micro-5-pcs-plato-cuenco-vaso-y-cubiertos-en-caja-paw-patrol-girl-superpowers-8412497818501.html
8412497812509|Set de vaisselle 5 pi\xe8ces Minnie Bold Florals|Minnie|81250|5,11|6|Sets de vaisselle|Template STOCK Mugs Vaisselle|https://storline.com/es/vajillas-infantiles/742-set-micro-5-pcs-plato-cuenco-vaso-y-cubiertos-en-caja-minnie-bold-florals-8412497812509.html
8412497752508|Set de vaisselle 5 pi\xe8ces Super Mario|Super Mario|75250|5,11|6|Sets de vaisselle|Template STOCK Mugs Vaisselle|https://storline.com/es/vajillas-infantiles/1274-set-micro-5-pcs-plato-cuenco-vaso-y-cubiertos-en-caja-super-mario-8412497752508.html
8412497409457|Tirelire m\xe9tallique Bluey|Bluey|40945|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/388-hucha-metalica-bluey-8412497409457.html
8412497448456|Tirelire m\xe9tallique Dragon Ball Super|Dragon Ball|44845|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/411-hucha-metalica-dragon-ball-super-8412497448456.html
8412497449354|Tirelire m\xe9tallique La Reine des Neiges|La Reine des Neiges|44935|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/417-hucha-metalica-frozen-autumn-leaves-8412497449354.html
8412497449057|Tirelire m\xe9tallique Gabby et la Maison Magique|Gabby|44905|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/415-hucha-metalica-gabby-s-dollhouse-8412497449057.html
8412497450053|Tirelire m\xe9tallique Hello Kitty|Hello Kitty|45005|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/422-hucha-metalica-hello-kitty-8412497450053.html
8412497450152|Tirelire m\xe9tallique Kuromi|Kuromi|45015|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/423-hucha-metalica-kuromi-8412497450152.html
8412497449453|Tirelire m\xe9tallique Mickey|Mickey|44945|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/418-hucha-metalica-mickey-has-fun-8412497449453.html
8412497447459|Tirelire m\xe9tallique Minecraft|Minecraft|44745|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/407-hucha-metalica-minecraft-8412497447459.html
8412497449552|Tirelire m\xe9tallique Minnie|Minnie|44955|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/419-hucha-metalica-minnie-bold-florals-8412497449552.html
8412497409358|Tirelire m\xe9tallique One Piece|One Piece|40935|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/387-hucha-metalica-one-piece-8412497409358.html
8412497449651|Tirelire m\xe9tallique Pat' Patrouille|Pat Patrouille|44965|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/420-hucha-metalica-paw-patrol-boy-rescue-pups-8412497449651.html
8412497447756|Tirelire m\xe9tallique Peppa Pig|Peppa Pig|44775|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/408-hucha-metalica-peppa-pig-kindness-counts-8412497447756.html
8412497448258|Tirelire m\xe9tallique Pok\xe9mon|Pok\xe9mon|44825|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/410-hucha-metalica-pokemon-distortion-8412497448258.html
8412497449859|Tirelire m\xe9tallique Disney Princesses|Disney Princesses|44985|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/421-hucha-metalica-princess-be-youtiful-8412497449859.html
8412497448753|Tirelire m\xe9tallique Sonic|Sonic|44875|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/413-hucha-metalica-sonic-8412497448753.html
8412497449255|Tirelire m\xe9tallique Spider-Man|Spider-Man|44925|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/416-hucha-metalica-spiderman-mob-rules-8412497449255.html
8412497448951|Tirelire m\xe9tallique Stitch|Stitch|44895|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/414-hucha-metalica-stitch-palms-8412497448951.html
8412497447954|Tirelire m\xe9tallique Super Mario|Super Mario|44795|1,33|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/409-hucha-metalica-supermario-8412497447954.html
8412497448654|Tirelire m\xe9tallique Licorne||44865|1,13|6|Tirelires|Template STOCK D\xe9corations|https://storline.com/es/huchas/412-hucha-metalica-unicorn-8412497448654.html
"""

FOURNISSEUR = "Stor"
FAMILLE = "Objets - mugs, vaisselle, papeterie, figurines, d\xe9co, jeux"
NAVIGATEUR = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

COLONNES = ["type_produit", "ean", "nom", "marque", "fournisseur",
            "reference_fournisseur", "prix_fournisseur_ht", "taux_tva_achat",
            "quantite_stock", "categorie_site", "theme_template",
            "famille_produit", "longueur", "largeur", "hauteur", "poids",
            "image_principale", "image_2", "image_3", "statut_stock",
            "eligible_papier_cadeau", "fiche_a_terminer", "url_fiche_stor"]


def telecharger(adresse):
    requete = urllib.request.Request(adresse, headers={"User-Agent": NAVIGATEUR})
    with urllib.request.urlopen(requete, timeout=40) as reponse:
        return reponse.read().decode("utf-8", "ignore")


def extraire_images(page):
    """Les 3 premieres images de la galerie du produit."""
    trouvees = re.findall(
        r"https://storline\.com/(\d+)-(?:medium|superlarge)_default/([A-Za-z0-9_\-]+)\.jpg",
        page)
    retenues = []
    vues = set()
    for identifiant, morceau in trouvees:
        if identifiant not in vues:
            vues.add(identifiant)
            retenues.append("https://storline.com/%s-large_default/%s.jpg"
                            % (identifiant, morceau))
    while len(retenues) < 3:
        retenues.append("")
    return retenues[:3]


def texte_brut(page):
    sans = re.sub(r"<script.*?</script>", " ", page, flags=re.S)
    sans = re.sub(r"<style.*?</style>", " ", sans, flags=re.S)
    sans = re.sub(r"<[^>]+>", " ", sans)
    return re.sub(r"\s+", " ", html.unescape(sans))


def mesure(texte, etiquette):
    trouve = re.search(re.escape(etiquette) + r"\s*([0-9]+(?:[.,][0-9]+)?)", texte)
    if not trouve:
        return ""
    return trouve.group(1).replace(".", ",")


def poids_en_kilos(texte):
    grammes = mesure(texte, "Peso (gr)")
    if not grammes:
        return ""
    return ("%.3f" % (float(grammes.replace(",", ".")) / 1000)).replace(".", ",")


def main():
    dossier = os.path.dirname(os.path.abspath(__file__))
    sortie = os.path.join(dossier, "Import_Produits_Stor.csv")

    lignes = [l for l in DONNEES.strip().split("\n") if l.strip()]
    resultats = []
    sans_image = 0
    sans_mesure = 0

    print("%d produits a traiter." % len(lignes))
    print("")

    for numero, ligne in enumerate(lignes, start=1):
        (ean, nom, marque, reference, prix, quantite,
         categorie, theme, adresse) = ligne.split("|")

        images = ["", "", ""]
        longueur = largeur = hauteur = poids = ""

        try:
            page = telecharger(adresse)
            images = extraire_images(page)
            texte = texte_brut(page)
            longueur = mesure(texte, "Largo (cm)")
            largeur = mesure(texte, "Ancho (cm)")
            hauteur = mesure(texte, "Alto (cm)")
            poids = poids_en_kilos(texte)
            etat = "%d image(s)" % len([i for i in images if i])
            if poids:
                etat = etat + " - poids " + poids + " kg"
            else:
                etat = etat + " - PAS DE FICHE TECHNIQUE"
        except Exception as erreur:
            etat = "ECHEC : %s" % erreur

        if not images[0]:
            sans_image = sans_image + 1
        if not poids:
            sans_mesure = sans_mesure + 1

        print("%2d/%d  ref %-6s  %s" % (numero, len(lignes), reference, etat))

        resultats.append({
            "type_produit": "stock",
            "ean": ean,
            "nom": nom,
            "marque": marque,
            "fournisseur": FOURNISSEUR,
            "reference_fournisseur": reference,
            "prix_fournisseur_ht": prix,
            "taux_tva_achat": "0",
            "quantite_stock": quantite,
            "categorie_site": categorie,
            "theme_template": theme,
            "famille_produit": FAMILLE,
            "longueur": longueur,
            "largeur": largeur,
            "hauteur": hauteur,
            "poids": poids,
            "image_principale": images[0],
            "image_2": images[1],
            "image_3": images[2],
            "statut_stock": "actif",
            "eligible_papier_cadeau": "1",
            "fiche_a_terminer": "1",
            "url_fiche_stor": adresse,
        })

        time.sleep(1)

    with open(sortie, "w", encoding="utf-8-sig", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=";")
        redacteur.writeheader()
        redacteur.writerows(resultats)

    print("")
    print("Fichier ecrit : %s" % sortie)
    print("Lignes : %d" % len(resultats))
    print("Sans image : %d" % sans_image)
    print("Sans poids/dimensions : %d" % sans_mesure)


main()