import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None, colors=None, on_toggle_collapse=None, on_toggle_theme=None, collapsed=False):
        super().__init__(master, width=240, corner_radius=0, fg_color=colors["bg_card"])
        self.on_navigate = on_navigate
        self.colors = colors
        self.active_view = "dashboard"
        self._collapsed = collapsed
        self._on_toggle_collapse = on_toggle_collapse
        self._on_toggle_theme = on_toggle_theme

        self.grid_propagate(False)
        self.grid_rowconfigure(11, weight=1)

        self._build_header()
        self._build_separator()
        self._build_menu_label()
        self._build_menu_buttons()
        self._build_footer()

        self._update_active("dashboard")
        if self._collapsed:
            self._apply_collapsed_state()

    def _build_header(self):
        """Construi o cabecalho da sidebar com logo e botao hamburger."""
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="ew")

        self.btn_hamburger = ctk.CTkButton(
            self.header,
            text="\u2630",
            font=ctk.CTkFont(size=20),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#16213e"),
            text_color=self.colors.get("text", "#fff"),
            command=self._on_hamburger,
        )
        self.btn_hamburger.pack(side="left")

        self.lbl_logo = ctk.CTkLabel(
            self.header,
            text="$",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("accent", "#00cec9"),
            width=40,
            height=40,
        )
        self.lbl_logo.pack(side="left", padx=(4, 0))

        self.lbl_title = ctk.CTkLabel(
            self.header,
            text="FinancePro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        )
        self.lbl_title.pack(side="left", padx=(8, 0))

    def _build_separator(self):
        """Construi a linha separadora apos o cabecalho."""
        self.separator = ctk.CTkFrame(self, fg_color=self.colors.get("border", "#2d2d44"), height=1)
        self.separator.grid(row=1, column=0, padx=20, pady=(8, 16), sticky="ew")

    def _build_menu_label(self):
        """Construi o rotulo do menu principal."""
        self.lbl_menu = ctk.CTkLabel(
            self,
            text="MENU PRINCIPAL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors.get("text_dim", "#a0a0b0"),
            anchor="w",
        )
        self.lbl_menu.grid(row=2, column=0, padx=24, pady=(0, 8), sticky="w")

    def _build_menu_buttons(self):
        """Construi os botoes do menu de navegacao."""
        menu = [
            ("Dashboard", "dashboard", "\U0001F4CA"),
            ("Receitas", "receitas", "\U0001F4B5"),
            ("Despesas", "despesas", "\U0001F4B8"),
            ("Investimentos", "investimentos", "\U0001F4C8"),
            ("Categorias", "categorias", "\U0001F3F7\uFE0F"),
            ("Orcamento", "orcamento", "\U0001F4CB"),
            ("Metas", "metas", "\U0001F3AF"),
            ("Recorrentes", "recorrentes", "\U0001F504"),
            ("Relatorios", "relatorios", "\U0001F4C8"),
        ]

        self._menu_items = menu
        self.buttons = {}

        for i, (label, view, icon) in enumerate(menu):
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=self.colors.get("text_dim", "#a0a0b0"),
                hover_color=self.colors.get("bg_hover", "#16213e"),
                height=40,
                corner_radius=8,
                command=lambda v=view: self.navegar(v),
            )
            btn.grid(row=i + 3, column=0, padx=12, pady=2, sticky="ew")
            self.buttons[view] = btn

    def _build_footer(self):
        """Construi o rodape da sidebar com versao e botao de tema."""
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=12, column=0, padx=20, pady=(16, 20), sticky="sew")

        ctk.CTkFrame(self.footer, fg_color=self.colors.get("border", "#2d2d44"), height=1).pack(
            fill="x", pady=(0, 12)
        )

        footer_row = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_row.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(
            footer_row,
            text="v2.0.0",
            font=ctk.CTkFont(size=11),
            text_color=self.colors.get("text_dim", "#a0a0b0"),
        )
        self.lbl_version.pack(side="left")

        self.btn_theme = ctk.CTkButton(
            footer_row,
            text="\u263E" if self.colors.get("bg_dark") == "#0f0f1a" else "\u2600",
            font=ctk.CTkFont(size=16),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#16213e"),
            text_color=self.colors.get("text", "#fff"),
            command=self._on_theme_click,
        )
        self.btn_theme.pack(side="right")

    def _on_hamburger(self):
        """Lida com o clique no botao hamburger para colapsar/expandir."""
        if self._on_toggle_collapse:
            self._on_toggle_collapse()

    def _on_theme_click(self):
        """Lida com o clique no botao de alternar tema."""
        if self._on_toggle_theme:
            self._on_toggle_theme()

    def set_collapsed(self, collapsed):
        """Define o estado colapsado da sidebar e reconstroi os botoes."""
        self._collapsed = collapsed
        if collapsed:
            self._apply_collapsed_state()
        else:
            self._apply_expanded_state()

    def _apply_collapsed_state(self):
        """Aplica visual colapsado: apenas icones, largura 60px."""
        self.configure(width=60)
        self.lbl_title.pack_forget()
        self.lbl_menu.grid_forget()
        self.lbl_version.pack_forget()
        self.btn_theme.pack_forget()

        footer_row = self.footer.winfo_children()
        for child in footer_row:
            child.destroy()

        self.btn_theme = ctk.CTkButton(
            self.footer,
            text="\u263E" if self.colors.get("bg_dark") == "#0f0f1a" else "\u2600",
            font=ctk.CTkFont(size=16),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#16213e"),
            text_color=self.colors.get("text", "#fff"),
            command=self._on_theme_click,
        )
        self.btn_theme.pack(pady=(0, 4))

        self.lbl_version_collapsed = ctk.CTkLabel(
            self.footer,
            text="v2.0",
            font=ctk.CTkFont(size=9),
            text_color=self.colors.get("text_dim", "#a0a0b0"),
        )
        self.lbl_version_collapsed.pack()

        for view, btn in self.buttons.items():
            for item in self._menu_items:
                if item[1] == view:
                    icon = item[2]
                    btn.configure(text=icon, anchor="center", font=ctk.CTkFont(size=18))
                    break

        self.header.grid_configure(padx=12)
        self.separator.grid_configure(padx=12)

    def _apply_expanded_state(self):
        """Aplica visual expandido: icones + texto, largura 240px."""
        self.configure(width=240)

        self.header.grid_configure(padx=20)
        self.separator.grid_configure(padx=20)

        self.lbl_title = ctk.CTkLabel(
            self.header,
            text="FinancePro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        )
        self.lbl_title.pack(side="left", padx=(8, 0))

        self.lbl_menu = ctk.CTkLabel(
            self,
            text="MENU PRINCIPAL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors.get("text_dim", "#a0a0b0"),
            anchor="w",
        )
        self.lbl_menu.grid(row=2, column=0, padx=24, pady=(0, 8), sticky="w")

        if hasattr(self, "lbl_version_collapsed"):
            self.lbl_version_collapsed.destroy()

        footer_inner = self.footer.winfo_children()
        for child in footer_inner:
            child.destroy()

        footer_row = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_row.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(
            footer_row,
            text="v2.0.0",
            font=ctk.CTkFont(size=11),
            text_color=self.colors.get("text_dim", "#a0a0b0"),
        )
        self.lbl_version.pack(side="left")

        self.btn_theme = ctk.CTkButton(
            footer_row,
            text="\u263E" if self.colors.get("bg_dark") == "#0f0f1a" else "\u2600",
            font=ctk.CTkFont(size=16),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=self.colors.get("bg_hover", "#16213e"),
            text_color=self.colors.get("text", "#fff"),
            command=self._on_theme_click,
        )
        self.btn_theme.pack(side="right")

        for view, btn in self.buttons.items():
            for item in self._menu_items:
                if item[1] == view:
                    label = item[0]
                    icon = item[2]
                    btn.configure(
                        text=f"  {icon}  {label}",
                        anchor="w",
                        font=ctk.CTkFont(size=14),
                    )
                    break

    def update_colors(self, colors):
        """Atualiza as cores de todos os elementos da sidebar."""
        self.colors = colors
        self.configure(fg_color=colors["bg_card"])

        self.lbl_logo.configure(text_color=colors.get("accent", "#00cec9"))
        self.lbl_title.configure(text_color=colors.get("text", "#fff"))
        self.separator.configure(fg_color=colors.get("border", "#2d2d44"))
        self.lbl_menu.configure(text_color=colors.get("text_dim", "#a0a0b0"))

        for name, btn in self.buttons.items():
            if name == self.active_view:
                btn.configure(
                    fg_color=colors["primary"],
                    text_color=colors["text"],
                    hover_color=colors.get("primary_hover", "#5a4bd1"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=colors.get("text_dim", "#a0a0b0"),
                    hover_color=colors.get("bg_hover", "#16213e"),
                )

        theme_icon = "\u263E" if colors.get("bg_dark") == "#0f0f1a" else "\u2600"
        self.btn_theme.configure(
            text=theme_icon,
            hover_color=colors.get("bg_hover", "#16213e"),
            text_color=colors.get("text", "#fff"),
        )
        self.lbl_version.configure(text_color=colors.get("text_dim", "#a0a0b0"))

    def navegar(self, view_name):
        """Navega para a view indicada e atualiza o estado ativo."""
        self._update_active(view_name)
        if self.on_navigate:
            self.on_navigate(view_name)

    def _update_active(self, view_name):
        """Atualiza a aparencia do botao ativo no menu."""
        self.active_view = view_name
        for name, btn in self.buttons.items():
            if name == view_name:
                btn.configure(
                    fg_color=self.colors["primary"],
                    text_color=self.colors["text"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors.get("text_dim", "#a0a0b0"),
                )
