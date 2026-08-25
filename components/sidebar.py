import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, width=200, corner_radius=0, fg_color="#1a1a2e")
        self.on_navigate = on_navigate

        self.grid_propagate(False)

        self.logo_label = ctk.CTkLabel(
            self,
            text="💰 Financeiro",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e94560",
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        menu_items = [
            ("📊 Dashboard", "dashboard"),
            ("💵 Receitas", "receitas"),
            ("💸 Despesas", "despesas"),
            ("🏷️ Categorias", "categorias"),
            ("📋 Orçamento", "orcamento"),
            ("🎯 Metas", "metas"),
            ("🔄 Recorrentes", "recorrentes"),
            ("📈 Relatórios", "relatorios"),
        ]

        self.buttons = []
        for i, (label, view_name) in enumerate(menu_items):
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color="#a0a0a0",
                hover_color="#16213e",
                height=40,
                command=lambda v=view_name: self.navegar(v),
            )
            btn.grid(row=i + 1, column=0, padx=10, pady=5, sticky="ew")
            self.buttons.append((btn, view_name))

        self.grid_columnconfigure(0, weight=1)

    def navegar(self, view_name: str):
        for btn, name in self.buttons:
            if name == view_name:
                btn.configure(fg_color="#16213e", text_color="#e94560")
            else:
                btn.configure(fg_color="transparent", text_color="#a0a0a0")

        if self.on_navigate:
            self.on_navigate(view_name)
