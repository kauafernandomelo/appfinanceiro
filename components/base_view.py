"""Classe base para todas as views do FinancePro - Dark Premium."""

import customtkinter as ctk

from components.modals import ConfirmarExclusaoModal
from components.toast import mostrar_toast
from constants import (
    BUTTON_CORNER_RADIUS,
    CARD_CORNER_RADIUS,
    FONT_BODY,
    FONT_LABEL,
    FONT_TITLE,
    SPACING_SM,
)


class BaseView(ctk.CTkFrame):
    """Classe base com helpers compartilhados para todas as views."""

    def __init__(self, master, colors=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors or {}
        self.grid_columnconfigure(0, weight=1)

    def _criar_entry(self, parent, placeholder="", **kwargs):
        """Cria um campo de entrada estilizado."""
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY),
            fg_color=self.colors.get("bg_elevated", "#1e1e3a"),
            border_color=self.colors.get("border", "#2a2a48"),
            text_color=self.colors.get("text", "#f0f0f8"),
            placeholder_text_color=self.colors.get("text_dim", "#606078"),
            border_width=1,
            **kwargs,
        )

    def _criar_combo(self, parent, values, **kwargs):
        """Cria um ComboBox estilizado."""
        return ctk.CTkComboBox(
            parent,
            values=values,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY),
            fg_color=self.colors.get("bg_elevated", "#1e1e3a"),
            border_color=self.colors.get("border", "#2a2a48"),
            button_color=self.colors.get("primary", "#6c5ce7"),
            button_hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            dropdown_fg_color=self.colors.get("bg_elevated", "#1e1e3a"),
            dropdown_hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text", "#f0f0f8"),
            border_width=1,
            **kwargs,
        )

    def _criar_label(self, parent, text, **kwargs):
        """Cria um label estilizado."""
        defaults = {
            "font": ctk.CTkFont(size=FONT_LABEL),
            "text_color": self.colors.get("text_secondary", "#a0a0b8"),
        }
        defaults.update(kwargs)
        return ctk.CTkLabel(parent, text=text, **defaults)

    def _criar_titulo(self, parent, text):
        """Cria o titulo da pagina."""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=FONT_TITLE, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        )

    def _criar_card_frame(self, parent, **kwargs):
        """Cria um card com borda sutil e elevacao."""
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors.get("bg_card", "#161630"),
            corner_radius=CARD_CORNER_RADIUS,
            border_width=1,
            border_color=self.colors.get("border", "#2a2a48"),
            **kwargs,
        )

    def _criar_lista_frame(self, parent):
        """Cria um container de lista com scroll e borda."""
        container = self._criar_card_frame(parent)
        lista = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=self.colors.get("border", "#2a2a48"),
            scrollbar_button_hover_color=self.colors.get("border_light", "#353560"),
        )
        lista.pack(fill="both", expand=True, padx=SPACING_SM, pady=SPACING_SM)
        lista.grid_columnconfigure(0, weight=1)
        return container, lista

    def _criar_separador(self, parent):
        """Cria uma linha separadora horizontal."""
        return ctk.CTkFrame(
            parent,
            height=1,
            fg_color=self.colors.get("border", "#2a2a48"),
        )

    def _criar_status_badge(self, parent, texto, cor):
        """Cria um badge de status colorido."""
        badge = ctk.CTkFrame(
            parent,
            fg_color=cor,
            corner_radius=4,
            height=22,
        )
        badge.grid_propagate(False)
        ctk.CTkLabel(
            badge,
            text=texto,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#ffffff",
        ).pack(padx=6, pady=2)
        return badge

    def _confirmar_exclusao(self, titulo, mensagem):
        """Exibe modal de confirmacao de exclusao."""
        modal = ConfirmarExclusaoModal(self, titulo, mensagem, colors=self.colors)
        self.wait_window(modal)
        return modal.resultado

    def _validar_campos(self, campos: dict) -> bool:
        """Valida que todos os campos obrigatorios estao preenchidos."""
        for nome, valor in campos.items():
            if not valor or not valor.strip():
                mostrar_toast(self, f"Preencha o campo: {nome}", "erro")
                return False
        return True

    def _validar_valor(self, valor: str) -> float | None:
        """Valida e converte string para float."""
        try:
            val = float(valor.replace(",", "."))
            if val <= 0:
                mostrar_toast(self, "O valor deve ser maior que zero.", "erro")
                return None
            return val
        except (ValueError, AttributeError):
            mostrar_toast(self, "Valor invalido! Use apenas numeros.", "erro")
            return None
