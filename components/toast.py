import customtkinter as ctk


class Toast(ctk.CTkFrame):
    def __init__(self, master, mensagem, tipo="sucesso", duration=2500, **kwargs):
        super().__init__(
            master,
            fg_color="#00b894" if tipo == "sucesso" else "#d63031" if tipo == "erro" else "#fdcb6e",
            corner_radius=10,
            height=44,
            **kwargs,
        )
        self.grid_propagate(False)

        icone = "\u2714" if tipo == "sucesso" else "\u2718" if tipo == "erro" else "\u26A0"
        cor_texto = "#fff"

        ctk.CTkLabel(
            self,
            text=f"  {icone}  {mensagem}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cor_texto,
        ).pack(padx=16, pady=10, side="left", expand=True)

        self.after(duration, self._fechar)

    def _fechar(self):
        try:
            self.destroy()
        except Exception:
            pass


def mostrar_toast(master, mensagem, tipo="sucesso"):
    toast = Toast(master, mensagem, tipo)
    toast.place(relx=0.5, rely=0.02, anchor="n")
    toast.lift()
    return toast
