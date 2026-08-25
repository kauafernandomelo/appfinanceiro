import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual
from components.charts import ChartWidget


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, colors=None):
        super().__init__(master, fg_color="transparent")
        self.colors = colors or {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._criar_header()
        self._criar_cards()
        self._criar_graficos()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 24))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Visao geral das suas financas",
            font=ctk.CTkFont(size=13),
            text_color=self.colors.get("text_dim", "#a0a0a0"),
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            header,
            text=obter_mes_atual(),
            font=ctk.CTkFont(size=13),
            text_color=self.colors.get("text_dim", "#a0a0a0"),
        ).pack(side="right")

    def _criar_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 24))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        dados = self._obter_resumo()

        self._card(cards_frame, "Saldo Total", formatar_moeda(dados["saldo"]),
                   self.colors.get("accent", "#00cec9"), 0)
        self._card(cards_frame, "Receitas", formatar_moeda(dados["receitas"]),
                   self.colors.get("green", "#00b894"), 1)
        self._card(cards_frame, "Despesas", formatar_moeda(dados["despesas"]),
                   self.colors.get("red", "#d63031"), 2)
        self._card(cards_frame, "Economia", formatar_moeda(dados["economia"]),
                   self.colors.get("yellow", "#fdcb6e"), 3)

    def _card(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
            height=110,
        )
        card.grid(row=0, column=col, padx=6, sticky="ew")
        card.grid_propagate(False)

        bar = ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=2)
        bar.pack(fill="x", padx=16, pady=(16, 0))

        ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=12),
            text_color=self.colors.get("text_dim", "#a0a0a0"),
        ).pack(anchor="w", padx=16, pady=(12, 0))

        ctk.CTkLabel(
            card,
            text=valor,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=cor,
        ).pack(anchor="w", padx=16, pady=(4, 0))

    def _criar_graficos(self):
        graficos_frame = ctk.CTkFrame(self, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew")
        graficos_frame.grid_columnconfigure((0, 1), weight=1)
        graficos_frame.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(
            graficos_frame,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        left.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        ctk.CTkLabel(
            left,
            text="  Despesas por Categoria",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(16, 0))

        chart1 = ChartWidget(left, fg_color="transparent")
        chart1.pack(fill="both", expand=True, padx=8, pady=8)

        dados = self._obter_dados_grafico()
        if dados["despesas_por_categoria"]:
            chart1.criar_grafico_pizza(
                list(dados["despesas_por_categoria"].keys()),
                list(dados["despesas_por_categoria"].values()),
                "",
            )

        right = ctk.CTkFrame(
            graficos_frame,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        right.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        ctk.CTkLabel(
            right,
            text="  Receitas por Categoria",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(16, 0))

        chart2 = ChartWidget(right, fg_color="transparent")
        chart2.pack(fill="both", expand=True, padx=8, pady=8)

        if dados["receitas_por_categoria"]:
            chart2.criar_grafico_pizza(
                list(dados["receitas_por_categoria"].keys()),
                list(dados["receitas_por_categoria"].values()),
                "",
            )

    def _obter_resumo(self):
        conn = get_connection()
        mes = obter_mes_atual()

        receitas = conn.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM receitas WHERE strftime('%Y-%m', data) = ?",
            (mes,),
        ).fetchone()[0]

        despesas = conn.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM despesas WHERE strftime('%Y-%m', data) = ?",
            (mes,),
        ).fetchone()[0]

        conn.close()

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": receitas - despesas,
            "economia": receitas - despesas if receitas > despesas else 0,
        }

    def _obter_dados_grafico(self):
        conn = get_connection()
        mes = obter_mes_atual()

        receitas = conn.execute(
            """SELECT COALESCE(c.nome, 'Sem categoria') as nome, SUM(r.valor) as total
               FROM receitas r
               LEFT JOIN categorias c ON r.categoria_id = c.id
               WHERE strftime('%Y-%m', r.data) = ?
               GROUP BY c.nome""",
            (mes,),
        ).fetchall()

        despesas = conn.execute(
            """SELECT COALESCE(c.nome, 'Sem categoria') as nome, SUM(d.valor) as total
               FROM despesas d
               LEFT JOIN categorias c ON d.categoria_id = c.id
               WHERE strftime('%Y-%m', d.data) = ?
               GROUP BY c.nome""",
            (mes,),
        ).fetchall()

        conn.close()

        return {
            "receitas_por_categoria": {r["nome"]: r["total"] for r in receitas},
            "despesas_por_categoria": {d["nome"]: d["total"] for d in despesas},
        }
