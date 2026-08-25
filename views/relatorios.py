import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual, obter_data_atual
from components.charts import ChartWidget
from components.toast import mostrar_toast
from components.base_view import BaseView


class RelatoriosView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._criar_header()
        self._criar_filtros()
        self._criar_conteudo()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Relatorios").pack(side="left")

    def _criar_filtros(self):
        filtros = self._criar_card_frame(self)
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        inner = ctk.CTkFrame(filtros, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(inner, text="Mes:", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(side="left")
        self.entry_mes = self._criar_entry(inner, "AAAA-MM")
        self.entry_mes.configure(width=130)
        self.entry_mes.insert(0, obter_mes_atual())
        self.entry_mes.pack(side="left", padx=(8, 16))

        ctk.CTkButton(inner, text="Gerar Relatorio", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("primary", "#6c5ce7"),
                       hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                       command=self._gerar).pack(side="left", padx=(0, 8))

        ctk.CTkButton(inner, text="Exportar PDF", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("accent", "#00cec9"), hover_color="#00a3a3",
                       command=self._exportar_pdf).pack(side="left")

        self.label_saldo = ctk.CTkLabel(inner, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_saldo.pack(side="right")

        self._dados_cache = None

    def _criar_conteudo(self):
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=2, column=0, sticky="nsew")
        self.conteudo.grid_columnconfigure((0, 1), weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

        self.cf1 = self._criar_card_frame(self.conteudo)
        self.cf1.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        self.cf2 = self._criar_card_frame(self.conteudo)
        self.cf2.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        container, self.lista_frame = self._criar_lista_frame(self.conteudo)
        container.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(12, 0))

    def _gerar(self):
        mes = self.entry_mes.get().strip()
        if not mes:
            return

        with get_connection() as conn:
            receitas = conn.execute(
                """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(r.valor) as total
                   FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                   WHERE strftime('%Y-%m',r.data)=? GROUP BY c.nome""", (mes,)).fetchall()

            despesas = conn.execute(
                """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(d.valor) as total
                   FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
                   WHERE strftime('%Y-%m',d.data)=? GROUP BY c.nome""", (mes,)).fetchall()

            inv = conn.execute("SELECT SUM(valor_investido) as ti, SUM(valor_atual) as ta FROM investimentos").fetchone()

        total_r = sum(r["total"] for r in receitas)
        total_d = sum(d["total"] for d in despesas)
        saldo = total_r - total_d

        self._dados_cache = {
            "mes": mes, "receitas": receitas, "despesas": despesas,
            "total_r": total_r, "total_d": total_d, "saldo": saldo, "inv": inv,
        }

        cs = self.colors.get("green", "#00b894") if saldo >= 0 else self.colors.get("red", "#d63031")
        self.label_saldo.configure(text=f"Saldo: {formatar_moeda(saldo)}", text_color=cs)

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

        if inv and inv["ti"]:
            lucro = (inv["ta"] or 0) - (inv["ti"] or 0)
            cl = self.colors.get("green", "#00b894") if lucro >= 0 else self.colors.get("red", "#d63031")
            ctk.CTkLabel(self.lista_frame, text="Investimentos", font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=self.colors.get("accent", "#00cec9")).grid(row=row, column=0, sticky="w", padx=16, pady=(8, 4))
            row += 1
            ctk.CTkLabel(self.lista_frame, text=f"  Investido: {formatar_moeda(inv['ti'] or 0)}",
                          font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=row, column=0, sticky="w", padx=16)
            row += 1
            ctk.CTkLabel(self.lista_frame, text=f"  Valor Atual: {formatar_moeda(inv['ta'] or 0)}",
                          font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=row, column=0, sticky="w", padx=16)
            row += 1
            sinal = "+" if lucro >= 0 else ""
            ctk.CTkLabel(self.lista_frame, text=f"  Lucro/Prejuizo: {sinal}{formatar_moeda(lucro)}",
                          font=ctk.CTkFont(size=12, weight="bold"), text_color=cl).grid(
                row=row, column=0, sticky="w", padx=16, pady=(4, 8))
            row += 1

        saldo_cor = self.colors.get("green", "#00b894") if total_r >= total_d else self.colors.get("red", "#d63031")
        ctk.CTkLabel(self.lista_frame, text=f"  Saldo do Mes: {formatar_moeda(total_r - total_d)}",
                      font=ctk.CTkFont(size=13, weight="bold"), text_color=saldo_cor).grid(
            row=row, column=0, sticky="w", padx=16, pady=(12, 8))

    def _exportar_pdf(self):
        if not self._dados_cache:
            mostrar_toast(self, "Gere um relatorio primeiro!", "erro")
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
            from reportlab.lib.colors import HexColor
            import os

            d = self._dados_cache
            filename = f"relatorio_{d['mes']}.pdf"
            filepath = os.path.join(os.path.dirname(__file__), "..", filename)

            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4

            c.setFillColor(HexColor("#1a1a2e"))
            c.rect(0, 0, width, height, fill=1)

            c.setFillColor(HexColor("#ffffff"))
            c.setFont("Helvetica-Bold", 20)
            c.drawString(2*cm, height - 2*cm, f"FinancePro - Relatorio {d['mes']}")

            c.setFont("Helvetica", 12)
            y = height - 3.5*cm

            c.setFillColor(HexColor("#00b894"))
            c.drawString(2*cm, y, f"Receitas: {formatar_moeda(d['total_r'])}")
            y -= 0.8*cm

            c.setFillColor(HexColor("#d63031"))
            c.drawString(2*cm, y, f"Despesas: {formatar_moeda(d['total_d'])}")
            y -= 0.8*cm

            saldo_cor = "#00b894" if d["saldo"] >= 0 else "#d63031"
            c.setFillColor(HexColor(saldo_cor))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y, f"Saldo: {formatar_moeda(d['saldo'])}")
            y -= 1.5*cm

            c.setFillColor(HexColor("#ffffff"))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y, "Detalhes por Categoria:")
            y -= 0.8*cm

            c.setFont("Helvetica", 11)
            c.setFillColor(HexColor("#00b894"))
            c.drawString(2*cm, y, "Receitas:")
            y -= 0.6*cm
            for r in d["receitas"]:
                c.setFillColor(HexColor("#a0a0a0"))
                c.drawString(2.5*cm, y, f"{r['nome']}: {formatar_moeda(r['total'])}")
                y -= 0.5*cm

            y -= 0.3*cm
            c.setFillColor(HexColor("#d63031"))
            c.drawString(2*cm, y, "Despesas:")
            y -= 0.6*cm
            for d_item in d["despesas"]:
                c.setFillColor(HexColor("#a0a0a0"))
                c.drawString(2.5*cm, y, f"{d_item['nome']}: {formatar_moeda(d_item['total'])}")
                y -= 0.5*cm

            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor("#636e72"))
            c.drawString(2*cm, 1.5*cm, f"Gerado em {obter_data_atual()} por FinancePro")

            c.save()
            mostrar_toast(self, f"PDF exportado: {filename}!")
        except ImportError:
            mostrar_toast(self, "Instale reportlab: pip install reportlab", "erro")
        except Exception as e:
            mostrar_toast(self, f"Erro ao exportar: {str(e)[:50]}", "erro")
