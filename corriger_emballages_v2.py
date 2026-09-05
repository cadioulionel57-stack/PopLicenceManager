import sqlite3, shutil, datetime, os

CHEMIN = "database/poplicence.db"

sauvegarde = CHEMIN + ".avant_emballages_" + datetime.datetime.now().strftime("%Y%m%d_%H%M")
shutil.copy(CHEMIN, sauvegarde)
print("Sauvegarde :", os.path.basename(sauvegarde))
print()

c = sqlite3.connect(CHEMIN)
c.row_factory = sqlite3.Row

print("=== 1. FICHES DE TEST ===")
n = c.execute("delete from produits where nom like '%Albator%'").rowcount
print(f"  {n} fiche(s) Albator supprimee(s)")

print()
print("=== 2. SACS KRAFT -> GRILLE CADEAU ===")
for code, nom, cout in [("K1", "Sac kraft brun 24x12x31", 0.28),
                        ("K2", "Sac kraft brun 32x12x41", 0.33)]:
    deja = c.execute("select id from grille_emballage_cadeau where code=?", (code,)).fetchone()
    if deja:
        print(f"  {code} deja dans la grille cadeau")
    else:
        c.execute("insert into grille_emballage_cadeau (code, nom, cout_ht, type, tarif_facture_ht, actif) "
                  "values (?,?,?,'principal',2.42,1)", (code, nom, cout))
        print(f"  {code} ajoute a la grille cadeau")
    c.execute("update grille_emballage set actif=0 where code=?", (code,))
    print(f"  {code} retire des emballages d'expedition")

print()
print("=== 3. POCHETTES P3 / P4 ===")
c.execute("update grille_emballage set type_emballage='souple', poids_max_g=4000 where code='P4'")
print("  P4 (35x45) : souple, poids max 4 kg")
c.execute("update grille_emballage set type_emballage='souple', poids_max_g=8000 where code='P3'")
print("  P3 (55x77) : souple, poids max 8 kg")

c.commit()

print()
print("=== 4. REATTRIBUTION DES EMBALLAGES ===")
grille = [dict(r) for r in c.execute(
    "select * from grille_emballage where actif=1 and poids_max_g is not null")]

def choisir(L, l, h, poids_kg):
    dims = sorted([L or 0, l or 0, h or 0], reverse=True)
    poids_g = (poids_kg or 0) * 1000
    ok = []
    for e in grille:
        marge = 0 if e["type_emballage"] == "souple" else 1
        de = sorted([e["longueur_ext_cm"], e["largeur_ext_cm"], e["hauteur_ext_cm"]], reverse=True)
        if all(ce >= cp + marge for ce, cp in zip(de, dims)) and e["poids_max_g"] >= poids_g:
            ok.append(e)
    ok.sort(key=lambda e: e["longueur_ext_cm"] * e["largeur_ext_cm"] * e["hauteur_ext_cm"])
    return ok[0] if ok else None

modifies = 0
sans = []
for r in c.execute("""select p.id, p.nom, p.longueur, p.largeur, p.hauteur, p.poids,
                             g.code ancien
                      from produits p left join grille_emballage g on g.id = p.emballage_id
                      where coalesce(p.longueur,0) > 0 and coalesce(p.poids,0) > 0""").fetchall():
    nouveau = choisir(r["longueur"], r["largeur"], r["hauteur"], r["poids"])
    if nouveau is None:
        sans.append(r["nom"])
        continue
    if nouveau["code"] != r["ancien"]:
        c.execute("update produits set emballage_id=? where id=?", (nouveau["id"], r["id"]))
        print(f"  {r['nom'][:46]:48} {str(r['ancien']):>4} -> {nouveau['code']}")
        modifies += 1

c.commit()

print()
print(f"  {modifies} produit(s) corrige(s)")
if sans:
    print()
    print("  ATTENTION, aucun emballage possible pour :")
    for nom in sans:
        print("   -", nom)
print()
print("Termine.")