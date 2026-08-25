import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None, colors=None):
        super().__init__(master, width=240, corner_radius=0, fg_color=colors["bg_card"])
        self.on_navigate = on_navigate
        self.colors = colors
        self.active_view = "dashboard"

        self.grid_propagate(False)
        self.grid_rowconfigure(10, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="ew")

        logo_icon = ctk.CTkLabel(
            header,
            text="$",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=colors["accent"],
            width=40,
            height=40,
        )
        logo_icon.pack(side="left")

        logo_text = ctk.CTkLabel(
            header,
            text="FinancePro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=colors["text"],
        )
        logo_text.pack(side="left", padx=(8, 0))

        ctk.CTkFrame(
            self,
            fg_color=colors["border"],
            height=1,
        ).grid(row=1, column=0, padx=20, pady=(8, 16), sticky="ew")

        menu_label = ctk.CTkLabel(
            self,
            text="MENU PRINCIPAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=colors["text_dim"],
            anchor="w",
        )
        menu_label.grid(row=2, column=0, padx=24, pady=(0, 8), sticky="w")

        menu_items = [
            ("Dashboard", "dashboard", "\U0001F4CA"),
            ("Receitas", "receitas", "\U0001F4B5"),
            ("Despesas", "despesas", "\U0001F4B8"),
            ("Categorias", "categorias", "\U0001F3F7\uFE0F"),
            ("Orcamento", "orcamento", "\U0001F4CB"),
            ("Metas", "metas", "\U0001F3AF"),
            ("Recorrentes", "recorrentes", "\U0001F504"),
            ("Relatorios", "relatorios", "\U0001F4C8"),
        ]

        self.buttons = {}
        for i, (label, view_name, icon) in enumerate(menu_items):
            btn = self._create_menu_button(label, view_name, icon)
            btn.grid(row=i + 3, column=0, padx=12, pady=2, sticky="ew")
            self.buttons[view_name] = btn

        self._update_active("dashboard")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=11, column=0, padx=20, pady=(16, 20), sticky="sew")

        ctk.CTkFrame(footer, fg_color=colors["border"], height=1).pack(
            fill="x", pady=(0, 12)
        )

        ctk.CTkLabel(
            footer,
            text="v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_dim"],
        ).pack(anchor="w")

    def _create_menu_button(self, label, view_name, icon):
        btn = ctk.CTkButton(
            self,
            text=f"  {icon}  {label}",
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.colors["text_dim"],
            hover_color=self.colors["bg_hover"],
            height=42,
            corner_radius=8,
            command=lambda v=view_name: self.navegar(v),
        )
        return btn

    def navegar(self, view_name):
        self._update_active(view_name)
        if self.on_navigate:
            self.on_navigate(view_name)

    def _update_active(self, view_name):
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
                    text_color=self.colors["text_dim"],
                )
