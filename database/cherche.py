import sqlite3
c = sqlite3.connect('poplicence.db')
for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    nom = t[0]
    cols = [x[1] for x in c.execute(f"PRAGMA table_info({nom})")]
    for col in cols:
        try:
            n = c.execute(f"SELECT COUNT(*) FROM {nom} WHERE {col} LIKE '%Bretelles ajustables%'").fetchone()[0]
            if n:
                print(nom, col, n)
        except Exception:
            pass
