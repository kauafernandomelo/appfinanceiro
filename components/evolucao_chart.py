import customtkinter as ctk
import matplotlib

matplotlib.use("Agg")
from datetime import datetime

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from constants import MESES_ABREV
from database import get_connection


class EvolucaoTemporalChart(ctk.CTkFrame):
    """Grafico de evolucao temporal (receitas vs despesas) compartilhado."""

    def __init__(self, master, colors=None, meses=6, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors or {}
        self.meses = meses
        self.canvas = None
        self._atualizar()

    def _atualizar(self):
        hoje = datetime.now()
        mes_atual = hoje.month
        ano_atual = hoje.year

        meses_lista = []
        for i in range(self.meses - 1, -1, -1):
            m = mes_atual - i
            y = ano_atual
            while m <= 0:
                m += 12
                y -= 1
            meses_lista.append(f"{y}-{m:02d}")

        with get_connection() as conn:
            rows = conn.execute("""
                SELECT strftime('%Y-%m', data) as mes,
                       SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as receita,
                       SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as despesa
                FROM (
                    SELECT valor, data, 'receita' as tipo FROM receitas
                    WHERE strftime('%Y-%m', data) IN ({})
                    UNION ALL
                    SELECT valor, data, 'despesa' as tipo FROM despesas
                    WHERE strftime('%Y-%m', data) IN ({})
                )
                GROUP BY mes
                ORDER BY mes
            """.format(",".join("?" * len(meses_lista)), ",".join("?" * len(meses_lista))),
                meses_lista + meses_lista
            ).fetchall()

        receitas_por_mes = {}
        despesas_por_mes = {}
        for r in rows:
            receitas_por_mes[r["mes"]] = r["receita"]
            despesas_por_mes[r["mes"]] = r["despesa"]

        labels = []
        rec_vals = []
        desp_vals = []
        for m in meses_lista:
            ano, mes_num = m.split("-")
            labels.append(MESES_ABREV.get(int(mes_num), m))
            rec_vals.append(receitas_por_mes.get(m, 0))
            desp_vals.append(despesas_por_mes.get(m, 0))

        self._renderizar(labels, rec_vals, desp_vals)

    def _renderizar(self, labels, rec_vals, desp_vals):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        fig = Figure(figsize=(6, 3), dpi=100, facecolor=self.colors.get("bg_card", "#1a1a2e"))
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors.get("bg_card", "#1a1a2e"))

        x = range(len(labels))
        ax.plot(x, rec_vals, color=self.colors.get("green", "#00b894"), linewidth=2, marker="o", markersize=5, label="Receitas")
        ax.fill_between(x, rec_vals, alpha=0.1, color=self.colors.get("green", "#00b894"))
        ax.plot(x, desp_vals, color=self.colors.get("red", "#d63031"), linewidth=2, marker="o", markersize=5, label="Despesas")
        ax.fill_between(x, desp_vals, alpha=0.1, color=self.colors.get("red", "#d63031"))

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=9)
        ax.legend(fontsize=9)
        ax.set_title("Evolucao Temporal", color="white", fontsize=11, pad=10)
        ax.tick_params(colors="white", labelsize=8)
        ax.spines["bottom"].set_color(self.colors.get("border", "#2d2d44"))
        ax.spines["left"].set_color(self.colors.get("border", "#2d2d44"))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def atualizar(self, colors=None):
        if colors:
            self.colors = colors
        self._atualizar()
