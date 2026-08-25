import customtkinter as ctk


class Tooltip(ctk.CTkToplevel):
    def __init__(self, widget, text, **kwargs):
        super().__init__(widget, **kwargs)
        self.widget = widget
        self.text = text

        self.overrideredirect(True)
        self.configure(fg_color="#2d2d44")

        label = ctk.CTkLabel(
            self, text=text, font=ctk.CTkFont(size=11),
            text_color="#ffffff", padx=8, pady=4,
        )
        label.pack()

        self.withdraw()
        self._visible = False

        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, event=None):
        if self._visible:
            return
        try:
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            self.geometry(f"+{x}+{y}")
            self.deiconify()
            self._visible = True
        except Exception:
            pass

    def _hide(self, event=None):
        if not self._visible:
            return
        self.withdraw()
        self._visible = False
