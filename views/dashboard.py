import logging

import customtkinter as ctk
import matplotlib

matplotlib.use("Agg")

from components.base_view import BaseView
from components.charts import ChartWidget
from components.evolucao_chart import EvolucaoTemporalChart
from constants import MESES_PT
from database import get_connection
from utils import formatar_moeda

logger = logging.getLogger("financeiro.dashboard")


class DashboardView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        import datetime
        now = datetime.datetime.now()
        self.mes_atual = now.month
        self.ano_atual = now.year

        self._criar_header()
        self._criar_cards()
        self._criar_graficos()
        self._criar_evolucao_temporal()
        self._criar_ultimos()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkButton(header, text="<", width=36, height=36, corner_radius=8,
                       fg_color=self.colors.get("bg_card", "#1a1a2e"), hover_color=self.colors.get("bg_hover", "#16213e"),
                       font=ctk.CTkFont(size=16, weight="bold"),
                       command=self._mes_anterior).pack(side="left")

        self.lbl_mes = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=22, weight="bold"),
                                     text_color=self.colors.get("text", "#fff"))
        self.lbl_mes.pack(side="left", padx=12)

        ctk.CTkButton(header, text=">", width=36, height=36, corner_radius=8,
                       fg_color=self.colors.get("bg_card", "#1a1a2e"), hover_color=self.colors.get("bg_hover", "#16213e"),
                       font=ctk.CTkFont(size=16, weight="bold"),
                       command=self._proximo_mes).pack(side="left")

        ctk.CTkButton(header, text="Hoje", height=32, corner_radius=8,
                       font=ctk.CTkFont(size=12), fg_color=self.colors.get("primary", "#6c5ce7"),
                       hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                       command=self._voltar_hoje).pack(side="left", padx=12)

        self._atualizar_label_mes()

    def _atualizar_label_mes(self):
        self.lbl_mes.configure(text=f"{MESES_PT[self.mes_atual]} {self.ano_atual}")

    def _mes_anterior(self):
        self.mes_atual -= 1
        if self.mes_atual < 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        self._atualizar_label_mes()
        self._refresh()

    def _proximo_mes(self):
        self.mes_atual += 1
        if self.mes_atual > 12:
            self.mes_atual = 1
            self.ano_atual += 1
        self._atualizar_label_mes()
        self._refresh()

    def _voltar_hoje(self):
        import datetime
        now = datetime.datetime.now()
        self.mes_atual = now.month
        self.ano_atual = now.year
        self._atualizar_label_mes()
        self._refresh()

    def _refresh(self):
        self._atualizar_cards()
        self._atualizar_graficos()
        self.evolucao_chart.atualizar(self.colors)
        self._atualizar_ultimos()

    def _criar_cards(self):
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._atualizar_cards()

    def _atualizar_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        try:
            d = self._dados()
        except Exception:
            d = {"receitas": 0, "despesas": 0, "saldo": 0, "investimentos": 0, "economia": 0}

        self._card(self.cards_frame, "Saldo", formatar_moeda(d["saldo"]),
                   self.colors.get("accent", "#00cec9"), 0)
        self._card(self.cards_frame, "Receitas", formatar_moeda(d["receitas"]),
                   self.colors.get("green", "#00b894"), 1)
        self._card(self.cards_frame, "Despesas", formatar_moeda(d["despesas"]),
                   self.colors.get("red", "#d63031"), 2)
        self._card(self.cards_frame, "Investimentos", formatar_moeda(d["investimentos"]),
                   self.colors.get("primary", "#6c5ce7"), 3)
        self._card(self.cards_frame, "Economia", formatar_moeda(d["economia"]),
                   self.colors.get("yellow", "#fdcb6e"), 4)

    def _card(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=self.colors.get("bg_card", "#1a1a2e"),
                             corner_radius=12, height=95)
        card.grid(row=0, column=col, padx=4, sticky="ew")
        card.grid_propagate(False)
        ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=2).pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(anchor="w", padx=14, pady=(8, 0))
        ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=19, weight="bold"),
                      text_color=cor).pack(anchor="w", padx=14, pady=(2, 0))

    def _criar_graficos(self):
        self.gf = ctk.CTkFrame(self, fg_color="transparent")
        self.gf.grid(row=2, column=0, sticky="nsew")
        self.gf.grid_columnconfigure((0, 1), weight=1)
        self.gf.grid_rowconfigure(0, weight=1)
        self._atualizar_graficos()

    def _atualizar_graficos(self):
        for w in self.gf.winfo_children():
            w.destroy()

        try:
            dados = self._dados_grafico()
        except Exception:
            dados = {"receitas": {}, "despesas": {}}

        left = self._criar_card_frame(self.gf)
        left.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        ctk.CTkLabel(left, text="  Despesas por Categoria",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        c1 = ChartWidget(left, fg_color="transparent")
        c1.pack(fill="both", expand=True, padx=8, pady=8)
        if dados["despesas"]:
            c1.criar_grafico_pizza(list(dados["despesas"].keys()), list(dados["despesas"].values()), "")

        right = self._criar_card_frame(self.gf)
        right.grid(row=0, column=1, padx=(6, 0), sticky="nsew")
        ctk.CTkLabel(right, text="  Receitas por Categoria",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        c2 = ChartWidget(right, fg_color="transparent")
        c2.pack(fill="both", expand=True, padx=8, pady=8)
        if dados["receitas"]:
            c2.criar_grafico_pizza(list(dados["receitas"].keys()), list(dados["receitas"].values()), "")

    def _criar_evolucao_temporal(self):
        self.evolucao_container = self._criar_card_frame(self)
        self.evolucao_container.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        self.evolucao_container.grid_columnconfigure(0, weight=1)
        self.evolucao_container.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.evolucao_container, text="  Evolucao Temporal - Receitas vs Despesas",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        self.evolucao_chart = EvolucaoTemporalChart(self.evolucao_container, colors=self.colors, meses=6)
        self.evolucao_chart.pack(fill="both", expand=True, padx=8, pady=(4, 12))

    def _criar_ultimos(self):
        self.ultimos_container = self._criar_card_frame(self)
        self.ultimos_container.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        self._atualizar_ultimos()

    def _atualizar_ultimos(self):
        for w in self.ultimos_container.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.ultimos_container, text="  Ultimos Lancamentos",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))

        mes_str = f"{self.ano_atual}-{self.mes_atual:02d}"

        try:
            with get_connection() as conn:
                ultimas = conn.execute(
                    """SELECT 'Receita' as tipo, descricao, valor, data FROM receitas
                       WHERE strftime('%Y-%m',data)=?
                       UNION ALL
                       SELECT 'Despesa' as tipo, descricao, -valor as valor, data FROM despesas
                       WHERE strftime('%Y-%m',data)=?
                       ORDER BY data DESC LIMIT 6""", (mes_str, mes_str)).fetchall()
        except Exception:
            ultimas = []

        if not ultimas:
            ctk.CTkLabel(self.ultimos_container, text="Nenhum lancamento neste mes",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=13)).pack(pady=20)
            return

        for u in ultimas:
            row = ctk.CTkFrame(self.ultimos_container, fg_color="transparent", height=30)
            row.pack(fill="x", padx=16, pady=2)

            tc = self.colors.get("green", "#00b894") if u["tipo"] == "Receita" else self.colors.get("red", "#d63031")
            sinal = "+" if u["tipo"] == "Receita" else ""

            ctk.CTkLabel(row, text=u["data"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0"), width=80).pack(side="left")
            ctk.CTkLabel(row, text=u["descricao"], font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text", "#fff")).pack(side="left", padx=12)
            ctk.CTkLabel(row, text=f"{sinal}{formatar_moeda(u['valor'])}", font=ctk.CTkFont(size=12, weight="bold"),
                          text_color=tc).pack(side="right")

        ctk.CTkFrame(self.ultimos_container, fg_color="transparent").pack(pady=(4, 8))

    def _dados(self):
        mes_str = f"{self.ano_atual}-{self.mes_atual:02d}"
        try:
            with get_connection() as conn:
                receitas = conn.execute("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE strftime('%Y-%m',data)=?",
                                        (mes_str,)).fetchone()[0]
                despesas = conn.execute("SELECT COALESCE(SUM(valor),0) FROM despesas WHERE strftime('%Y-%m',data)=?",
                                        (mes_str,)).fetchone()[0]
                inv = conn.execute("SELECT COALESCE(SUM(valor_atual),0) FROM investimentos").fetchone()[0]
        except Exception:
            logger.error("Erro ao carregar dados do dashboard")
            receitas = 0
            despesas = 0
            inv = 0

        return {
            "receitas": receitas, "despesas": despesas,
            "saldo": receitas - despesas, "investimentos": inv,
            "economia": receitas - despesas if receitas > despesas else 0,
        }

    def _dados_grafico(self):
        mes_str = f"{self.ano_atual}-{self.mes_atual:02d}"
        try:
            with get_connection() as conn:
                r = conn.execute(
                    """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(r.valor) as total
                       FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                       WHERE strftime('%Y-%m',r.data)=? GROUP BY c.nome""", (mes_str,)).fetchall()
                d = conn.execute(
                    """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(d.valor) as total
                       FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
                       WHERE strftime('%Y-%m',d.data)=? GROUP BY c.nome""", (mes_str,)).fetchall()
        except Exception:
            r = []
            d = []

        return {"receitas": {x["nome"]: x["total"] for x in r}, "despesas": {x["nome"]: x["total"] for x in d}}
