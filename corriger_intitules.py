import shutil
from pathlib import Path

# ----------------------------------------------------------
# Onglet Tarification : n'afficher que les canaux
# réellement pertinents pour le produit.
#
#   1. Un produit EN STOCK ne voit plus BigBuy ni Direct
#      Fournisseur. Un produit DIRECT FOURNISSEUR ne voit
#      qu'eux.
#
#   2. Une marketplace sur laquelle le produit est refusé
#      (prix sous le minimum du canal) est masquée : elle
#      n'a rien à faire dans la liste.
# ----------------------------------------------------------

FICHIER = "ui/tabs/tab_tarification.py"

REMPLACEMENTS = [

    (
        '        canaux = CanalManager().tous()\n'
        '\n'
        '        return [\n'
        '            c for c in canaux\n'
        '            if c["type"] != "marketplace" or self.type_produit == "stock"\n'
        '        ]\n',

        '        canaux = CanalManager().tous()\n'
        '\n'
        '        # Canaux de dropshipping : le fournisseur\n'
        '        # expédie lui-même. Ils n\'ont aucun sens pour un\n'
        '        # produit tenu en stock, et inversement le stock\n'
        '        # n\'a rien à faire sur ces canaux-là.\n'
        '        DROPSHIPPING = ("bigbuy", "direct fournisseur", "dropshipping")\n'
        '\n'
        '        retenus = []\n'
        '\n'
        '        for canal in canaux:\n'
        '\n'
        '            est_drop = any(\n'
        '                mot in canal["nom"].strip().lower()\n'
        '                for mot in DROPSHIPPING\n'
        '            )\n'
        '\n'
        '            if self.type_produit == "dropshipping":\n'
        '\n'
        '                # Direct fournisseur : ses canaux propres,\n'
        '                # plus le Site. Jamais de marketplace.\n'
        '                if est_drop or canal["type"] == "site":\n'
        '                    retenus.append(canal)\n'
        '\n'
        '                continue\n'
        '\n'
        '            if est_drop:\n'
        '                continue\n'
        '\n'
        '            if canal["type"] == "marketplace" and self.type_produit != "stock":\n'
        '                continue\n'
        '\n'
        '            retenus.append(canal)\n'
        '\n'
        '        return retenus\n'
    ),

    (
        '        self._comparerCanauxSimilaires(canaux)\n'
        '\n'
        '        # Tous les canaux visibles d\'un coup, sans défilement\n'
        '        # interne : c\'est ici qu\'on fixe la hauteur du tableau\n'
        '        # sur son contenu réel.\n'
        '        self._ajusterHauteur()\n',

        '        self._comparerCanauxSimilaires(canaux)\n'
        '\n'
        '        self._masquerCanauxRefuses()\n'
        '\n'
        '        # Tous les canaux visibles d\'un coup, sans défilement\n'
        '        # interne : c\'est ici qu\'on fixe la hauteur du tableau\n'
        '        # sur son contenu réel.\n'
        '        self._ajusterHauteur()\n'
        '\n'
        '    def _masquerCanauxRefuses(self):\n'
        '        """\n'
        '        Masque les lignes des marketplaces sur lesquelles\n'
        '        le produit ne passe pas : prix calculé sous le\n'
        '        minimum du canal, ou transport trop lourd.\n'
        '\n'
        '        Le Site n\'est jamais masqué : c\'est la boutique,\n'
        '        elle reste toujours affichée.\n'
        '        """\n'
        '\n'
        '        for ligne, canal_id in self.ligneVersCanal.items():\n'
        '\n'
        '            resultat = self.derniersResultats.get(canal_id)\n'
        '\n'
        '            if resultat is None:\n'
        '                continue\n'
        '\n'
        '            canal = self.canaux.obtenir(canal_id)\n'
        '\n'
        '            if canal is None or canal["type"] != "marketplace":\n'
        '                continue\n'
        '\n'
        '            refuse = bool(resultat.get("erreur"))\n'
        '\n'
        '            if not refuse:\n'
        '                decision = resultat.get("decision", "")\n'
        '                refuse = decision.startswith("🔴")\n'
        '\n'
        '            self.table.setRowHidden(ligne, refuse)\n'
    ),

]

# ----------------------------------------------------------
# Contrôle AVANT écriture
# ----------------------------------------------------------

fichier = Path(FICHIER)

if not fichier.exists():
    print("fichier introuvable :", FICHIER)
    raise SystemExit

texte = fichier.read_text(encoding="utf-8")

if "_masquerCanauxRefuses" in texte:
    print("Déjà corrigé, rien à faire.")
    raise SystemExit

anomalies = []

for ancien, _nouveau in REMPLACEMENTS:

    if texte.count(ancien) != 1:
        anomalies.append(
            f"bloc trouvé {texte.count(ancien)} fois : "
            + ancien.strip().split("\n")[0][:55]
        )

if anomalies:

    print("ARRÊT — RIEN n'a été modifié :")
    print()

    for anomalie in anomalies:
        print("   ", anomalie)

    raise SystemExit

shutil.copy(FICHIER, FICHIER + ".avant_filtre")

for ancien, nouveau in REMPLACEMENTS:
    texte = texte.replace(ancien, nouveau)

fichier.write_text(texte, encoding="utf-8")

print("corrigé :", FICHIER)
print()
print("Produit EN STOCK      -> Site + marketplaces, sans BigBuy")
print("Produit DIRECT FOURN. -> Site + BigBuy + Direct Fournisseur")
print("Marketplace en rouge  -> ligne masquée")