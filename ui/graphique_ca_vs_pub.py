from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
    QLineSeries,
)
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

from modules.budget_publicitaire_manager import BudgetPublicitaireManager


class GraphiqueCaVsPubWidget(QWidget):
    """
    Graphique CA du mois vs budget publicitaire dépensé,
    mois par mois — pour voir en un coup d'œil si plus de
    budget pub correspond à plus de ventes.
    """

    def __init__(self):

        super().__init__()

        self.manager = BudgetPublicitaireManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.labelVide = QLabel(
            "Aucune donnée pour l'instant — saisis au moins un "
            "mois de dépense publicitaire pour voir apparaître "
            "le graphique."
        )
        self.labelVide.setStyleSheet("color:#7f8c8d; padding:20px;")
        self.labelVide.setWordWrap(True)
        layout.addWidget(self.labelVide)

        self.chartView = QChartView()
        self.chartView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chartView.setMinimumHeight(320)
        self.chartView.setVisible(False)
        layout.addWidget(self.chartView)

        self.rafraichir()

    def rafraichir(self):

        donnees = self.manager.evolution_ca_vs_pub()

        if not donnees:
            self.labelVide.setVisible(True)
            self.chartView.setVisible(False)
            return

        self.labelVide.setVisible(False)
        self.chartView.setVisible(True)

        mois = [d["mois"] for d in donnees]
        depenses = [d["depense_pub_ht"] for d in donnees]
        cas = [d["ca_ht"] for d in donnees]

        setDepense = QBarSet("Budget pub dépensé (€ HT)")
        setDepense.append(depenses)
        setDepense.setColor(QColor("#e67e22"))

        setCa = QBarSet("CA du mois (€ HT)")
        setCa.append(cas)
        setCa.setColor(QColor("#144b8b"))

        series = QBarSeries()
        series.append(setDepense)
        series.append(setCa)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Évolution mensuelle : CA vs budget publicitaire")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        axeX = QBarCategoryAxis()
        axeX.append(mois)
        chart.addAxis(axeX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axeX)

        valeur_max = max(depenses + cas) if (depenses + cas) else 100

        axeY = QValueAxis()
        axeY.setRange(0, valeur_max * 1.15)
        axeY.setLabelFormat("%.0f €")
        chart.addAxis(axeY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axeY)

        self.chartView.setChart(chart)