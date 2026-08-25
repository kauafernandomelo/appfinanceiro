import customtkinter as ctk


class Modal(ctk.CTkToplevel):
    def __init__(self, master, titulo: str = "", largura: int = 400, altura: int = 300):
        super().__init__(master)
        self.title(titulo)
        self.geometry(f"{largura}x{altura}")
        self.resizable(False, False)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self.resultado = None

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def fechar(self):
        self.resultado = None
        self.destroy()

    def confirmar(self, resultado=None):
        self.resultado = resultado
        self.destroy()


class ConfirmarExclusaoModal(Modal):
    def __init__(self, master, titulo: str = "Confirmar Exclusão", mensagem: str = ""):
        super().__init__(master, titulo, 350, 180)

        ctk.CTkLabel(
            self.main_frame,
            text=mensagem,
            font=ctk.CTkFont(size=14),
            wraplength=300,
        ).pack(pady=(0, 20))

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            fg_color="#404040",
            hover_color="#505050",
            command=self.fechar,
        ).pack(side="left", expand=True, padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Excluir",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: self.confirmar(True),
        ).pack(side="right", expand=True, padx=5)
