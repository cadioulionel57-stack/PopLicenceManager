import shutil
from pathlib import Path

# ----------------------------------------------------------
# Corrige DEUX fichiers d'un coup :
#
#   modules/moteur_prix.py       -> symboles distincts
#   ui/tabs/tab_tarification.py  -> couleurs + infobulles
#
# Les deux vont ensemble : l'écran choisit la couleur en
# lisant le symbole du texte. Changer l'un sans l'autre
# ferait passer TOUS les refus en vert.
# ----------------------------------------------------------

TRAVAUX = [

    ("modules/moteur_prix.py", [

        # Rouge = refus, orange = alerte. Deux problèmes
        # différents, deux symboles différents.
        (
            '        decision = "⛔ PRIX TROP BAS"\n',
            '        decision = "🔴 PRIX TROP BAS"\n'
        ),
        (
            '                decision = "⛔ PORT TROP CHER"\n',
            '                decision = "🟠 PORT TROP CHER"\n'
        ),

    ]),

    ("ui/tabs/tab_tarification.py", [

        # 1. Infobulle = le détail, plus la répétition du
        #    titre. Et couleur choisie sur les nouveaux
        #    symboles.
        (
            '        itemDecision = QTableWidgetItem(resultat["decision"])\n'
            '        itemDecision.setToolTip(resultat["decision"])\n'
            '\n'
            '        if resultat["decision"].startswith("❌"):\n'
            '            self._appliquerStyleAlerte(itemDecision, "erreur")\n'
            '        elif resultat["decision"].startswith("⚠️"):\n'
            '            self._appliquerStyleAlerte(itemDecision, "attention")\n'
            '        else:\n'
            '            self._appliquerStyleAlerte(itemDecision, "ok")\n',

            '        itemDecision = QTableWidgetItem(resultat["decision"])\n'
            '\n'
            '        # Infobulle : la phrase complète, que la\n'
            '        # colonne est trop étroite pour afficher.\n'
            '        itemDecision.setToolTip(\n'
            '            resultat.get("decision_detail")\n'
            '            or resultat["decision"]\n'
            '        )\n'
            '\n'
            '        self._appliquerStyleAlerte(\n'
            '            itemDecision,\n'
            '            self._niveauDecision(resultat["decision"])\n'
            '        )\n'
        ),

        # 2. Même test dans la mise à jour après saisie
        #    d'un prix marché.
        (
            '        if resultat["decision"].startswith("❌"):\n'
            '\n'
            '            itemDecision = QTableWidgetItem(resultat["decision"])\n'
            '            self._appliquerStyleAlerte(itemDecision, "erreur")\n'
            '            self.table.setItem(ligne, 6, itemDecision)\n'
            '            return\n',

            '        if self._niveauDecision(resultat["decision"]) == "erreur":\n'
            '\n'
            '            itemDecision = QTableWidgetItem(resultat["decision"])\n'
            '            itemDecision.setToolTip(\n'
            '                resultat.get("decision_detail")\n'
            '                or resultat["decision"]\n'
            '            )\n'
            '            self._appliquerStyleAlerte(itemDecision, "erreur")\n'
            '            self.table.setItem(ligne, 6, itemDecision)\n'
            '            return\n'
        ),

        # 3. FBA/FBM : une information, pas une alerte.
        (
            '                    itemDecision = QTableWidgetItem(\n'
            '                        f"⚠️ FBA plus cher que FBM (+{ecart:.2f}€)"\n'
            '                    )\n'
            '                    self._appliquerStyleAlerte(itemDecision, "attention")\n',

            '                    itemDecision = QTableWidgetItem(\n'
            '                        "💡 PRÉFÉRER FBM"\n'
            '                    )\n'
            '                    itemDecision.setToolTip(\n'
            '                        f"Le FBA revient {ecart:.2f}€ plus cher "\n'
            '                        f"que le FBM sur ce produit."\n'
            '                    )\n'
            '                    self._appliquerStyleAlerte(itemDecision, "info")\n'
        ),

        # 4. Le bleu pour l'information, et la fonction qui
        #    déduit le niveau du symbole.
        (
            '        if niveau == "erreur":\n'
            '            item.setBackground(QColor("#e74c3c"))\n'
            '        elif niveau == "attention":\n'
            '            item.setBackground(QColor("#f39c12"))\n'
            '        else:\n'
            '            item.setBackground(QColor("#27ae60"))\n',

            '        if niveau == "erreur":\n'
            '            item.setBackground(QColor("#e74c3c"))\n'
            '        elif niveau == "attention":\n'
            '            item.setBackground(QColor("#f39c12"))\n'
            '        elif niveau == "info":\n'
            '            item.setBackground(QColor("#2980b9"))\n'
            '        else:\n'
            '            item.setBackground(QColor("#27ae60"))\n'
            '\n'
            '    def _niveauDecision(self, decision):\n'
            '        """\n'
            '        Déduit la couleur du symbole placé en tête\n'
            '        de l\'intitulé.\n'
            '\n'
            '        🔴 refus  ·  🟠 alerte  ·  💡 information\n'
            '        ✅ tout va bien\n'
            '        """\n'
            '\n'
            '        if decision.startswith("🔴") or decision.startswith("❌"):\n'
            '            return "erreur"\n'
            '\n'
            '        if decision.startswith("🟠") or decision.startswith("⚠️"):\n'
            '            return "attention"\n'
            '\n'
            '        if decision.startswith("💡"):\n'
            '            return "info"\n'
            '\n'
            '        return "ok"\n'
        ),

    ]),

]

# ----------------------------------------------------------
# Contrôle complet AVANT toute écriture
# ----------------------------------------------------------

anomalies = []
contenus = {}

for chemin, remplacements in TRAVAUX:

    fichier = Path(chemin)

    if not fichier.exists():
        anomalies.append(f"fichier introuvable : {chemin}")
        continue

    texte = fichier.read_text(encoding="utf-8")
    contenus[chemin] = texte

    for ancien, _nouveau in remplacements:

        if texte.count(ancien) != 1:
            anomalies.append(
                f"{chemin} : bloc trouvé "
                f"{texte.count(ancien)} fois — "
                + ancien.strip().split("\n")[0][:50]
            )

if anomalies:

    print("ARRÊT — RIEN n'a été modifié :")
    print()

    for anomalie in anomalies:
        print("   ", anomalie)

    raise SystemExit

# ----------------------------------------------------------
# Sauvegarde puis écriture
# ----------------------------------------------------------

for chemin, remplacements in TRAVAUX:

    shutil.copy(chemin, chemin + ".avant_couleurs")

    texte = contenus[chemin]

    for ancien, nouveau in remplacements:
        texte = texte.replace(ancien, nouveau)

    Path(chemin).write_text(texte, encoding="utf-8")

    print("corrigé :", chemin)

print()
print("Colonne Décision :")
print("   ✅ À VENDRE ICI      fond vert")
print("   🔴 PRIX TROP BAS     fond rouge   (refus)")
print("   🟠 PORT TROP CHER    fond orange  (alerte)")
print("   💡 PRÉFÉRER FBM      fond bleu    (information)")
print()
print("Le détail complet s'affiche au survol de la souris.")