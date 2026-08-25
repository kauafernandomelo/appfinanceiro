import customtkinter as ctk
from database import init_db
from components.sidebar import Sidebar
from views.dashboard import DashboardView
from views.receitas import ReceitasView
from views.despesas import DespesasView
from views.categorias import CategoriasView
from views.orcamento import OrcamentoView
from views.metas import MetasView
from views.recorrentes import RecorrentesView
from views.relatorios import RelatoriosView


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Controle Financeiro")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self.navegar)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.current_view = None
        self.navegar("dashboard")

    def navegar(self, view_name: str):
        if self.current_view:
            self.current_view.destroy()

        views_map = {
            "dashboard": DashboardView,
            "receitas": ReceitasView,
            "despesas": DespesasView,
            "categorias": CategoriasView,
            "orcamento": OrcamentoView,
            "metas": MetasView,
            "recorrentes": RecorrentesView,
            "relatorios": RelatoriosView,
        }

        view_class = views_map.get(view_name, DashboardView)
        self.current_view = view_class(self.content_frame)
        self.current_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
