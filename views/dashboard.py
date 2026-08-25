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
        self._criar_ultimos()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="Dashboard", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=self.colors.get("text", "#fff")).pack(anchor="w")
        ctk.CTkLabel(left, text="Visao geral das suas financas",
                      font=ctk.CTkFont(size=13),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(header, text=obter_mes_atual(), font=ctk.CTkFont(size=13),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(side="right")

    def _criar_cards(self):
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        cards.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        d = self._dados()

        self._card(cards, "Saldo", formatar_moeda(d["saldo"]),
                   self.colors.get("accent", "#00cec9"), 0)
        self._card(cards, "Receitas", formatar_moeda(d["receitas"]),
                   self.colors.get("green", "#00b894"), 1)
        self._card(cards, "Despesas", formatar_moeda(d["despesas"]),
                   self.colors.get("red", "#d63031"), 2)
        self._card(cards, "Investimentos", formatar_moeda(d["investimentos"]),
                   self.colors.get("primary", "#6c5ce7"), 3)
        self._card(cards, "Economia", formatar_moeda(d["economia"]),
                   self.colors.get("yellow", "#fdcb6e"), 4)

    def _card(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=self.colors.get("bg_card", "#1a1a2e"),
                             corner_radius=12, height=100)
        card.grid(row=0, column=col, padx=4, sticky="ew")
        card.grid_propagate(False)

        ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=2).pack(fill="x", padx=14, pady=(14, 0))
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(anchor="w", padx=14, pady=(8, 0))
        ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=cor).pack(anchor="w", padx=14, pady=(2, 0))

    def _criar_graficos(self):
        gf = ctk.CTkFrame(self, fg_color="transparent")
        gf.grid(row=2, column=0, sticky="nsew")
        gf.grid_columnconfigure((0, 1), weight=1)
        gf.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(gf, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        left.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        ctk.CTkLabel(left, text="  Despesas por Categoria",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))

        c1 = ChartWidget(left, fg_color="transparent")
        c1.pack(fill="both", expand=True, padx=8, pady=8)
        dados = self._dados_grafico()
        if dados["despesas"]:
            c1.criar_grafico_pizza(list(dados["despesas"].keys()), list(dados["despesas"].values()), "")

        right = ctk.CTkFrame(gf, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        right.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        ctk.CTkLabel(right, text="  Receitas por Categoria",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))

        c2 = ChartWidget(right, fg_color="transparent")
        c2.pack(fill="both", expand=True, padx=8, pady=8)
        if dados["receitas"]:
            c2.criar_grafico_pizza(list(dados["receitas"].keys()), list(dados["receitas"].values()), "")

    def _criar_ultimos(self):
        container = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        container.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        ctk.CTkLabel(container, text="  Ultimos Lançamentos",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))

        conn = get_connection()
        ultimas = conn.execute(
            """SELECT 'Receita' as tipo, descricao, valor, data FROM receitas
               UNION ALL
               SELECT 'Despesa' as tipo, descricao, -valor as valor, data FROM despesas
               ORDER BY data DESC LIMIT 6"""
        ).fetchall()
        conn.close()

        if not ultimas:
            ctk.CTkLabel(container, text="Nenhum lancamento recente",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=13)).pack(pady=20)
            return

        for u in ultimas:
            row = ctk.CTkFrame(container, fg_color="transparent", height=32)
            row.pack(fill="x", padx=16, pady=2)

            tc = self.colors.get("green", "#00b894") if u["tipo"] == "Receita" else self.colors.get("red", "#d63031")
            sinal = "+" if u["tipo"] == "Receita" else ""

            ctk.CTkLabel(row, text=u["data"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0"), width=80).pack(side="left")
            ctk.CTkLabel(row, text=u["descricao"], font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text", "#fff")).pack(side="left", padx=12)
            ctk.CTkLabel(row, text=f"{sinal}{formatar_moeda(u['valor'])}", font=ctk.CTkFont(size=12, weight="bold"),
                          text_color=tc).pack(side="right")

        ctk.CTkFrame(container, fg_color="transparent").pack(pady=(4, 8))

    def _dados(self):
        conn = get_connection()
        mes = obter_mes_atual()

        receitas = conn.execute("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE strftime('%Y-%m',data)=?",
                                (mes,)).fetchone()[0]
        despesas = conn.execute("SELECT COALESCE(SUM(valor),0) FROM despesas WHERE strftime('%Y-%m',data)=?",
                                (mes,)).fetchone()[0]
        inv = conn.execute("SELECT COALESCE(SUM(valor_atual),0) FROM investimentos").fetchone()[0]
        conn.close()

        return {
            "receitas": receitas, "despesas": despesas,
            "saldo": receitas - despesas, "investimentos": inv,
            "economia": receitas - despesas if receitas > despesas else 0,
        }

    def _dados_grafico(self):
        conn = get_connection()
        mes = obter_mes_atual()

        r = conn.execute(
            """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(r.valor) as total
               FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
               WHERE strftime('%Y-%m',r.data)=? GROUP BY c.nome""", (mes,)).fetchall()

        d = conn.execute(
            """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(d.valor) as total
               FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
               WHERE strftime('%Y-%m',d.data)=? GROUP BY c.nome""", (mes,)).fetchall()

        conn.close()
        return {"receitas": {x["nome"]: x["total"] for x in r}, "despesas": {x["nome"]: x["total"] for x in d}}
