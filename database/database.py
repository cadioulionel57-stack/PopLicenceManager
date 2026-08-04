import sqlite3
from pathlib import Path

from database.schema import SCHEMA

# Enrichit SCHEMA avec les tables de variations. L'import
# doit rester ici : c'est le seul endroit traversé par tous
# les points d'entrée du logiciel, donc la seule garantie
# que les tables existent quoi qu'il arrive.
import database.schema_variations  # noqa: F401
import database.schema_templates   # noqa: F401


class Database:

    def __init__(self):

        db_path = Path(__file__).parent / "poplicence.db"

        # timeout=30 : si une autre partie du logiciel est en
        # train d'ecrire, on ATTEND notre tour jusqu'a trente
        # secondes au lieu d'abandonner au bout de cinq.
        self.conn = sqlite3.connect(db_path, timeout=30)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        # WAL : les lectures ne bloquent plus les ecritures.
        # C'est ce qui faisait echouer un enregistrement de
        # fiche produit quand un autre ecran consultait la
        # base au meme instant — l'erreur "database is locked".
        self.cursor.execute("PRAGMA journal_mode = WAL")

        # Filet supplementaire, cote moteur SQLite lui-meme.
        self.cursor.execute("PRAGMA busy_timeout = 30000")

        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.creer_tables()
        self.migrer_colonnes()

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

        C'est ce qui permet de faire évoluer le logiciel
        sans avoir à supprimer poplicence.db à chaque
        changement de structure.
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

        self.cursor.execute(sql, parametres)

        self.conn.commit()

        return self.cursor

    def lire(self, sql, parametres=()):

        self.cursor.execute(sql, parametres)

        return self.cursor.fetchall()

    def lire_un(self, sql, parametres=()):

        self.cursor.execute(sql, parametres)

        return self.cursor.fetchone()

    def fermer(self):

        self.conn.close()