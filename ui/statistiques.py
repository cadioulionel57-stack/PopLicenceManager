from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
)
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
)
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

from modules.commande_manager import CommandeManager


class StatistiquesPage(QWidget):
    """
    Graphiques de pilotage — pour l'instant, la répartition
    du CA par canal de vente, mois par mois.
    """

    COULEURS = [
        "#144b8b", "#1e7d32", "#e67e22", "#c0392b", "#8e44ad",
        "#0064d2", "#eaba00", "#0057a8", "#7b241c", "#16a085",
    ]

    def __init__(self):

        super().__init__()

        self.manager = CommandeManager()

        self.setStyleSheet("""
        QWidget{ background:#f4f7fb; font-family:'Segoe UI'; }
        QLabel#titre{ font-size:24px; font-weight:600; color:#0f2f5c; }
        QLabel#sousTitre{ font-size:15px; font-weight:600; color:#0f2f5c; }
        QFrame#card{
            background:white; border:1px solid #e1e8f0;
            border-radius:12px;
        }
        QComboBox{
            background:#f7f9fc; border:1px solid #d7e0ec;
            border-radius:7px; padding:6px 8px; font-size:10.5pt;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        entete = QHBoxLayout()
        titre = QLabel("📊 Statistiques")
        titre.setObjectName("titre")
        entete.addWidget(titre)
        entete.addStretch()
        layout.addLayout(entete)

        ####################################################
        # Répartition du CA par canal
        ####################################################

        carte = QFrame()
        carte.setObjectName("card")
        layoutCarte = QVBoxLayout(carte)

        entêteGraphique = QHBoxLayout()

        titreGraphique = QLabel("🥧 Répartition du CA par canal de vente")
        titreGraphique.setObjectName("sousTitre")
        entêteGraphique.addWidget(titreGraphique)

        entêteGraphique.addStretch()

        entêteGraphique.addWidget(QLabel("Mois :"))

        self.selecteurMois = QComboBox()
        self.selecteurMois.currentIndexChanged.connect(
            self.rafraichirCamembert
        )
        entêteGraphique.addWidget(self.selecteurMois)

        layoutCarte.addLayout(entêteGraphique)

        self.labelVide = QLabel(
            "Aucune commande pour ce mois — rien à répartir."
        )
        self.labelVide.setStyleSheet("color:#7f8c8d; padding:20px;")
        layoutCarte.addWidget(self.labelVide)

        self.chartView = QChartView()
        self.chartView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chartView.setMinimumHeight(420)
        layoutCarte.addWidget(self.chartView)

        layout.addWidget(carte)

        ####################################################
        # Évolution du CA dans le temps
        ####################################################

        carteEvolution = QFrame()
        carteEvolution.setObjectName("card")
        layoutEvolution = QVBoxLayout(carteEvolution)

        entêteEvolution = QHBoxLayout()

        titreEvolution = QLabel("📈 Évolution du CA — mois par mois")
        titreEvolution.setObjectName("sousTitre")
        entêteEvolution.addWidget(titreEvolution)

        entêteEvolution.addStretch()

        entêteEvolution.addWidget(QLabel("Année :"))

        self.selecteurAnnee = QComboBox()
        self.selecteurAnnee.currentIndexChanged.connect(
            self.rafraichirEvolution
        )
        entêteEvolution.addWidget(self.selecteurAnnee)

        layoutEvolution.addLayout(entêteEvolution)

        self.chartViewEvolution = QChartView()
        self.chartViewEvolution.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        self.chartViewEvolution.setMinimumHeight(380)
        layoutEvolution.addWidget(self.chartViewEvolution)

        layout.addWidget(carteEvolution)

        layout.addStretch()

        self.charger()

    def charger(self):

        mois_disponibles = self.manager.mois_avec_commandes()

        self.selecteurMois.blockSignals(True)
        self.selecteurMois.clear()

        if not mois_disponibles:

            mois_disponibles = [date.today().strftime("%Y-%m")]

        for mois in mois_disponibles:
            self.selecteurMois.addItem(mois, mois)

        self.selecteurMois.blockSignals(False)

        self.rafraichirCamembert()

        annees_disponibles = self.manager.annees_disponibles()

        self.selecteurAnnee.blockSignals(True)
        self.selecteurAnnee.clear()

        if not annees_disponibles:
            annees_disponibles = [str(date.today().year)]

        for annee in annees_disponibles:
            self.selecteurAnnee.addItem(annee, annee)

        self.selecteurAnnee.blockSignals(False)

        self.rafraichirEvolution()

    def rafraichirEvolution(self):

        annee = self.selecteurAnnee.currentData()

        if annee is None:
            return

        donnees = self.manager.ca_par_mois_annee(annee)

        mois = [d["mois"] for d in donnees]
        valeurs = [d["ca_ht"] for d in donnees]

        barSet = QBarSet("CA HT")
        barSet.append(valeurs)
        barSet.setColor(QColor("#144b8b"))

        series = QBarSeries()
        series.append(barSet)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"CA mensuel — {annee}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(False)

        axeX = QBarCategoryAxis()
        axeX.append(mois)
        chart.addAxis(axeX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axeX)

        valeur_max = max(valeurs) if valeurs else 100

        axeY = QValueAxis()
        axeY.setRange(0, valeur_max * 1.15 if valeur_max > 0 else 100)
        axeY.setLabelFormat("%.0f €")
        chart.addAxis(axeY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axeY)

        self.chartViewEvolution.setChart(chart)

    def rafraichirCamembert(self):

        mois = self.selecteurMois.currentData()

        if mois is None:
            return

        donnees = self.manager.ca_par_canal(mois)

        if not donnees:

            self.labelVide.setVisible(True)
            self.chartView.setVisible(False)
            return

        self.labelVide.setVisible(False)
        self.chartView.setVisible(True)

        series = QPieSeries()

        for i, item in enumerate(donnees):

            tranche = series.append(
                f"{item['canal']} ({item['ca_ht']:.0f} € HT)",
                item["ca_ht"]
            )
            tranche.setLabelVisible(True)
            tranche.setColor(QColor(self.COULEURS[i % len(self.COULEURS)]))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Répartition du CA — {mois}")

        titleFont = QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(11)
        chart.setTitleFont(titleFont)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.chartView.setChart(chart)