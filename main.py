import customtkinter as ctk
from database import init_db
from components.sidebar import Sidebar
from views.dashboard import DashboardView
from views.receitas import ReceitasView
from views.despesas import DespesasView
from views.investimentos import InvestimentosView
from views.categorias import CategoriasView
from views.orcamento import OrcamentoView
from views.metas import MetasView
from views.recorrentes import RecorrentesView
from views.relatorios import RelatoriosView


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#0f0f1a",
    "bg_card": "#1a1a2e",
    "bg_hover": "#16213e",
    "primary": "#6c5ce7",
    "primary_hover": "#5a4bd1",
    "accent": "#00cec9",
    "green": "#00b894",
    "red": "#d63031",
    "yellow": "#fdcb6e",
    "text": "#ffffff",
    "text_dim": "#a0a0b0",
    "border": "#2d2d44",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FinancePro - Controle Financeiro")
        self.geometry("1300x750")
        self.minsize(1050, 620)
        self.configure(fg_color=COLORS["bg_dark"])

        init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self.navegar, colors=COLORS)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.current_view = None
        self.navegar("dashboard")

    def navegar(self, view_name):
        if self.current_view:
            self.current_view.destroy()

        views_map = {
            "dashboard": DashboardView,
            "receitas": ReceitasView,
            "despesas": DespesasView,
            "investimentos": InvestimentosView,
            "categorias": CategoriasView,
            "orcamento": OrcamentoView,
            "metas": MetasView,
            "recorrentes": RecorrentesView,
            "relatorios": RelatoriosView,
        }

        view_class = views_map.get(view_name, DashboardView)
        self.current_view = view_class(self.content_frame, colors=COLORS)
        self.current_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)


if __name__ == "__main__":
    app = App()
    app.after(200, lambda: app.lift())
    app.mainloop()
