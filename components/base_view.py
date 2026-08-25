import customtkinter as ctk
from components.toast import mostrar_toast
from components.modals import ConfirmarExclusaoModal


class BaseView(ctk.CTkFrame):
    def __init__(self, master, colors=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.colors = colors or {}
        self.grid_columnconfigure(0, weight=1)

    def _criar_entry(self, parent, placeholder="", **kwargs):
        return ctk.CTkEntry(
            parent, placeholder_text=placeholder, height=36, corner_radius=8,
            fg_color=self.colors.get("bg_dark", "#0f0f1a"),
            border_color=self.colors.get("border", "#2d2d44"), **kwargs,
        )

    def _criar_combo(self, parent, values, **kwargs):
        return ctk.CTkComboBox(
            parent, values=values, height=36, corner_radius=8,
            fg_color=self.colors.get("bg_dark", "#0f0f1a"),
            border_color=self.colors.get("border", "#2d2d44"),
            button_color=self.colors.get("primary", "#6c5ce7"), **kwargs,
        )

    def _criar_label(self, parent, text, **kwargs):
        defaults = {
            "font": ctk.CTkFont(size=11),
            "text_color": self.colors.get("text_dim", "#a0a0a0"),
        }
        defaults.update(kwargs)
        return ctk.CTkLabel(parent, text=text, **defaults)

    def _criar_titulo(self, parent, text):
        return ctk.CTkLabel(
            parent, text=text, font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        )

    def _criar_card_frame(self, parent):
        return ctk.CTkFrame(parent, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)

    def _criar_lista_frame(self, parent):
        container = self._criar_card_frame(parent)
        lista = ctk.CTkScrollableFrame(
            container, fg_color="transparent",
            scrollbar_button_color=self.colors.get("border", "#2d2d44"),
        )
        lista.pack(fill="both", expand=True, padx=4, pady=4)
        lista.grid_columnconfigure(0, weight=1)
        return container, lista

    def _confirmar_exclusao(self, titulo, mensagem):
        modal = ConfirmarExclusaoModal(self, titulo, mensagem, colors=self.colors)
        self.wait_window(modal)
        return modal.resultado

    def _validar_campos(self, campos: dict) -> bool:
        for nome, valor in campos.items():
            if not valor or not valor.strip():
                mostrar_toast(self, f"Preencha o campo: {nome}", "erro")
                return False
        return True

    def _validar_valor(self, valor: str) -> float | None:
        try:
            return float(valor.replace(",", "."))
        except (ValueError, AttributeError):
            mostrar_toast(self, "Valor invalido! Use apenas numeros.", "erro")
            return None
