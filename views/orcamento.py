"""View de Orcamento Mensal - Dark Premium."""

import logging
import sqlite3

import customtkinter as ctk

from components.base_view import BaseView
from components.empty_state import EmptyState
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from constants import (
    ACTION_BUTTON_SIZE,
    BUTTON_CORNER_RADIUS,
    FONT_BODY,
    FONT_CARD_TITLE,
    FONT_LABEL,
    FONT_SMALL,
    ICONS,
    PROGRESS_BAR_HEIGHT,
    ROW_HEIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
)
from database import get_connection
from utils import formatar_moeda, obter_mes_atual

logger = logging.getLogger("financeiro.orcamento")


class OrcamentoView(BaseView):
    """View de orcamento mensal com alertas de uso."""

    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._criar_header()
        self._criar_resumo()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, "Orcamento Mensal").pack(side="left")
        ctk.CTkLabel(
            header, text=obter_mes_atual(),
            font=ctk.CTkFont(size=FONT_BODY),
            text_color=self.colors.get("text_dim", "#606078"),
        ).pack(side="right")

    def _criar_resumo(self):
        self.resumo_frame = self._criar_card_frame(self)
        self.resumo_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_MD))
        r = ctk.CTkFrame(self.resumo_frame, fg_color="transparent")
        r.pack(fill="x", padx=SPACING_XL, pady=SPACING_MD)
        r.grid_columnconfigure((0, 1), weight=1)

        self.lbl_total_limite = self._criar_label(
            r, "Limite Total: R$ 0,00",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        )
        self.lbl_total_limite.grid(row=0, column=0, sticky="w")

        self.lbl_total_gasto = self._criar_label(
            r, "Total Gasto: R$ 0,00",
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        )
        self.lbl_total_gasto.grid(row=0, column=1, sticky="e")

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=2, column=0, sticky="ew", pady=(0, SPACING_MD))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)
        g.grid_columnconfigure((0, 1, 2), weight=1)

        self._criar_label(g, "Categoria*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=0, sticky="w", pady=(0, SPACING_SM))
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=0, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Limite (R$)*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=1, sticky="w", pady=(0, SPACING_SM))
        self.entry_limite = self._criar_entry(g, "0,00")
        self.entry_limite.grid(row=1, column=1, sticky="ew", padx=(0, SPACING_SM))

        ctk.CTkButton(
            g, text="Definir Limite", height=38, corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._salvar,
        ).grid(row=1, column=2, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._atualizar()

    def _cats(self):
        try:
            with get_connection() as conn:
                cats = conn.execute(
                    "SELECT nome FROM categorias WHERE tipo='despesa' ORDER BY nome"
                ).fetchall()
            return [c["nome"] for c in cats] if cats else ["Sem categoria"]
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categorias: %s", e)
            return ["Sem categoria"]

    def _salvar(self):
        cat = self.combo_cat.get()
        lim_str = self.entry_limite.get().replace(",", ".").strip()
        if not self._validar_campos({"Limite": lim_str}):
            return
        lim = self._validar_valor(lim_str)
        if lim is None:
            return

        try:
            with get_connection() as conn:
                c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
                if not c:
                    mostrar_toast(self, "Categoria nao encontrada", "erro")
                    return
                mes = obter_mes_atual()
                ex = conn.execute(
                    "SELECT id FROM orcamento WHERE categoria_id=? AND mes=?",
                    (c["id"], mes),
                ).fetchone()
                if ex:
                    conn.execute("UPDATE orcamento SET limite=? WHERE id=?", (lim, ex["id"]))
                else:
                    conn.execute(
                        "INSERT INTO orcamento (categoria_id,limite,mes) VALUES (?,?,?)",
                        (c["id"], lim, mes),
                    )
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao salvar orcamento: %s", e)
            mostrar_toast(self, f"Erro ao salvar: {e}", "erro")
            return

        self.entry_limite.delete(0, "end")
        mostrar_toast(self, "Orcamento atualizado!")
        self._atualizar()
        self._verificar_alertas()

    def _verificar_alertas(self):
        mes = obter_mes_atual()
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT COALESCE(c.nome,'?') as cat, o.limite,
                              COALESCE(SUM(d.valor),0) as gasto
                       FROM orcamento o
                       LEFT JOIN categorias c ON o.categoria_id=c.id
                       LEFT JOIN despesas d ON d.categoria_id=c.id AND strftime('%Y-%m',d.data)=o.mes
                       WHERE o.mes=? GROUP BY o.id""", (mes,),
                ).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao verificar alertas: %s", e)
            return

        for o in rows:
            pct = (o["gasto"] / o["limite"] * 100) if o["limite"] > 0 else 0
            if pct > 100:
                mostrar_toast(self, f"Limite excedido em {o['cat']}! ({pct:.0f}%)", "erro")
            elif pct >= 80:
                mostrar_toast(self, f"{o['cat']} proximo do limite! ({pct:.0f}%)", "aviso")

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        mes = obter_mes_atual()

        total_limite = 0
        total_gasto = 0

        try:
            with get_connection() as conn:
                rows = conn.execute(
                    """SELECT o.id, COALESCE(c.nome,'?') as cat, o.limite,
                              COALESCE(SUM(d.valor),0) as gasto
                       FROM orcamento o
                       LEFT JOIN categorias c ON o.categoria_id=c.id
                       LEFT JOIN despesas d ON d.categoria_id=c.id AND strftime('%Y-%m',d.data)=o.mes
                       WHERE o.mes=? GROUP BY o.id""", (mes,),
                ).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar orcamentos: %s", e)
            mostrar_toast(self, f"Erro ao carregar: {e}", "erro")
            return

        for o in rows:
            total_limite += o["limite"]
            total_gasto += o["gasto"]

        if total_limite > 0:
            pct_total = (total_gasto / total_limite * 100)
            self.lbl_total_limite.configure(text=f"Limite Total: {formatar_moeda(total_limite)}")
            cor_total = (
                self.colors.get("positive", "#00b894") if pct_total <= 80
                else self.colors.get("warning", "#fdcb6e") if pct_total <= 100
                else self.colors.get("negative", "#d63031")
            )
            self.lbl_total_gasto.configure(
                text=f"Total Gasto: {formatar_moeda(total_gasto)} ({pct_total:.0f}%)",
                text_color=cor_total,
            )
        else:
            self.lbl_total_limite.configure(text="Limite Total: R$ 0,00")
            self.lbl_total_gasto.configure(
                text="Total Gasto: R$ 0,00",
                text_color=self.colors.get("text", "#f0f0f8"),
            )

        if not rows:
            EmptyState(
                self.lista, icone=ICONS["orcamento"],
                titulo="Nenhum orcamento definido",
                subtitulo="Selecione uma categoria e defina um limite",
                colors=self.colors,
            ).grid(row=0, column=0, pady=40)
            return

        for i, o in enumerate(rows):
            row_bg = (self.colors.get("bg_card", "#161630") if i % 2 == 0
                      else self.colors.get("bg_elevated", "#1e1e3a"))
            row = ctk.CTkFrame(
                self.lista, fg_color=row_bg,
                corner_radius=BUTTON_CORNER_RADIUS, height=ROW_HEIGHT + 16,
            )
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(1, weight=1)
            row.grid_propagate(False)

            # Hover effect
            def on_enter(e, r=row):
                r.configure(fg_color=self.colors.get("bg_hover", "#252550"))
            def on_leave(e, r=row, bg=row_bg):
                r.configure(fg_color=bg)
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

            # Categoria
            ctk.CTkLabel(
                row, text=o["cat"],
                font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).grid(row=0, column=0, padx=SPACING_LG, pady=SPACING_SM, sticky="w")

            # Progress bar
            pct = (o["gasto"] / o["limite"] * 100) if o["limite"] > 0 else 0
            bc = (
                self.colors.get("positive", "#00b894") if pct <= 80
                else self.colors.get("warning", "#fdcb6e") if pct <= 100
                else self.colors.get("negative", "#d63031")
            )

            bf = ctk.CTkFrame(row, fg_color="transparent")
            bf.grid(row=0, column=1, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
            bf.grid_columnconfigure(0, weight=1)

            bar = ctk.CTkProgressBar(
                bf, progress_color=bc,
                height=PROGRESS_BAR_HEIGHT, corner_radius=6,
            )
            bar.grid(row=0, column=0, sticky="ew")
            bar.set(min(pct / 100, 1.0))

            ctk.CTkLabel(
                bf,
                text=f"{formatar_moeda(o['gasto'])} / {formatar_moeda(o['limite'])}  ({pct:.0f}%)",
                font=ctk.CTkFont(size=FONT_SMALL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=1, column=0, sticky="w", pady=(SPACING_XS, 0))

            # Botao excluir
            btn_excluir = ctk.CTkButton(
                row, text=ICONS["delete"],
                width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                fg_color=self.colors.get("negative", "#d63031"),
                hover_color=self.colors.get("negative_muted", "#a32525"),
                command=lambda oid=o["id"]: self._excluir(oid),
            )
            btn_excluir.grid(row=0, column=2, padx=SPACING_LG, pady=SPACING_SM)
            Tooltip(btn_excluir, "Excluir orcamento", self.colors)

    def _excluir(self, oid):
        if not self._confirmar_exclusao("Excluir Orcamento", "Deseja excluir este orcamento?"):
            return
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM orcamento WHERE id=?", (oid,))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao excluir orcamento: %s", e)
            mostrar_toast(self, f"Erro ao excluir: {e}", "erro")
            return
        mostrar_toast(self, "Orcamento removido!")
        self._atualizar()
