import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual
from components.charts import ChartWidget


class RelatoriosView(ctk.CTkFrame):
    def __init__(self, master, colors=None):
        super().__init__(master, fg_color="transparent")
        self.colors = colors or {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._criar_header()
        self._criar_filtros()
        self._criar_conteudo()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(header, text="Relatorios", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=self.colors.get("text", "#fff")).pack(side="left")

    def _criar_filtros(self):
        filtros = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        inner = ctk.CTkFrame(filtros, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(inner, text="Mes:", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(side="left")
        self.entry_mes = ctk.CTkEntry(inner, placeholder_text="AAAA-MM", height=36, width=130, corner_radius=8,
                                       fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                       border_color=self.colors.get("border", "#2d2d44"))
        self.entry_mes.insert(0, obter_mes_atual())
        self.entry_mes.pack(side="left", padx=(8, 16))

        ctk.CTkButton(inner, text="Gerar Relatorio", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("primary", "#6c5ce7"),
                       hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                       command=self._gerar).pack(side="left")

        self.label_saldo = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_saldo.pack(side="right")

    def _criar_conteudo(self):
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=2, column=0, sticky="nsew")
        self.conteudo.grid_columnconfigure((0, 1), weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

        self.cf1 = ctk.CTkFrame(self.conteudo, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        self.cf1.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        self.cf2 = ctk.CTkFrame(self.conteudo, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        self.cf2.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        self.lista_frame = ctk.CTkScrollableFrame(self.conteudo,
                                                   fg_color=self.colors.get("bg_card", "#1a1a2e"),
                                                   corner_radius=12,
                                                   scrollbar_button_color=self.colors.get("border", "#2d2d44"))
        self.lista_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        self.lista_frame.grid_columnconfigure(0, weight=1)

    def _gerar(self):
        mes = self.entry_mes.get().strip()
        if not mes:
            return
        conn = get_connection()

        receitas = conn.execute(
            """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(r.valor) as total
               FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
               WHERE strftime('%Y-%m',r.data)=? GROUP BY c.nome""", (mes,)).fetchall()

        despesas = conn.execute(
            """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(d.valor) as total
               FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
               WHERE strftime('%Y-%m',d.data)=? GROUP BY c.nome""", (mes,)).fetchall()

        inv = conn.execute("SELECT SUM(valor_investido) as total_inv, SUM(valor_atual) as total_atu FROM investimentos").fetchone()

        total_r = sum(r["total"] for r in receitas)
        total_d = sum(d["total"] for d in despesas)
        saldo = total_r - total_d

        cor_saldo = self.colors.get("green", "#00b894") if saldo >= 0 else self.colors.get("red", "#d63031")
        self.label_saldo.configure(text=f"Saldo: {formatar_moeda(saldo)}", text_color=cor_saldo)

        conn.close()

        self._chart(self.cf1, [r["nome"] for r in receitas], [r["total"] for r in receitas], f"Receitas - {mes}")
        self._chart(self.cf2, [d["nome"] for d in despesas], [d["total"] for d in despesas], f"Despesas - {mes}")

        self._detalhes(receitas, despesas, total_r, total_d, inv)

    def _chart(self, frame, labels, valores, titulo):
        for w in frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(frame, text=f"  {titulo}", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("text", "#fff"), anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        if not labels:
            ctk.CTkLabel(frame, text="Sem dados para este periodo",
                          text_color=self.colors.get("text_dim", "#a0a0a0")).pack(pady=40)
            return
        chart = ChartWidget(frame, fg_color="transparent")
        chart.pack(fill="both", expand=True, padx=8, pady=8)
        chart.criar_grafico_pizza(labels, valores, "")

    def _detalhes(self, receitas, despesas, total_r, total_d, inv):
        for w in self.lista_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.lista_frame, text="Resumo Completo",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color=self.colors.get("text", "#fff")).grid(row=0, column=0, pady=12, padx=16, sticky="w")

        row = 1
        ctk.CTkLabel(self.lista_frame, text="Receitas", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("green", "#00b894")).grid(row=row, column=0, sticky="w", padx=16, pady=(8, 4))
        row += 1

        for r in receitas:
            ctk.CTkLabel(self.lista_frame, text=f"  {r['nome']}: {formatar_moeda(r['total'])}",
                          font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=row, column=0, sticky="w", padx=16)
            row += 1

        ctk.CTkLabel(self.lista_frame, text=f"  Total Receitas: {formatar_moeda(total_r)}",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      text_color=self.colors.get("green", "#00b894")).grid(row=row, column=0, sticky="w", padx=16, pady=(4, 8))
        row += 1

        ctk.CTkLabel(self.lista_frame, text="Despesas", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("red", "#d63031")).grid(row=row, column=0, sticky="w", padx=16, pady=(8, 4))
        row += 1

        for d in despesas:
            ctk.CTkLabel(self.lista_frame, text=f"  {d['nome']}: {formatar_moeda(d['total'])}",
                          font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=row, column=0, sticky="w", padx=16)
            row += 1

        ctk.CTkLabel(self.lista_frame, text=f"  Total Despesas: {formatar_moeda(total_d)}",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      text_color=self.colors.get("red", "#d63031")).grid(row=row, column=0, sticky="w", padx=16, pady=(4, 8))
        row += 1

        if inv and inv["total_inv"]:
            ctk.CTkLabel(self.lista_frame, text="Investimentos", font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=self.colors.get("accent", "#00cec9")).grid(row=row, column=0, sticky="w", padx=16, pady=(8, 4))
            row += 1

            lucro = (inv["total_atu"] or 0) - (inv["total_inv"] or 0)
            cor_l = self.colors.get("green", "#00b894") if lucro >= 0 else self.colors.get("red", "#d63031")

            ctk.CTkLabel(self.lista_frame, text=f"  Investido: {formatar_moeda(inv['total_inv'] or 0)}",
                          font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=row, column=0, sticky="w", padx=16)
            row += 1
            ctk.CTkLabel(self.lista_frame, text=f"  Valor Atual: {formatar_moeda(inv['total_atu'] or 0)}",
                          font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=row, column=0, sticky="w", padx=16)
            row += 1
            sinal = "+" if lucro >= 0 else ""
            ctk.CTkLabel(self.lista_frame, text=f"  Lucro/Prejuizo: {sinal}{formatar_moeda(lucro)}",
                          font=ctk.CTkFont(size=12, weight="bold"),
                          text_color=cor_l).grid(row=row, column=0, sticky="w", padx=16, pady=(4, 8))
            row += 1

        ctk.CTkLabel(self.lista_frame, text=f"  Saldo do Mes: {formatar_moeda(total_r - total_d)}",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=self.colors.get("green", "#00b894") if total_r >= total_d else self.colors.get("red", "#d63031")
                      ).grid(row=row, column=0, sticky="w", padx=16, pady=(12, 8))
