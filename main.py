import calendar
from datetime import datetime

import customtkinter as ctk

from components.sidebar import Sidebar
from constants import COLORS_DEFAULTS, LIGHT_COLORS_DEFAULTS, __version__
from database import get_connection, init_db
from views.categorias import CategoriasView
from views.configuracoes import ConfiguracoesView
from views.dashboard import DashboardView
from views.despesas import DespesasView
from views.investimentos import InvestimentosView
from views.metas import MetasView
from views.orcamento import OrcamentoView
from views.receitas import ReceitasView
from views.recorrentes import RecorrentesView
from views.relatorios import RelatoriosView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"FinancePro v{__version__} - Controle Financeiro")
        self.geometry("1320x760")
        self.minsize(1050, 620)

        self.theme = "dark"
        self.current_colors = dict(COLORS_DEFAULTS)
        self.sidebar_collapsed = False

        self.configure(fg_color=self.current_colors["bg_dark"])

        init_db()
        self._verificar_recorrentes()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(
            self,
            on_navigate=self.navegar,
            colors=self.current_colors,
            on_toggle_collapse=self._toggle_sidebar_collapse,
            on_toggle_theme=self.toggle_theme,
            collapsed=self.sidebar_collapsed,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ctk.CTkFrame(
            self, fg_color=self.current_colors["bg_dark"], corner_radius=0
        )
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
        self.bind("<Control-b>", lambda e: self.navegar("categorias"))
        self.bind("<Control-o>", lambda e: self.navegar("orcamento"))
        self.bind("<Control-m>", lambda e: self.navegar("metas"))
        self.bind("<Control-Shift-C>", lambda e: self.navegar("recorrentes"))
        self.bind("<Control-t>", lambda e: self.navegar("configuracoes"))
        self.bind("<Escape>", lambda e: self.navegar("dashboard"))

    def _verificar_recorrentes(self):
        hoje = datetime.now()
        mes = hoje.strftime("%Y-%m")

        with get_connection() as conn:
            ativos = conn.execute(
                "SELECT * FROM recorrentes WHERE ativo=1"
            ).fetchall()

            if not ativos:
                return

            ja_gerados = 0
            for rec in ativos:
                if rec["tipo"] == "receita":
                    existe = conn.execute(
                        "SELECT COUNT(*) FROM receitas WHERE descricao=? AND strftime('%Y-%m',data)=?",
                        (rec["descricao"], mes),
                    ).fetchone()[0]
                else:
                    existe = conn.execute(
                        "SELECT COUNT(*) FROM despesas WHERE descricao=? AND strftime('%Y-%m',data)=?",
                        (rec["descricao"], mes),
                    ).fetchone()[0]
                if existe > 0:
                    ja_gerados += 1

            pendentes = len(ativos) - ja_gerados
            if pendentes > 0:
                self.after(1000, lambda: self._popup_recorrentes(pendentes))

    def _popup_recorrentes(self, count):
        modal = ctk.CTkToplevel(self)
        modal.title("Lancamentos Recorrentes")
        modal.geometry("380x200")
        modal.configure(fg_color=self.current_colors["bg_dark"])
        modal.grab_set()

        f = ctk.CTkFrame(modal, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(
            f,
            text="Lancamentos Recorrentes Detectados",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.current_colors["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            f,
            text=f"Existem {count} contas recorrentes pendentes.\nDeseja gerar os lancamentos do mes atual?",
            font=ctk.CTkFont(size=13),
            text_color=self.current_colors["text_dim"],
            wraplength=320,
        ).pack(anchor="w", pady=(12, 20))

        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(fill="x")

        def gerar():
            ano_num = datetime.now().year
            mes_num = datetime.now().month
            dias_no_mes = calendar.monthrange(ano_num, mes_num)[1]

            with get_connection() as conn:
                ativos = conn.execute(
                    "SELECT * FROM recorrentes WHERE ativo=1"
                ).fetchall()
                gerados = 0
                for r in ativos:
                    dia = min(r["dia_mes"], dias_no_mes)
                    data = f"{ano_num}-{mes_num:02d}-{dia:02d}"
                    cat = conn.execute(
                        "SELECT id FROM categorias WHERE id=?", (r["categoria_id"],)
                    ).fetchone()
                    cid = cat["id"] if cat else None
                    if r["tipo"] == "receita":
                        conn.execute(
                            "INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                            (r["descricao"], r["valor"], data, cid),
                        )
                    else:
                        conn.execute(
                            "INSERT INTO despesas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                            (r["descricao"], r["valor"], data, cid),
                        )
                    gerados += 1
                conn.commit()
            modal.destroy()
            self.navegar("dashboard")

        ctk.CTkButton(
            btns,
            text="Gerar",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.current_colors["green"],
            hover_color="#00a884",
            command=gerar,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btns,
            text="Agora Nao",
            height=36,
            corner_radius=8,
            fg_color=self.current_colors["border"],
            hover_color="#3d3d54",
            command=modal.destroy,
        ).pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _atalho_novo(self):
        view = self.sidebar.active_view
        if view in ("receitas", "despesas", "investimentos"):
            self.navegar(view)
        else:
            self.navegar("dashboard")

    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            self.current_colors = dict(LIGHT_COLORS_DEFAULTS)
            ctk.set_appearance_mode("light")
        else:
            self.theme = "dark"
            self.current_colors = dict(COLORS_DEFAULTS)
            ctk.set_appearance_mode("dark")

        self.configure(fg_color=self.current_colors["bg_dark"])
        self.content_frame.configure(fg_color=self.current_colors["bg_dark"])
        self.sidebar.update_colors(self.current_colors)
        self.navegar(self.sidebar.active_view)

    def _toggle_sidebar_collapse(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.sidebar.set_collapsed(self.sidebar_collapsed)

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
            "configuracoes": ConfiguracoesView,
        }

        view_class = views_map.get(view_name, DashboardView)
        self.current_view = view_class(self.content_frame, colors=self.current_colors)
        self.current_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)


if __name__ == "__main__":
    app = App()
    app.after(200, lambda: app.lift())
    app.mainloop()
