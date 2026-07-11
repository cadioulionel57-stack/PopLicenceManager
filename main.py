import sys
import traceback

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale

try:
    print("1")
    from database.init_database import initialiser

    print("2")
    from ui.main_window import MainWindow

    print("3")
    initialiser()

    print("4")
    app = QApplication(sys.argv)

    # Force le point comme séparateur décimal partout dans
    # le logiciel (champs poids, prix, marge...) — sans ça,
    # les champs numériques suivent la langue de Windows et
    # attendent une virgule ; taper un point dedans produit
    # alors une valeur fausse sans aucun message d'erreur.
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

    print("5")
    window = MainWindow()

    print("6")
    window.show()

    print("7")
    sys.exit(app.exec())

except Exception:
    traceback.print_exc()