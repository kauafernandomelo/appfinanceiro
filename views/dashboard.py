import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual
from components.charts import ChartWidget


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_header()
        self.criar_cards_resumo()
        self.criar_graficos()

    def criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=obter_mes_atual(),
            font=ctk.CTkFont(size=14),
            text_color="#a0a0a0",
        ).pack(side="right")

    def criar_cards_resumo(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        dados = self.obter_resumo()

        self.criar_card(cards_frame, "💰 Saldo", formatar_moeda(dados["saldo"]), "#10b981", 0)
        self.criar_card(cards_frame, "💵 Receitas", formatar_moeda(dados["receitas"]), "#3b82f6", 1)
        self.criar_card(cards_frame, "💸 Despesas", formatar_moeda(dados["despesas"]), "#ef4444", 2)

    def criar_card(self, parent, titulo: str, valor: str, cor: str, col: int):
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=10, height=100)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=14),
            text_color="#a0a0a0",
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            card,
            text=valor,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=cor,
        ).pack()

    def criar_graficos(self):
        graficos_frame = ctk.CTkFrame(self, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew")
        graficos_frame.grid_columnconfigure((0, 1), weight=1)
        graficos_frame.grid_rowconfigure(0, weight=1)

        chart_frame1 = ctk.CTkFrame(graficos_frame, fg_color="#1a1a2e", corner_radius=10)
        chart_frame1.grid(row=0, column=0, padx=5, sticky="nsew")

        chart1 = ChartWidget(chart_frame1, fg_color="transparent")
        chart1.pack(fill="both", expand=True, padx=10, pady=10)

        dados = self.obter_dados_grafico()
        if dados["receitas_por_categoria"]:
            chart1.criar_grafico_pizza(
                list(dados["receitas_por_categoria"].keys()),
                list(dados["receitas_por_categoria"].values()),
                "Receitas por Categoria",
            )

        chart_frame2 = ctk.CTkFrame(graficos_frame, fg_color="#1a1a2e", corner_radius=10)
        chart_frame2.grid(row=0, column=1, padx=5, sticky="nsew")

        chart2 = ChartWidget(chart_frame2, fg_color="transparent")
        chart2.pack(fill="both", expand=True, padx=10, pady=10)

        if dados["despesas_por_categoria"]:
            chart2.criar_grafico_pizza(
                list(dados["despesas_por_categoria"].keys()),
                list(dados["despesas_por_categoria"].values()),
                "Despesas por Categoria",
            )

    def obter_resumo(self) -> dict:
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
        }

    def obter_dados_grafico(self) -> dict:
        conn = get_connection()
        mes = obter_mes_atual()

        receitas = conn.execute(
            """SELECT c.nome, SUM(r.valor) as total
               FROM receitas r
               LEFT JOIN categorias c ON r.categoria_id = c.id
               WHERE strftime('%Y-%m', r.data) = ?
               GROUP BY c.nome""",
            (mes,),
        ).fetchall()

        despesas = conn.execute(
            """SELECT c.nome, SUM(d.valor) as total
               FROM despesas d
               LEFT JOIN categorias c ON d.categoria_id = c.id
               WHERE strftime('%Y-%m', d.data) = ?
               GROUP BY c.nome""",
            (mes,),
        ).fetchall()

        conn.close()

        return {
            "receitas_por_categoria": {r["nome"] or "Sem categoria": r["total"] for r in receitas},
            "despesas_por_categoria": {d["nome"] or "Sem categoria": d["total"] for d in despesas},
        }
