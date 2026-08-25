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
        self.geometry("1320x760")
        self.minsize(1050, 620)
        self.configure(fg_color=COLORS["bg_dark"])

        init_db()
        self._verificar_recorrentes()

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

        self.bind("<Control-n>", lambda e: self._atalho_novo())
        self.bind("<Control-r>", lambda e: self.navegar("receitas"))
        self.bind("<Control-d>", lambda e: self.navegar("despesas"))
        self.bind("<Control-i>", lambda e: self.navegar("investimentos"))
        self.bind("<Control-l>", lambda e: self.navegar("relatorios"))
        self.bind("<Escape>", lambda e: self.navegar("dashboard"))

    def _verificar_recorrentes(self):
        from datetime import datetime
        from utils import obter_mes_atual
        from database import get_connection

        hoje = datetime.now()
        mes = obter_mes_atual()

        with get_connection() as conn:
            ativos = conn.execute(
                "SELECT COUNT(*) FROM recorrentes WHERE ativo=1 AND dia_mes=?", (hoje.day,)
            ).fetchone()[0]

            if ativos > 0:
                ja_existe = conn.execute(
                    """SELECT COUNT(*) FROM (
                        SELECT id FROM despesas WHERE strftime('%Y-%m',data)=?
                        UNION ALL
                        SELECT id FROM receitas WHERE strftime('%Y-%m',data)=?
                    )""", (mes, mes)
                ).fetchone()[0]

                if ja_existe == 0:
                    self.after(1000, lambda: self._popup_recorrentes(ativos))

    def _popup_recorrentes(self, count):
        modal = ctk.CTkToplevel(self)
        modal.title("Lancamentos Recorrentes")
        modal.geometry("380x200")
        modal.configure(fg_color=COLORS["bg_dark"])
        modal.grab_set()

        f = ctk.CTkFrame(modal, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(f, text="Lancamentos Recorrentes Detectados",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=COLORS["text"]).pack(anchor="w")

        ctk.CTkLabel(f, text=f"Existem {count} contas recorrentes ativas.\nDeseja gerar os lancamentos do mes atual?",
                      font=ctk.CTkFont(size=13),
                      text_color=COLORS["text_dim"], wraplength=320).pack(anchor="w", pady=(12, 20))

        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(fill="x")

        def gerar():
            from utils import obter_mes_atual
            from datetime import datetime
            with get_connection() as conn:
                ativos = conn.execute("SELECT * FROM recorrentes WHERE ativo=1").fetchall()
                mes = obter_mes_atual()
                ano, mes_num = mes.split("-")
                dias = 31 if mes_num in ("01","03","05","07","08","10","12") else 30 if mes_num != "02" else 28
                gerados = 0
                for r in ativos:
                    dia = min(r["dia_mes"], dias)
                    data = f"{ano}-{mes_num:02d}-{dia:02d}"
                    cat = conn.execute("SELECT id FROM categorias WHERE id=?", (r["categoria_id"],)).fetchone()
                    cid = cat["id"] if cat else None
                    if r["tipo"] == "receita":
                        conn.execute("INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                                     (r["descricao"], r["valor"], data, cid))
                    else:
                        conn.execute("INSERT INTO despesas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                                     (r["descricao"], r["valor"], data, cid))
                    gerados += 1
                conn.commit()
            modal.destroy()
            self.navegar("dashboard")

        ctk.CTkButton(btns, text="Gerar", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=COLORS["green"], hover_color="#00a884",
                       command=gerar).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btns, text="Agora Nao", height=36, corner_radius=8,
                       fg_color=COLORS["border"], hover_color="#3d3d54",
                       command=modal.destroy).pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _atalho_novo(self):
        nav_map = {
            "receitas": "receitas",
            "despesas": "despesas",
            "investimentos": "investimentos",
        }
        if self.sidebar.active_view in nav_map:
            pass

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
