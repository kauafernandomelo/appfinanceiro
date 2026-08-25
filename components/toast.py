import customtkinter as ctk

toasts_ativos = []


class Toast(ctk.CTkFrame):
    def __init__(self, master, mensagem, tipo="sucesso", duration=2500, **kwargs):
        super().__init__(
            master,
            fg_color="#00b894" if tipo == "sucesso" else "#d63031" if tipo == "erro" else "#fdcb6e",
            corner_radius=10, height=44, **kwargs,
        )
        self.grid_propagate(False)

        icone = "\u2714" if tipo == "sucesso" else "\u2718" if tipo == "erro" else "\u26A0"
        ctk.CTkLabel(
            self, text=f"  {icone}  {mensagem}",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#fff",
        ).pack(padx=16, pady=10, side="left", expand=True)

        self.after(duration, self._fechar)

    def _fechar(self):
        try:
            if self in toasts_ativos:
                toasts_ativos.remove(self)
            self._reposition_all()
            self.destroy()
        except Exception:
            pass

    def _reposition_all(self):
        try:
            for i, t in enumerate(toasts_ativos):
                if t.winfo_exists():
                    t.place(relx=0.5, rely=0.02 + i * 0.04, anchor="n")
                    t.lift()
        except Exception:
            pass


def mostrar_toast(master, mensagem, tipo="sucesso"):
    while len(toasts_ativos) >= 4:
        old = toasts_ativos.pop(0)
        try:
            old.destroy()
        except Exception:
            pass

    toast = Toast(master, mensagem, tipo)
    idx = len(toasts_ativos)
    toasts_ativos.append(toast)
    toast.place(relx=0.5, rely=0.02 + idx * 0.04, anchor="n")
    toast.lift()
    return toast
