"""Sidebar do FinancePro - Dark Premium com icones Unicode."""

import customtkinter as ctk

from constants import (
    BUTTON_CORNER_RADIUS,
    FONT_SMALL,
    ICONS,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
)


class Sidebar(ctk.CTkFrame):
    """Menu lateral com navegacao, tema e colapso."""

    def __init__(self, master, on_navigate=None, colors=None,
                 on_toggle_collapse=None, on_toggle_theme=None, collapsed=False):
        super().__init__(master, width=240, corner_radius=0,
                         fg_color=colors.get("sidebar_bg", "#12122a"))
        self.on_navigate = on_navigate
        self.colors = colors
        self.active_view = "dashboard"
        self._collapsed = collapsed
        self._on_toggle_collapse = on_toggle_collapse
        self._on_toggle_theme = on_toggle_theme

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_separator()
        self._build_menu()
        self._build_footer()

        self._update_active("dashboard")
        if self._collapsed:
            self._apply_collapsed_state()

    def _build_header(self):
        """Construi o cabecalho com logo e hamburger."""
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=SPACING_LG, pady=(SPACING_XL, SPACING_SM), sticky="ew")

        self.btn_hamburger = ctk.CTkButton(
            self.header,
            text=ICONS["menu"],
            font=ctk.CTkFont(size=18),
            width=30, height=30,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text_secondary", "#a0a0b8"),
            command=self._on_hamburger,
        )
        self.btn_hamburger.pack(side="left")

        self.lbl_logo = ctk.CTkLabel(
            self.header,
            text=ICONS["logo"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors.get("primary", "#6c5ce7"),
            width=36, height=36,
        )
        self.lbl_logo.pack(side="left", padx=(SPACING_SM, 0))

        self.lbl_title = ctk.CTkLabel(
            self.header,
            text="FinancePro",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        )
        self.lbl_title.pack(side="left", padx=(SPACING_SM, 0))

    def _build_separator(self):
        """Linha separadora."""
        self.separator = ctk.CTkFrame(
            self, fg_color=self.colors.get("border", "#2a2a48"), height=1,
        )
        self.separator.grid(row=1, column=0, padx=SPACING_LG, pady=(SPACING_SM, SPACING_MD), sticky="ew")

    def _build_menu(self):
        """Construi os itens do menu."""
        menu = [
            ("Dashboard", "dashboard", ICONS["dashboard"]),
            ("Receitas", "receitas", ICONS["receitas"]),
            ("Despesas", "despesas", ICONS["despesas"]),
            ("Investimentos", "investimentos", ICONS["investimentos"]),
            None,  # separador
            ("Categorias", "categorias", ICONS["categorias"]),
            ("Orcamento", "orcamento", ICONS["orcamento"]),
            ("Metas", "metas", ICONS["metas"]),
            ("Recorrentes", "recorrentes", ICONS["recorrentes"]),
            None,  # separador
            ("Relatorios", "relatorios", ICONS["relatorios"]),
            ("Configuracoes", "configuracoes", ICONS["configuracoes"]),
        ]

        self._menu_items = menu
        self.buttons = {}
        row = 2

        for item in menu:
            if item is None:
                # Separador
                sep = ctk.CTkFrame(
                    self, height=1,
                    fg_color=self.colors.get("border", "#2a2a48"),
                )
                sep.grid(row=row, column=0, padx=SPACING_LG + SPACING_SM,
                         pady=SPACING_SM, sticky="ew")
                row += 1
                continue

            label, view, icon = item
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
                hover_color=self.colors.get("bg_hover", "#252550"),
                height=40,
                corner_radius=BUTTON_CORNER_RADIUS,
                command=lambda v=view: self.navegar(v),
            )
            btn.grid(row=row, column=0, padx=SPACING_SM, pady=2, sticky="ew")
            self.buttons[view] = btn
            row += 1

        # Empurra footer para baixo
        self.grid_rowconfigure(row, weight=1)

    def _build_footer(self):
        """Rodape com versao e botao de tema."""
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=100, column=0, padx=SPACING_LG,
                         pady=(SPACING_MD, SPACING_XL), sticky="sew")

        ctk.CTkFrame(
            self.footer, fg_color=self.colors.get("border", "#2a2a48"), height=1,
        ).pack(fill="x", pady=(0, SPACING_MD))

        footer_row = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_row.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(
            footer_row,
            text="v5.0",
            font=ctk.CTkFont(size=FONT_SMALL),
            text_color=self.colors.get("text_dim", "#606078"),
        )
        self.lbl_version.pack(side="left")

        self.btn_theme = ctk.CTkButton(
            footer_row,
            text=ICONS["moon"],
            font=ctk.CTkFont(size=14),
            width=30, height=30,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text", "#f0f0f8"),
            command=self._on_theme_click,
        )
        self.btn_theme.pack(side="right")

    def _on_hamburger(self):
        if self._on_toggle_collapse:
            self._on_toggle_collapse()

    def _on_theme_click(self):
        if self._on_toggle_theme:
            self._on_toggle_theme()

    def set_collapsed(self, collapsed):
        """Alterna entre modo colapsado e expandido."""
        self._collapsed = collapsed
        if collapsed:
            self._apply_collapsed_state()
        else:
            self._apply_expanded_state()

    def _apply_collapsed_state(self):
        """Modo colapsado: apenas icones, 60px."""
        self.configure(width=60)
        self.lbl_title.pack_forget()

        for view, btn in self.buttons.items():
            for item in self._menu_items:
                if item is not None and item[1] == view:
                    btn.configure(text=item[2], anchor="center",
                                  font=ctk.CTkFont(size=16))
                    break

        self.header.grid_configure(padx=SPACING_SM)
        self.separator.grid_configure(padx=SPACING_SM)

        # Limpa footer
        for child in self.footer.winfo_children():
            child.destroy()

        self.btn_theme = ctk.CTkButton(
            self.footer,
            text=ICONS["moon"],
            font=ctk.CTkFont(size=14),
            width=30, height=30,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text", "#f0f0f8"),
            command=self._on_theme_click,
        )
        self.btn_theme.pack(pady=(0, 4))

        self.lbl_version = ctk.CTkLabel(
            self.footer, text="v5",
            font=ctk.CTkFont(size=9),
            text_color=self.colors.get("text_dim", "#606078"),
        )
        self.lbl_version.pack()

    def _apply_expanded_state(self):
        """Modo expandido: icones + texto, 240px."""
        self.configure(width=240)
        self.header.grid_configure(padx=SPACING_LG)
        self.separator.grid_configure(padx=SPACING_LG)

        self.lbl_title = ctk.CTkLabel(
            self.header, text="FinancePro",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        )
        self.lbl_title.pack(side="left", padx=(SPACING_SM, 0))

        # Limpa e reconstrui footer
        for child in self.footer.winfo_children():
            child.destroy()

        ctk.CTkFrame(
            self.footer, fg_color=self.colors.get("border", "#2a2a48"), height=1,
        ).pack(fill="x", pady=(0, SPACING_MD))

        footer_row = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_row.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(
            footer_row, text="v5.0",
            font=ctk.CTkFont(size=FONT_SMALL),
            text_color=self.colors.get("text_dim", "#606078"),
        )
        self.lbl_version.pack(side="left")

        self.btn_theme = ctk.CTkButton(
            footer_row,
            text=ICONS["moon"],
            font=ctk.CTkFont(size=14),
            width=30, height=30,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#252550"),
            text_color=self.colors.get("text", "#f0f0f8"),
            command=self._on_theme_click,
        )
        self.btn_theme.pack(side="right")

        for view, btn in self.buttons.items():
            for item in self._menu_items:
                if item is not None and item[1] == view:
                    btn.configure(
                        text=f"  {item[2]}  {item[0]}",
                        anchor="w",
                        font=ctk.CTkFont(size=14),
                    )
                    break

    def update_colors(self, colors):
        """Atualiza cores de todos os elementos."""
        self.colors = colors
        self.configure(fg_color=colors.get("sidebar_bg", "#12122a"))
        self.lbl_logo.configure(text_color=colors.get("primary", "#6c5ce7"))
        self.separator.configure(fg_color=colors.get("border", "#2a2a48"))

        if hasattr(self, "lbl_title") and self.lbl_title.winfo_exists():
            self.lbl_title.configure(text_color=colors.get("text", "#f0f0f8"))

        for name, btn in self.buttons.items():
            if name == self.active_view:
                btn.configure(
                    fg_color=colors.get("primary_muted", "#3d3580"),
                    text_color=colors.get("text", "#f0f0f8"),
                    hover_color=colors.get("primary_hover", "#5a4bd1"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=colors.get("text_secondary", "#a0a0b8"),
                    hover_color=colors.get("bg_hover", "#252550"),
                )

        theme_icon = ICONS["moon"] if "bg_dark" in colors and colors.get("bg_dark") == "#0d0d1a" else ICONS["sun"]
        if hasattr(self, "btn_theme") and self.btn_theme.winfo_exists():
            self.btn_theme.configure(
                text=theme_icon,
                hover_color=colors.get("bg_hover", "#252550"),
                text_color=colors.get("text", "#f0f0f8"),
            )
        if hasattr(self, "lbl_version") and self.lbl_version.winfo_exists():
            self.lbl_version.configure(text_color=colors.get("text_dim", "#606078"))

    def navegar(self, view_name):
        """Navega para a view indicada."""
        self._update_active(view_name)
        if self.on_navigate:
            self.on_navigate(view_name)

    def _update_active(self, view_name):
        """Atualiza visual do botao ativo com barra lateral."""
        self.active_view = view_name
        for name, btn in self.buttons.items():
            if name == view_name:
                btn.configure(
                    fg_color=self.colors.get("primary_muted", "#3d3580"),
                    text_color=self.colors.get("text", "#f0f0f8"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors.get("text_secondary", "#a0a0b8"),
                )

