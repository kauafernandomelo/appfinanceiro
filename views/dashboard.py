import datetime
import logging
import sqlite3

import customtkinter as ctk
import matplotlib

matplotlib.use("Agg")

from components.base_view import BaseView
from components.charts import ChartWidget
from components.empty_state import EmptyState
from components.evolucao_chart import EvolucaoTemporalChart
from constants import (
    CARD_CORNER_RADIUS,
    DASHBOARD_CARD_HEIGHT,
    FONT_BODY,
    FONT_SECTION,
    FONT_SMALL,
    FONT_TITLE,
    ICONS,
    MESES_PT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
)
from database import get_connection
from utils import formatar_moeda

logger = logging.getLogger("financeiro.dashboard")


class DashboardView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

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
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="left")

        ctk.CTkButton(
            nav_frame, text=ICONS["prev"],
            width=38, height=38, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors.get("bg_card", "#161630"),
            border_width=1,
            border_color=self.colors.get("border", "#2a2a48"),
            hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text", "#f0f0f8"),
            command=self._mes_anterior,
        ).pack(side="left")

        self.lbl_mes = ctk.CTkLabel(
            nav_frame, text="",
            font=ctk.CTkFont(size=FONT_TITLE, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        )
        self.lbl_mes.pack(side="left", padx=SPACING_MD)

        ctk.CTkButton(
            nav_frame, text=ICONS["next"],
            width=38, height=38, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors.get("bg_card", "#161630"),
            border_width=1,
            border_color=self.colors.get("border", "#2a2a48"),
            hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text", "#f0f0f8"),
            command=self._proximo_mes,
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Hoje",
            height=38, corner_radius=8, padx=16,
            font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_muted", "#3d3580"),
            text_color=self.colors.get("primary", "#6c5ce7"),
            command=self._voltar_hoje,
        ).pack(side="left", padx=(SPACING_MD, 0))

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
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_LG))
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._atualizar_cards()

    def _atualizar_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        try:
            d = self._dados()
        except Exception:
            logger.error("Erro ao carregar dados dos cards")
            d = {"receitas": 0, "despesas": 0, "saldo": 0, "investimentos": 0, "economia": 0}

        card_data = [
            ("Saldo", formatar_moeda(d["saldo"]), self.colors.get("primary", "#6c5ce7"), ICONS["dashboard"]),
            ("Receitas", formatar_moeda(d["receitas"]), self.colors.get("positive", "#00b894"), ICONS["receitas"]),
            ("Despesas", formatar_moeda(d["despesas"]), self.colors.get("negative", "#d63031"), ICONS["despesas"]),
            ("Investimentos", formatar_moeda(d["investimentos"]), self.colors.get("primary", "#6c5ce7"), ICONS["investimentos"]),
            ("Economia", formatar_moeda(d["economia"]), self.colors.get("warning", "#fdcb6e"), ICONS["check"]),
        ]

        for col, (titulo, valor, cor, icone) in enumerate(card_data):
            self._card(self.cards_frame, titulo, valor, cor, icone, col)

    def _card(self, parent, titulo, valor, cor, icone, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors.get("bg_card", "#161630"),
            corner_radius=CARD_CORNER_RADIUS,
            border_width=1,
            border_color=self.colors.get("border", "#2a2a48"),
            height=DASHBOARD_CARD_HEIGHT,
        )
        card.grid(row=0, column=col, padx=SPACING_SM, sticky="ew")
        card.grid_propagate(False)

        line = ctk.CTkFrame(card, height=4, fg_color=cor, corner_radius=2)
        line.pack(fill="x", padx=12, pady=(12, SPACING_SM))

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=12)
        ctk.CTkLabel(
            header_row, text=icone,
            font=ctk.CTkFont(size=14),
            text_color=cor,
        ).pack(side="left")
        ctk.CTkLabel(
            header_row, text=titulo,
            font=ctk.CTkFont(size=FONT_SMALL),
            text_color=self.colors.get("text_dim", "#606078"),
        ).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            card, text=valor,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        ).pack(padx=12, anchor="w", pady=(4, 0))

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
            logger.error("Erro ao carregar dados dos graficos")
            dados = {"receitas": {}, "despesas": {}}

        left = self._criar_card_frame(self.gf)
        left.grid(row=0, column=0, padx=(0, SPACING_SM), sticky="nsew")

        left_header = ctk.CTkFrame(left, fg_color="transparent")
        left_header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(
            left_header, text=ICONS["despesas"],
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("negative", "#d63031"),
        ).pack(side="left")
        ctk.CTkLabel(
            left_header, text="Despesas por Categoria",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
            anchor="w",
        ).pack(side="left", padx=(6, 0))

        c1 = ChartWidget(left, fg_color="transparent")
        c1.pack(fill="both", expand=True, padx=8, pady=8)
        if dados["despesas"]:
            c1.criar_grafico_pizza(
                list(dados["despesas"].keys()),
                list(dados["despesas"].values()), "",
            )

        right = self._criar_card_frame(self.gf)
        right.grid(row=0, column=1, padx=(SPACING_SM, 0), sticky="nsew")

        right_header = ctk.CTkFrame(right, fg_color="transparent")
        right_header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(
            right_header, text=ICONS["receitas"],
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("positive", "#00b894"),
        ).pack(side="left")
        ctk.CTkLabel(
            right_header, text="Receitas por Categoria",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
            anchor="w",
        ).pack(side="left", padx=(6, 0))

        c2 = ChartWidget(right, fg_color="transparent")
        c2.pack(fill="both", expand=True, padx=8, pady=8)
        if dados["receitas"]:
            c2.criar_grafico_pizza(
                list(dados["receitas"].keys()),
                list(dados["receitas"].values()), "",
            )

    def _criar_evolucao_temporal(self):
        self.evolucao_container = self._criar_card_frame(self)
        self.evolucao_container.grid(row=3, column=0, sticky="nsew", pady=(SPACING_MD, 0))
        self.evolucao_container.grid_columnconfigure(0, weight=1)
        self.evolucao_container.grid_rowconfigure(1, weight=1)

        evo_header = ctk.CTkFrame(self.evolucao_container, fg_color="transparent")
        evo_header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(
            evo_header, text=ICONS["chart"],
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("primary", "#6c5ce7"),
        ).pack(side="left")
        ctk.CTkLabel(
            evo_header, text="Evolucao Temporal - Receitas vs Despesas",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
            anchor="w",
        ).pack(side="left", padx=(6, 0))

        self.evolucao_chart = EvolucaoTemporalChart(
            self.evolucao_container, colors=self.colors, meses=6,
        )
        self.evolucao_chart.pack(fill="both", expand=True, padx=8, pady=(SPACING_SM, 12))

    def _criar_ultimos(self):
        self.ultimos_container = self._criar_card_frame(self)
        self.ultimos_container.grid(row=4, column=0, sticky="ew", pady=(SPACING_MD, 0))
        self._atualizar_ultimos()

    def _atualizar_ultimos(self):
        for w in self.ultimos_container.winfo_children():
            w.destroy()

        ultimos_header = ctk.CTkFrame(self.ultimos_container, fg_color="transparent")
        ultimos_header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(
            ultimos_header, text=ICONS["calendar"],
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("warning", "#fdcb6e"),
        ).pack(side="left")
        ctk.CTkLabel(
            ultimos_header, text="Ultimos Lancamentos",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
            anchor="w",
        ).pack(side="left", padx=(6, 0))

        mes_str = f"{self.ano_atual}-{self.mes_atual:02d}"

        try:
            with get_connection() as conn:
                ultimas = conn.execute(
                    """SELECT 'Receita' as tipo, descricao, valor, data FROM receitas
                       WHERE strftime('%Y-%m',data)=?
                       UNION ALL
                       SELECT 'Despesa' as tipo, descricao, -valor as valor, data FROM despesas
                       WHERE strftime('%Y-%m',data)=?
                       ORDER BY data DESC LIMIT 6""",
                    (mes_str, mes_str),
                ).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar ultimos lancamentos: %s", e)
            ultimas = []

        if not ultimas:
            EmptyState(
                self.ultimos_container,
                icone=ICONS["calendar"],
                titulo="Nenhum lancamento neste mes",
                subtitulo="Adicione receitas ou despesas para comecar",
                colors=self.colors,
            ).pack(pady=20)
            return

        for i, u in enumerate(ultimas):
            row_bg = (
                self.colors.get("bg_card", "#161630")
                if i % 2 == 0
                else self.colors.get("bg_elevated", "#1e1e3a")
            )
            row = ctk.CTkFrame(
                self.ultimos_container,
                fg_color=row_bg,
                corner_radius=8, height=42,
            )
            row.pack(fill="x", padx=12, pady=2)
            row.pack_propagate(False)

            tc = (
                self.colors.get("positive", "#00b894")
                if u["tipo"] == "Receita"
                else self.colors.get("negative", "#d63031")
            )
            sinal = "+" if u["tipo"] == "Receita" else ""

            tipo_badge = self._criar_status_badge(
                row, u["tipo"][0], tc,
            )
            tipo_badge.pack(side="left", padx=(12, SPACING_SM), pady=8)

            ctk.CTkLabel(
                row, text=u["data"],
                font=ctk.CTkFont(size=FONT_SMALL),
                text_color=self.colors.get("text_dim", "#606078"),
                width=80,
            ).pack(side="left", pady=8)

            ctk.CTkLabel(
                row, text=u["descricao"],
                font=ctk.CTkFont(size=FONT_BODY),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).pack(side="left", padx=SPACING_MD, pady=8, expand=True, anchor="w")

            ctk.CTkLabel(
                row, text=f"{sinal}{formatar_moeda(u['valor'])}",
                font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
                text_color=tc,
            ).pack(side="right", padx=12, pady=8)

            def on_enter(e, frame=row):
                frame.configure(fg_color=self.colors.get("bg_hover", "#252550"))

            def on_leave(e, frame=row, bg=row_bg):
                frame.configure(fg_color=bg)

            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

        ctk.CTkFrame(self.ultimos_container, fg_color="transparent").pack(pady=(SPACING_XS, 8))

    def _dados(self):
        mes_str = f"{self.ano_atual}-{self.mes_atual:02d}"
        try:
            with get_connection() as conn:
                receitas = conn.execute(
                    "SELECT COALESCE(SUM(valor),0) FROM receitas WHERE strftime('%Y-%m',data)=?",
                    (mes_str,),
                ).fetchone()[0]
                despesas = conn.execute(
                    "SELECT COALESCE(SUM(valor),0) FROM despesas WHERE strftime('%Y-%m',data)=?",
                    (mes_str,),
                ).fetchone()[0]
                inv = conn.execute(
                    "SELECT COALESCE(SUM(valor_atual),0) FROM investimentos",
                ).fetchone()[0]
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar dados do dashboard: %s", e)
            receitas = 0
            despesas = 0
            inv = 0

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": receitas - despesas,
            "investimentos": inv,
            "economia": receitas - despesas if receitas > despesas else 0,
        }

    def _dados_grafico(self):
        mes_str = f"{self.ano_atual}-{self.mes_atual:02d}"
        try:
            with get_connection() as conn:
                r = conn.execute(
                    """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(r.valor) as total
                       FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                       WHERE strftime('%Y-%m',r.data)=? GROUP BY c.nome""",
                    (mes_str,),
                ).fetchall()
                d = conn.execute(
                    """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(d.valor) as total
                       FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
                       WHERE strftime('%Y-%m',d.data)=? GROUP BY c.nome""",
                    (mes_str,),
                ).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar dados dos graficos: %s", e)
            r = []
            d = []

        return {
            "receitas": {x["nome"]: x["total"] for x in r},
            "despesas": {x["nome"]: x["total"] for x in d},
        }
