import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual
from components.charts import ChartWidget


class RelatoriosView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.criar_header()
        self.criar_filtros()
        self.criar_conteudo()

    def criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Relatórios",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

    def criar_filtros(self):
        filtros = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filtros.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(filtros, text="Mês:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_mes = ctk.CTkEntry(filtros, placeholder_text="YYYY-MM")
        self.entry_mes.insert(0, obter_mes_atual())
        self.entry_mes.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            filtros,
            text="Gerar Relatório",
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.gerar_relatorio,
        ).grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        self.label_total = ctk.CTkLabel(
            filtros,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.label_total.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="e")

    def criar_conteudo(self):
        self.conteudo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo_frame.grid(row=2, column=0, sticky="nsew")
        self.conteudo_frame.grid_columnconfigure((0, 1), weight=1)
        self.conteudo_frame.grid_rowconfigure(0, weight=1)

        self.chart_frame1 = ctk.CTkFrame(self.conteudo_frame, fg_color="#1a1a2e", corner_radius=10)
        self.chart_frame1.grid(row=0, column=0, padx=5, sticky="nsew")

        self.chart_frame2 = ctk.CTkFrame(self.conteudo_frame, fg_color="#1a1a2e", corner_radius=10)
        self.chart_frame2.grid(row=0, column=1, padx=5, sticky="nsew")

        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.lista_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.lista_frame.grid_columnconfigure(0, weight=1)

    def gerar_relatorio(self):
        mes = self.entry_mes.get()
        if not mes:
            return

        conn = get_connection()

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

        total_receitas = sum(r["total"] for r in receitas)
        total_despesas = sum(d["total"] for d in despesas)
        saldo = total_receitas - total_despesas

        self.label_total.configure(
            text=f"Saldo: {formatar_moeda(saldo)}",
            text_color="#10b981" if saldo >= 0 else "#ef4444",
        )

        conn.close()

        self.atualizar_grafico(
            self.chart_frame1,
            [r["nome"] or "Sem categoria" for r in receitas],
            [r["total"] for r in receitas],
            f"Receitas - {mes}",
        )

        self.atualizar_grafico(
            self.chart_frame2,
            [d["nome"] or "Sem categoria" for d in despesas],
            [d["total"] for d in despesas],
            f"Despesas - {mes}",
        )

        self.atualizar_lista_detalhada(receitas, despesas, total_receitas, total_despesas)

    def atualizar_grafico(self, frame, labels, valores, titulo):
        for widget in frame.winfo_children():
            widget.destroy()

        if not labels:
            ctk.CTkLabel(frame, text="Sem dados", text_color="#a0a0a0").pack(pady=20)
            return

        chart = ChartWidget(frame, fg_color="transparent")
        chart.pack(fill="both", expand=True, padx=10, pady=10)
        chart.criar_grafico_pizza(labels, valores, titulo)

    def atualizar_lista_detalhada(self, receitas, despesas, total_receitas, total_despesas):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.lista_frame,
            text="Resumo Detalhado",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=10, sticky="w")

        row = 1
        ctk.CTkLabel(
            self.lista_frame,
            text="Receitas:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#10b981",
        ).grid(row=row, column=0, pady=(10, 5), sticky="w")
        row += 1

        for r in receitas:
            ctk.CTkLabel(
                self.lista_frame,
                text=f"  • {r['nome'] or 'Sem categoria'}: {formatar_moeda(r['total'])}",
                font=ctk.CTkFont(size=12),
            ).grid(row=row, column=0, sticky="w")
            row += 1

        ctk.CTkLabel(
            self.lista_frame,
            text=f"  Total Receitas: {formatar_moeda(total_receitas)}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
        ).grid(row=row, column=0, sticky="w")
        row += 1

        ctk.CTkLabel(
            self.lista_frame,
            text="Despesas:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ef4444",
        ).grid(row=row, column=0, pady=(10, 5), sticky="w")
        row += 1

        for d in despesas:
            ctk.CTkLabel(
                self.lista_frame,
                text=f"  • {d['nome'] or 'Sem categoria'}: {formatar_moeda(d['total'])}",
                font=ctk.CTkFont(size=12),
            ).grid(row=row, column=0, sticky="w")
            row += 1

        ctk.CTkLabel(
            self.lista_frame,
            text=f"  Total Despesas: {formatar_moeda(total_despesas)}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ef4444",
        ).grid(row=row, column=0, sticky="w")
