"""View de Metas de Economia - Dark Premium."""

import logging
import sqlite3

import customtkinter as ctk

from components.base_view import BaseView
from components.datepicker import DatePicker
from components.empty_state import EmptyState
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from constants import (
    ACTION_BUTTON_SIZE,
    BUTTON_CORNER_RADIUS,
    FONT_BODY,
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
from utils import formatar_moeda, formatar_percentual

logger = logging.getLogger("financeiro.metas")


class MetasView(BaseView):
    """View de metas de economia com progresso visual."""

    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, "Metas de Economia").pack(side="left")

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_MD))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)
        g.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._criar_label(g, "Nome da Meta*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=0, sticky="w", pady=(0, SPACING_SM))
        self.entry_nome = self._criar_entry(g, "Ex: Viagem, Reserva...")
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Valor Alvo (R$)*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=1, sticky="w", pady=(0, SPACING_SM))
        self.entry_alvo = self._criar_entry(g, "0,00")
        self.entry_alvo.grid(row=1, column=1, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Prazo*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=2, sticky="w", pady=(0, SPACING_SM))
        self.dp_prazo = DatePicker(g, colors=self.colors)
        self.dp_prazo.grid(row=1, column=2, sticky="ew", padx=(0, SPACING_SM))

        ctk.CTkButton(
            g, text=f"{ICONS['add']} Adicionar", height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._salvar,
        ).grid(row=1, column=3, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=2, column=0, sticky="nsew")
        self._atualizar()

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        alvo_str = self.entry_alvo.get().replace(",", ".").strip()
        prazo = self.dp_prazo.get()

        if not self._validar_campos({"Nome": nome, "Valor Alvo": alvo_str, "Prazo": prazo}):
            return
        alvo = self._validar_valor(alvo_str)
        if alvo is None:
            return

        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO metas (nome, valor_alvo, valor_atual, prazo) VALUES (?, ?, 0, ?)",
                    (nome, alvo, prazo),
                )
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao salvar meta: %s", e)
            mostrar_toast(self, f"Erro ao salvar: {e}", "erro")
            return

        self.entry_nome.delete(0, "end")
        self.entry_alvo.delete(0, "end")
        self.dp_prazo.set("")
        mostrar_toast(self, f"Meta '{nome}' criada!")
        self._atualizar()

    def _adicionar_valor(self, mid):
        """Adiciona valor a uma meta existente."""
        for w in self.lista.winfo_children():
            if hasattr(w, "_meta_id") and w._meta_id == mid:
                entry = w._entry_add
                val_str = entry.get().replace(",", ".").strip()
                if not val_str:
                    return
                try:
                    val = float(val_str)
                except ValueError:
                    mostrar_toast(self, "Valor invalido!", "erro")
                    return

                try:
                    with get_connection() as conn:
                        meta = conn.execute("SELECT valor_alvo, valor_atual FROM metas WHERE id=?", (mid,)).fetchone()
                        if not meta:
                            return
                        novo_atual = meta["valor_atual"] + val
                        conn.execute("UPDATE metas SET valor_atual=? WHERE id=?", (novo_atual, mid))
                        conn.commit()
                except (sqlite3.Error, ValueError) as e:
                    logger.error("Erro ao adicionar valor: %s", e)
                    mostrar_toast(self, f"Erro: {e}", "erro")
                    return

                entry.delete(0, "end")
                mostrar_toast(self, f"+{formatar_moeda(val)} adicionado!")
                self._atualizar()
                break

    def _excluir(self, mid):
        if not self._confirmar_exclusao("Excluir Meta", "Deseja excluir esta meta?"):
            return
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM metas WHERE id=?", (mid,))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao excluir meta: %s", e)
            mostrar_toast(self, f"Erro ao excluir: {e}", "erro")
            return
        mostrar_toast(self, "Meta excluida!")
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        try:
            with get_connection() as conn:
                rows = conn.execute("SELECT * FROM metas ORDER BY prazo").fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar metas: %s", e)
            mostrar_toast(self, f"Erro ao carregar: {e}", "erro")
            return

        if not rows:
            EmptyState(
                self.lista, icone=ICONS["metas"],
                titulo="Nenhuma meta definida",
                subtitulo="Crie sua primeira meta de economia",
                colors=self.colors,
            ).grid(row=0, column=0, pady=40)
            return

        for i, m in enumerate(rows):
            row_bg = (self.colors.get("bg_card", "#161630") if i % 2 == 0
                      else self.colors.get("bg_elevated", "#1e1e3a"))
            row = ctk.CTkFrame(
                self.lista, fg_color=row_bg,
                corner_radius=BUTTON_CORNER_RADIUS, height=ROW_HEIGHT + 24,
            )
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(1, weight=1)
            row.grid_propagate(False)
            row._meta_id = m["id"]

            # Hover
            def on_enter(e, r=row):
                r.configure(fg_color=self.colors.get("bg_hover", "#252550"))
            def on_leave(e, r=row, bg=row_bg):
                r.configure(fg_color=bg)
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

            # Info da meta
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=0, padx=SPACING_LG, pady=SPACING_SM, sticky="w")

            ctk.CTkLabel(
                info, text=m["nome"],
                font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=f"{formatar_moeda(m['valor_atual'])} / {formatar_moeda(m['valor_alvo'])}  |  Prazo: {m['prazo']}",
                font=ctk.CTkFont(size=FONT_SMALL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).pack(anchor="w", pady=(2, 0))

            # Progress bar
            pct = (m["valor_atual"] / m["valor_alvo"] * 100) if m["valor_alvo"] > 0 else 0
            if pct >= 100:
                cor = self.colors.get("positive", "#00b894")
            elif pct >= 50:
                cor = self.colors.get("warning", "#fdcb6e")
            else:
                cor = self.colors.get("negative", "#d63031")

            pf = ctk.CTkFrame(row, fg_color="transparent")
            pf.grid(row=0, column=1, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
            pf.grid_columnconfigure(0, weight=1)

            bar = ctk.CTkProgressBar(
                pf, progress_color=cor,
                height=PROGRESS_BAR_HEIGHT, corner_radius=6,
            )
            bar.grid(row=0, column=0, sticky="ew")
            bar.set(min(pct / 100, 1.0))

            ctk.CTkLabel(
                pf, text=formatar_percentual(pct),
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                text_color=cor,
            ).grid(row=1, column=0, sticky="w", pady=(SPACING_XS, 0))

            # Adicionar valor inline
            add_frame = ctk.CTkFrame(row, fg_color="transparent")
            add_frame.grid(row=0, column=2, padx=SPACING_SM, pady=SPACING_SM, sticky="e")

            entry_add = ctk.CTkEntry(
                add_frame, placeholder_text="+R$", width=80, height=28,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=FONT_SMALL),
                fg_color=self.colors.get("bg_elevated", "#1e1e3a"),
                border_color=self.colors.get("border", "#2a2a48"),
                text_color=self.colors.get("text", "#f0f0f8"),
                border_width=1,
            )
            entry_add.pack(side="left", padx=(0, SPACING_XS))
            row._entry_add = entry_add

            btn_add = ctk.CTkButton(
                add_frame, text=ICONS["add"], width=28, height=28,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=FONT_SMALL),
                fg_color=self.colors.get("positive", "#00b894"),
                hover_color=self.colors.get("positive_muted", "#00875f"),
                command=lambda mid=m["id"]: self._adicionar_valor(mid),
            )
            btn_add.pack(side="left")

            # Botao excluir
            btn_excluir = ctk.CTkButton(
                row, text=ICONS["delete"],
                width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                fg_color=self.colors.get("negative", "#d63031"),
                hover_color=self.colors.get("negative_muted", "#a32525"),
                command=lambda mid=m["id"]: self._excluir(mid),
            )
            btn_excluir.grid(row=0, column=3, padx=SPACING_LG, pady=SPACING_SM)
            Tooltip(btn_excluir, "Excluir meta", self.colors)
