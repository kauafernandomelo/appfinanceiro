import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ChartWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = None

    def limpar(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

    def criar_grafico_barras(self, labels: list, valores: list, titulo: str = ""):
        self.limpar()

        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2b2b2b")

        cores = ["#10b981" if v >= 0 else "#ef4444" for v in valores]
        ax.bar(labels, valores, color=cores, edgecolor="#404040")

        ax.set_title(titulo, color="white", fontsize=12)
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("#404040")
        ax.spines["left"].set_color("#404040")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def criar_grafico_pizza(self, labels: list, valores: list, titulo: str = ""):
        self.limpar()

        fig = Figure(figsize=(5, 4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2b2b2b")

        cores = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct="%1.1f%%",
            colors=cores[: len(valores)],
            textprops={"color": "white"},
        )

        ax.set_title(titulo, color="white", fontsize=12)
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def criar_grafico_linha(self, labels: list, valores: list, titulo: str = ""):
        self.limpar()

        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2b2b2b")

        ax.plot(labels, valores, color="#3b82f6", linewidth=2, marker="o", markersize=6)
        ax.fill_between(labels, valores, alpha=0.1, color="#3b82f6")

        ax.set_title(titulo, color="white", fontsize=12)
        ax.tick_params(colors="white")
        ax.spines["bottom"].set_color("#404040")
        ax.spines["left"].set_color("#404040")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
