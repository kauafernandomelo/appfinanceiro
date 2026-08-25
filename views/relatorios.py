import csv
import logging
import os
import sqlite3

import customtkinter as ctk
import matplotlib

matplotlib.use("Agg")
from datetime import datetime

from components.base_view import BaseView
from components.charts import ChartWidget
from components.evolucao_chart import EvolucaoTemporalChart
from components.toast import mostrar_toast
from constants import (
    BUTTON_CORNER_RADIUS,
    FONT_BODY,
    FONT_CARD_TITLE,
    FONT_LABEL,
    FONT_SECTION,
    ICONS,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
)
from database import get_connection
from utils import formatar_moeda, obter_data_atual, obter_mes_atual

logger = logging.getLogger("financeiro.relatorios")


class RelatoriosView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._criar_header()
        self._criar_filtros()
        self._criar_conteudo()
        self._criar_evolucao_temporal()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, f"{ICONS['relatorios']}  Relatorios").pack(side="left")

    def _criar_filtros(self):
        filtros = self._criar_card_frame(self)
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_MD))
        inner = ctk.CTkFrame(filtros, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)

        self._criar_label(
            inner, "Mes:",
            font=ctk.CTkFont(size=FONT_LABEL),
        ).pack(side="left")

        self.entry_mes = self._criar_entry(inner, "AAAA-MM")
        self.entry_mes.configure(width=130)
        self.entry_mes.insert(0, obter_mes_atual())
        self.entry_mes.pack(side="left", padx=(SPACING_SM, SPACING_LG))

        ctk.CTkButton(
            inner, text=f"{ICONS['check']}  Gerar Relatorio", height=36,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._gerar,
        ).pack(side="left", padx=(0, SPACING_SM))

        ctk.CTkButton(
            inner, text=f"{ICONS['info']}  Exportar PDF", height=36,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._exportar_pdf,
        ).pack(side="left", padx=(0, SPACING_SM))

        ctk.CTkButton(
            inner, text=f"{ICONS['info']}  Exportar CSV", height=36,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._exportar_csv,
        ).pack(side="left")

        self.label_saldo = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
        )
        self.label_saldo.pack(side="right")

        self._dados_cache = None

    def _criar_conteudo(self):
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=2, column=0, sticky="nsew")
        self.conteudo.grid_columnconfigure((0, 1), weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

        self.cf1 = self._criar_card_frame(self.conteudo)
        self.cf1.grid(row=0, column=0, padx=(0, SPACING_SM), sticky="nsew")

        self.cf2 = self._criar_card_frame(self.conteudo)
        self.cf2.grid(row=0, column=1, padx=(SPACING_SM, 0), sticky="nsew")

        container, self.lista_frame = self._criar_lista_frame(self.conteudo)
        container.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(SPACING_MD, 0))

    def _criar_evolucao_temporal(self):
        self.evolucao_container = self._criar_card_frame(self)
        self.evolucao_container.grid(row=3, column=0, sticky="nsew", pady=(SPACING_MD, 0))
        self.evolucao_container.grid_columnconfigure(0, weight=1)
        self.evolucao_container.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            self.evolucao_container,
            text=f"  {ICONS['chart']}  Evolucao Temporal - Receitas vs Despesas",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
            anchor="w",
        ).pack(fill="x", padx=SPACING_LG, pady=(SPACING_MD, 0))
        self.evolucao_chart = EvolucaoTemporalChart(
            self.evolucao_container, colors=self.colors, meses=6
        )
        self.evolucao_chart.pack(fill="both", expand=True, padx=SPACING_SM, pady=(SPACING_SM, SPACING_MD))

    def _gerar(self):
        mes = self.entry_mes.get().strip()
        if not mes:
            return

        try:
            with get_connection() as conn:
                receitas = conn.execute(
                    """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(r.valor) as total
                       FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                       WHERE strftime('%Y-%m',r.data)=? GROUP BY c.nome""",
                    (mes,),
                ).fetchall()

                despesas = conn.execute(
                    """SELECT COALESCE(c.nome,'Sem categoria') as nome, SUM(d.valor) as total
                       FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
                       WHERE strftime('%Y-%m',d.data)=? GROUP BY c.nome""",
                    (mes,),
                ).fetchall()

                inv = conn.execute(
                    "SELECT SUM(valor_investido) as ti, SUM(valor_atual) as ta FROM investimentos"
                ).fetchone()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao acessar banco de dados: %s", e)
            mostrar_toast(self, "Erro ao acessar banco de dados!", "erro")
            return

        total_r = sum(r["total"] for r in receitas)
        total_d = sum(d["total"] for d in despesas)
        saldo = total_r - total_d

        self._dados_cache = {
            "mes": mes,
            "receitas": receitas,
            "despesas": despesas,
            "total_r": total_r,
            "total_d": total_d,
            "saldo": saldo,
            "inv": inv,
        }

        cs = (
            self.colors.get("positive", "#00b894")
            if saldo >= 0
            else self.colors.get("negative", "#d63031")
        )
        self.label_saldo.configure(text=f"Saldo: {formatar_moeda(saldo)}", text_color=cs)

        self._chart(
            self.cf1,
            [r["nome"] for r in receitas],
            [r["total"] for r in receitas],
            f"Receitas - {mes}",
        )
        self._chart(
            self.cf2,
            [d["nome"] for d in despesas],
            [d["total"] for d in despesas],
            f"Despesas - {mes}",
        )
        self._detalhes(receitas, despesas, total_r, total_d, inv)

    def _chart(self, frame, labels, valores, titulo):
        for w in frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            frame,
            text=f"  {titulo}",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
            anchor="w",
        ).pack(fill="x", padx=SPACING_LG, pady=(SPACING_MD, 0))
        if not labels:
            ctk.CTkLabel(
                frame,
                text="Sem dados para este periodo",
                font=ctk.CTkFont(size=FONT_LABEL),
                text_color=self.colors.get("text_dim", "#606078"),
            ).pack(pady=40)
            return
        chart = ChartWidget(frame, fg_color="transparent")
        chart.pack(fill="both", expand=True, padx=SPACING_SM, pady=SPACING_SM)
        chart.criar_grafico_pizza(labels, valores, "")

    def _detalhes(self, receitas, despesas, total_r, total_d, inv):
        for w in self.lista_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.lista_frame,
            text="Resumo Completo",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        ).grid(row=0, column=0, pady=SPACING_MD, padx=SPACING_LG, sticky="w")

        row = 1
        ctk.CTkLabel(
            self.lista_frame,
            text=f"{ICONS['receitas']}  Receitas",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=self.colors.get("positive", "#00b894"),
        ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_SM, SPACING_XS))
        row += 1

        for r in receitas:
            ctk.CTkLabel(
                self.lista_frame,
                text=f"  {r['nome']}: {formatar_moeda(r['total'])}",
                font=ctk.CTkFont(size=FONT_LABEL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=row, column=0, sticky="w", padx=SPACING_LG)
            row += 1

        ctk.CTkLabel(
            self.lista_frame,
            text=f"  Total Receitas: {formatar_moeda(total_r)}",
            font=ctk.CTkFont(size=FONT_LABEL, weight="bold"),
            text_color=self.colors.get("positive", "#00b894"),
        ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_SM, SPACING_MD))
        row += 1

        ctk.CTkLabel(
            self.lista_frame,
            text=f"{ICONS['despesas']}  Despesas",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=self.colors.get("negative", "#d63031"),
        ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_SM, SPACING_XS))
        row += 1

        for d in despesas:
            ctk.CTkLabel(
                self.lista_frame,
                text=f"  {d['nome']}: {formatar_moeda(d['total'])}",
                font=ctk.CTkFont(size=FONT_LABEL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=row, column=0, sticky="w", padx=SPACING_LG)
            row += 1

        ctk.CTkLabel(
            self.lista_frame,
            text=f"  Total Despesas: {formatar_moeda(total_d)}",
            font=ctk.CTkFont(size=FONT_LABEL, weight="bold"),
            text_color=self.colors.get("negative", "#d63031"),
        ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_SM, SPACING_MD))
        row += 1

        if inv and inv["ti"]:
            lucro = (inv["ta"] or 0) - (inv["ti"] or 0)
            cl = (
                self.colors.get("positive", "#00b894")
                if lucro >= 0
                else self.colors.get("negative", "#d63031")
            )
            ctk.CTkLabel(
                self.lista_frame,
                text=f"{ICONS['investimentos']}  Investimentos",
                font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
                text_color=self.colors.get("primary", "#6c5ce7"),
            ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_SM, SPACING_XS))
            row += 1

            ctk.CTkLabel(
                self.lista_frame,
                text=f"  Investido: {formatar_moeda(inv['ti'] or 0)}",
                font=ctk.CTkFont(size=FONT_LABEL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=row, column=0, sticky="w", padx=SPACING_LG)
            row += 1

            ctk.CTkLabel(
                self.lista_frame,
                text=f"  Valor Atual: {formatar_moeda(inv['ta'] or 0)}",
                font=ctk.CTkFont(size=FONT_LABEL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=row, column=0, sticky="w", padx=SPACING_LG)
            row += 1

            sinal = "+" if lucro >= 0 else ""
            ctk.CTkLabel(
                self.lista_frame,
                text=f"  Lucro/Prejuizo: {sinal}{formatar_moeda(lucro)}",
                font=ctk.CTkFont(size=FONT_LABEL, weight="bold"),
                text_color=cl,
            ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_SM, SPACING_MD))
            row += 1

        saldo_cor = (
            self.colors.get("positive", "#00b894")
            if total_r >= total_d
            else self.colors.get("negative", "#d63031")
        )
        ctk.CTkLabel(
            self.lista_frame,
            text=f"  Saldo do Mes: {formatar_moeda(total_r - total_d)}",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=saldo_cor,
        ).grid(row=row, column=0, sticky="w", padx=SPACING_LG, pady=(SPACING_MD, SPACING_SM))

    def _exportar_csv(self):
        if not self._dados_cache:
            mostrar_toast(self, "Gere um relatorio primeiro!", "erro")
            return

        try:
            mes = self._dados_cache["mes"]
            filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            downloads_dir = os.path.expanduser("~/Downloads")
            filepath = os.path.join(downloads_dir, filename)

            with get_connection() as conn:
                receitas_linhas = conn.execute(
                    """SELECT r.data, r.descricao, r.valor,
                       COALESCE(c.nome,'Sem categoria') as categoria
                       FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                       WHERE strftime('%Y-%m',r.data)=? ORDER BY r.data""",
                    (mes,),
                ).fetchall()
                despesas_linhas = conn.execute(
                    """SELECT d.data, d.descricao, d.valor,
                       COALESCE(c.nome,'Sem categoria') as categoria
                       FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
                       WHERE strftime('%Y-%m',d.data)=? ORDER BY d.data""",
                    (mes,),
                ).fetchall()

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Data", "Descricao", "Tipo", "Valor", "Categoria"])

                for r in receitas_linhas:
                    writer.writerow([
                        r["data"], r["descricao"], "Receita",
                        f"{r['valor']:.2f}", r["categoria"],
                    ])

                for d in despesas_linhas:
                    writer.writerow([
                        d["data"], d["descricao"], "Despesa",
                        f"{d['valor']:.2f}", d["categoria"],
                    ])

            mostrar_toast(self, f"CSV exportado: {filename}!")
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao exportar CSV: %s", e)
            mostrar_toast(self, f"Erro ao exportar CSV: {str(e)[:50]}", "erro")
        except Exception as e:
            logger.error("Erro ao exportar CSV: %s", e)
            mostrar_toast(self, f"Erro ao exportar CSV: {str(e)[:50]}", "erro")

    def _exportar_pdf(self):
        if not self._dados_cache:
            mostrar_toast(self, "Gere um relatorio primeiro!", "erro")
            return

        try:
            from reportlab.lib.colors import HexColor
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.pdfgen import canvas

            d = self._dados_cache
            filename = f"relatorio_{d['mes']}.pdf"
            downloads_dir = os.path.expanduser("~/Downloads")
            filepath = os.path.join(downloads_dir, filename)

            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4

            c.setFillColor(HexColor(self.colors.get("bg_dark", "#0d0d1a")))
            c.rect(0, 0, width, height, fill=1)

            c.setFillColor(HexColor(self.colors.get("text", "#f0f0f8")))
            c.setFont("Helvetica-Bold", 20)
            c.drawString(2 * cm, height - 2 * cm, f"FinancePro - Relatorio {d['mes']}")

            c.setFont("Helvetica", 12)
            y = height - 3.5 * cm

            c.setFillColor(HexColor(self.colors.get("positive", "#00b894")))
            c.drawString(2 * cm, y, f"Receitas: {formatar_moeda(d['total_r'])}")
            y -= 0.8 * cm

            c.setFillColor(HexColor(self.colors.get("negative", "#d63031")))
            c.drawString(2 * cm, y, f"Despesas: {formatar_moeda(d['total_d'])}")
            y -= 0.8 * cm

            saldo_cor = (
                self.colors.get("positive", "#00b894")
                if d["saldo"] >= 0
                else self.colors.get("negative", "#d63031")
            )
            c.setFillColor(HexColor(saldo_cor))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, y, f"Saldo: {formatar_moeda(d['saldo'])}")
            y -= 1.5 * cm

            c.setFillColor(HexColor(self.colors.get("text", "#f0f0f8")))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2 * cm, y, "Detalhes por Categoria:")
            y -= 0.8 * cm

            c.setFont("Helvetica", 11)
            c.setFillColor(HexColor(self.colors.get("positive", "#00b894")))
            c.drawString(2 * cm, y, "Receitas:")
            y -= 0.6 * cm
            for r in d["receitas"]:
                c.setFillColor(HexColor(self.colors.get("text_secondary", "#a0a0b8")))
                c.drawString(2.5 * cm, y, f"{r['nome']}: {formatar_moeda(r['total'])}")
                y -= 0.5 * cm

            y -= 0.3 * cm
            c.setFillColor(HexColor(self.colors.get("negative", "#d63031")))
            c.drawString(2 * cm, y, "Despesas:")
            y -= 0.6 * cm
            for d_item in d["despesas"]:
                c.setFillColor(HexColor(self.colors.get("text_secondary", "#a0a0b8")))
                c.drawString(2.5 * cm, y, f"{d_item['nome']}: {formatar_moeda(d_item['total'])}")
                y -= 0.5 * cm

            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor(self.colors.get("text_dim", "#606078")))
            c.drawString(2 * cm, 1.5 * cm, f"Gerado em {obter_data_atual()} por FinancePro")

            c.save()
            mostrar_toast(self, f"PDF exportado: {filename}!")
        except ImportError:
            mostrar_toast(self, "Instale reportlab: pip install reportlab", "erro")
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao exportar PDF: %s", e)
            mostrar_toast(self, f"Erro ao exportar PDF: {str(e)[:50]}", "erro")
        except Exception as e:
            logger.error("Erro ao exportar PDF: %s", e)
            mostrar_toast(self, f"Erro ao exportar PDF: {str(e)[:50]}", "erro")
