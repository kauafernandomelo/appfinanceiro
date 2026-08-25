import customtkinter as ctk


class Modal(ctk.CTkToplevel):
    def __init__(self, master, titulo="", largura=400, altura=300, colors=None):
        super().__init__(master)
        self.colors = colors or {}
        self.title(titulo)
        self.geometry(f"{largura}x{altura}")
        self.configure(fg_color=self.colors.get("bg_dark", "#0f0f1a"))
        self.resizable(False, False)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.resultado = None

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=24)

    def _fechar(self):
        self.resultado = None
        self.destroy()

    def confirmar(self, resultado=None):
        self.resultado = resultado
        self.destroy()


class ConfirmarExclusaoModal(Modal):
    def __init__(self, master, titulo="Confirmar Exclusao", mensagem="", colors=None):
        super().__init__(master, titulo, 380, 200, colors)

        ctk.CTkLabel(
            self.main_frame,
            text=mensagem,
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("text", "#fff"),
            wraplength=320,
        ).pack(pady=(0, 24))

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            fg_color=self.colors.get("border", "#2d2d44"),
            hover_color="#3d3d54",
            text_color=self.colors.get("text", "#fff"),
            command=self._fechar,
        ).pack(side="left", expand=True, padx=(0, 6), fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Excluir",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("red", "#d63031"),
            hover_color="#c0392b",
            command=lambda: self.confirmar(True),
        ).pack(side="right", expand=True, padx=(6, 0), fill="x")
