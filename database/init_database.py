from database.database import Database
from database.seed import Seeder

from modules.numerotation_manager import NumerotationManager


def initialiser():

    Database()

    NumerotationManager().initialiser()

    Seeder().executer()