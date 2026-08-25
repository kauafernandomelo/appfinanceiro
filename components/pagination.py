"""Componente de paginacao reutilizavel - Dark Premium."""

import customtkinter as ctk

from constants import BUTTON_CORNER_RADIUS, FONT_SMALL, SPACING_SM


class PaginationBar(ctk.CTkFrame):
    """Barra de paginacao com setas e info de registros."""

    def __init__(self, master, colors=None, on_page_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors or {}
        self.on_page_change = on_page_change
        self.pagina_atual = 1
        self.total_paginas = 1
        self.total_registros = 0

        btn_cfg = {
            "width": 32,
            "height": 28,
            "corner_radius": BUTTON_CORNER_RADIUS,
            "font": ctk.CTkFont(size=FONT_SMALL),
            "fg_color": self.colors.get("bg_elevated", "#1e1e3a"),
            "hover_color": self.colors.get("bg_hover", "#252550"),
            "border_width": 1,
            "border_color": self.colors.get("border", "#2a2a48"),
            "text_color": self.colors.get("text", "#f0f0f8"),
        }

        self.btn_prev = ctk.CTkButton(
            self, text="\u25C0", command=self._prev, **btn_cfg,
        )
        self.btn_prev.pack(side="left", padx=(0, SPACING_SM))

        self.lbl_info = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=FONT_SMALL),
            text_color=self.colors.get("text_secondary", "#a0a0b8"),
        )
        self.lbl_info.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(
            self, text="\u25B6", command=self._next, **btn_cfg,
        )
        self.btn_next.pack(side="right", padx=(SPACING_SM, 0))

    def atualizar(self, pagina_atual, total_paginas, total_registros, inicio, fim):
        """Atualiza o estado da paginacao."""
        self.pagina_atual = pagina_atual
        self.total_paginas = total_paginas
        self.total_registros = total_registros

        self.lbl_info.configure(
            text=f"Mostrando {inicio}-{fim} de {total_registros} registros"
        )

        self.btn_prev.configure(
            state="normal" if pagina_atual > 1 else "disabled",
            fg_color=self.colors.get("bg_elevated", "#1e1e3a") if pagina_atual > 1
            else self.colors.get("bg_card", "#161630"),
        )
        self.btn_next.configure(
            state="normal" if pagina_atual < total_paginas else "disabled",
            fg_color=self.colors.get("bg_elevated", "#1e1e3a") if pagina_atual < total_paginas
            else self.colors.get("bg_card", "#161630"),
        )

    def _prev(self):
        if self.pagina_atual > 1 and self.on_page_change:
            self.on_page_change(self.pagina_atual - 1)

    def _next(self):
        if self.pagina_atual < self.total_paginas and self.on_page_change:
            self.on_page_change(self.pagina_atual + 1)
