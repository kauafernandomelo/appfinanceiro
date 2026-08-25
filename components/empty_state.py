"""Componente de estado vazio - Dark Premium."""

import customtkinter as ctk

from constants import FONT_BODY, SPACING_LG


class EmptyState(ctk.CTkFrame):
    """Componente para exibir quando nao ha dados."""

    def __init__(self, master, icone="\u25A0", titulo="Nenhum registro",
                 subtitulo="Adicione dados para comecar", colors=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors or {}

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, pady=40)

        ctk.CTkLabel(
            container,
            text=icone,
            font=ctk.CTkFont(size=48),
            text_color=self.colors.get("text_dim", "#606078"),
        ).pack(pady=(0, SPACING_LG))

        ctk.CTkLabel(
            container,
            text=titulo,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors.get("text_secondary", "#a0a0b8"),
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            container,
            text=subtitulo,
            font=ctk.CTkFont(size=FONT_BODY),
            text_color=self.colors.get("text_dim", "#606078"),
        ).pack()
