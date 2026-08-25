import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None, colors=None):
        super().__init__(master, width=240, corner_radius=0, fg_color=colors["bg_card"])
        self.on_navigate = on_navigate
        self.colors = colors
        self.active_view = "dashboard"

        self.grid_propagate(False)
        self.grid_rowconfigure(11, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="ew")

        ctk.CTkLabel(header, text="$", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=colors["accent"], width=40, height=40).pack(side="left")
        ctk.CTkLabel(header, text="FinancePro", font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=colors["text"]).pack(side="left", padx=(8, 0))

        ctk.CTkFrame(self, fg_color=colors["border"], height=1).grid(row=1, column=0, padx=20, pady=(8, 16), sticky="ew")

        ctk.CTkLabel(self, text="MENU PRINCIPAL", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=colors["text_dim"], anchor="w").grid(row=2, column=0, padx=24, pady=(0, 8), sticky="w")

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

        self.buttons = {}
        for i, (label, view, icon) in enumerate(menu):
            btn = ctk.CTkButton(
                self, text=f"  {icon}  {label}", anchor="w",
                font=ctk.CTkFont(size=14), fg_color="transparent",
                text_color=colors["text_dim"], hover_color=colors["bg_hover"],
                height=40, corner_radius=8,
                command=lambda v=view: self.navegar(v))
            btn.grid(row=i + 3, column=0, padx=12, pady=2, sticky="ew")
            self.buttons[view] = btn

        self._update_active("dashboard")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=12, column=0, padx=20, pady=(16, 20), sticky="sew")
        ctk.CTkFrame(footer, fg_color=colors["border"], height=1).pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(footer, text="v2.0.0", font=ctk.CTkFont(size=11),
                      text_color=colors["text_dim"]).pack(anchor="w")

    def navegar(self, view_name):
        self._update_active(view_name)
        if self.on_navigate:
            self.on_navigate(view_name)

    def _update_active(self, view_name):
        self.active_view = view_name
        for name, btn in self.buttons.items():
            if name == view_name:
                btn.configure(fg_color=self.colors["primary"], text_color=self.colors["text"])
            else:
                btn.configure(fg_color="transparent", text_color=self.colors["text_dim"])
