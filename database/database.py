import sqlite3
import sys
from pathlib import Path

from database.schema import SCHEMA

# Enrichit SCHEMA avec les tables de variations. L'import
# doit rester ici : c'est le seul endroit traversé par tous
# les points d'entrée du logiciel, donc la seule garantie
# que les tables existent quoi qu'il arrive.
import database.schema_variations  # noqa: F401
import database.schema_templates   # noqa: F401


def chemin_base():
    """
    Renvoie le chemin du fichier poplicence.db.

    Deux situations, et une seule règle : la base est
    toujours À CÔTÉ du programme qui tourne.

    - Lancé normalement (python main.py), le programme est
      le dossier du projet : la base est dans
      database/poplicence.db, comme depuis toujours.

    - Lancé en version compilée (.exe), les fichiers .py
      n'existent plus sur le disque, ils sont enfermés dans
      l'exécutable. Le chemin calculé à partir de ce fichier
      ne mène donc nulle part, et la base est introuvable.
      On repart alors du dossier de l'exe lui-même, où le
      dossier database est copié à côté.
    """

    if getattr(sys, "frozen", False):
        # sys.executable = le chemin de l'exe en cours.
        return Path(sys.executable).parent / "database" / "poplicence.db"

    return Path(__file__).parent / "poplicence.db"


class Database:

    def __init__(self):

        db_path = chemin_base()

        # timeout=30 : si une autre partie du logiciel est en
        # train d'ecrire, on ATTEND notre tour au lieu
        # d'abandonner aussitot.
        self.conn = sqlite3.connect(db_path, timeout=30)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        # WAL : les lectures ne bloquent plus les ecritures.
        self.cursor.execute("PRAGMA journal_mode = WAL")

        self.cursor.execute("PRAGMA busy_timeout = 30000")

        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.creer_tables()
        self.migrer_colonnes()
        self.reparer_codes_vides()

    def creer_tables(self):

        for table, colonnes in SCHEMA.items():

            sql = self.generer_create_table(table, colonnes)

            self.cursor.execute(sql)

        self.conn.commit()

    def migrer_colonnes(self):
        """
        Ajoute automatiquement les colonnes qui existent
        dans le schéma mais pas encore dans la base
        existante, SANS jamais supprimer ni modifier les
        données déjà présentes.
        """

        for table, colonnes in SCHEMA.items():

            try:
                infos = self.cursor.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall()
            except sqlite3.OperationalError:
                continue

            colonnes_existantes = {info[1] for info in infos}

            for nom, type_colonne in colonnes:

                if nom in colonnes_existantes:
                    continue

                if "PRIMARY KEY" in type_colonne.upper():
                    continue

                try:
                    self.cursor.execute(
                        f"ALTER TABLE {table} "
                        f"ADD COLUMN {nom} {type_colonne}"
                    )
                except sqlite3.OperationalError:
                    pass

        self.conn.commit()

    def reparer_codes_vides(self):
        """
        Remet a vide (NULL) les EAN et SKU enregistres comme
        une chaine vide.

        Les colonnes ean et sku sont UNIQUES. SQLite accepte
        autant de valeurs absentes qu'on veut quand elles
        valent NULL, mais REFUSE deux chaines vides
        identiques. Un ancien produit sans code-barres
        empechait donc d'en enregistrer un second : l'ecriture
        etait refusee, et la fiche en cours de saisie perdue.
        """

        try:
            self.cursor.execute(
                "UPDATE produits SET ean = NULL "
                "WHERE ean IS NOT NULL AND TRIM(ean) = ''"
            )
            self.cursor.execute(
                "UPDATE produits SET sku = NULL "
                "WHERE sku IS NOT NULL AND TRIM(sku) = ''"
            )
            self.conn.commit()

        except Exception:
            self.conn.rollback()

    def generer_create_table(self, table, colonnes):

        definition = []

        for nom, type_colonne in colonnes:

            definition.append(f"{nom} {type_colonne}")

        sql = f"""
        CREATE TABLE IF NOT EXISTS {table}
        (
            {', '.join(definition)}
        )
        """

        return sql

    def executer(self, sql, parametres=()):
        """
        Execute une ecriture et la valide.

        EN CAS D'ERREUR, la transaction est ANNULEE avant que
        l'erreur ne remonte. Sans cela, une ecriture refusee
        laissait une transaction ouverte, et la base restait
        VERROUILLEE pour tout le reste de la session : la
        fenetre d'enregistrement se figeait indefiniment, sans
        message, et la saisie etait perdue.
        """

        try:
            self.cursor.execute(sql, parametres)
            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

        return self.cursor

    def lire(self, sql, parametres=()):

        self.cursor.execute(sql, parametres)

        return self.cursor.fetchall()

    def lire_un(self, sql, parametres=()):

        self.cursor.execute(sql, parametres)

        return self.cursor.fetchone()

    def fermer(self):

        self.conn.close()