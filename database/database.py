import sqlite3
from pathlib import Path

from database.schema import SCHEMA


class Database:

    def __init__(self):

        db_path = Path(__file__).parent / "poplicence.db"

        print("Base SQLite :", db_path)

        self.conn = sqlite3.connect(db_path)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.creer_tables()

    def creer_tables(self):

        for table, colonnes in SCHEMA.items():

            sql = self.generer_create_table(table, colonnes)

            self.cursor.execute(sql)

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