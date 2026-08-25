import customtkinter as ctk
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

    def criar_grafico_pizza(self, labels, valores, titulo=""):
        self.limpar()

        if not labels or not valores:
            return

        fig = Figure(figsize=(5, 4), dpi=100, facecolor="#1a1a2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1a1a2e")

        cores = ["#6c5ce7", "#00cec9", "#fdcb6e", "#d63031", "#00b894", "#e17055", "#a29bfe", "#fab1a0"]
        wedge_colors = cores[: len(labels)]

        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            autopct="%1.1f%%",
            colors=wedge_colors,
            textprops={"color": "white", "fontsize": 9},
            pctdistance=0.75,
            startangle=90,
        )

        for t in autotexts:
            t.set_fontsize(8)
            t.set_color("white")

        if titulo:
            ax.set_title(titulo, color="white", fontsize=11, pad=10)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def criar_grafico_barras(self, labels, valores, titulo=""):
        self.limpar()

        if not labels or not valores:
            return

        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#1a1a2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1a1a2e")

        cores = ["#00b894" if v >= 0 else "#d63031" for v in valores]
        ax.bar(labels, valores, color=cores, edgecolor="#2d2d44", width=0.6)

        ax.set_title(titulo, color="white", fontsize=11)
        ax.tick_params(colors="white", labelsize=8)
        ax.spines["bottom"].set_color("#2d2d44")
        ax.spines["left"].set_color("#2d2d44")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def criar_grafico_linha(self, labels, valores, titulo=""):
        self.limpar()

        if not labels or not valores:
            return

        fig = Figure(figsize=(6, 4), dpi=100, facecolor="#1a1a2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1a1a2e")

        ax.plot(labels, valores, color="#6c5ce7", linewidth=2, marker="o", markersize=6)
        ax.fill_between(labels, valores, alpha=0.1, color="#6c5ce7")

        ax.set_title(titulo, color="white", fontsize=11)
        ax.tick_params(colors="white", labelsize=8)
        ax.spines["bottom"].set_color("#2d2d44")
        ax.spines["left"].set_color("#2d2d44")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
