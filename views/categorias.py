import customtkinter as ctk
from database import get_connection
from components.modals import ConfirmarExclusaoModal


class CategoriasView(ctk.CTkFrame):
    def __init__(self, master, colors=None):
        super().__init__(master, fg_color="transparent")
        self.colors = colors or {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Categorias",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        ).pack(side="left")

    def _criar_formulario(self):
        form = ctk.CTkFrame(
            self,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        form.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=20)
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(grid, text="Nome", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=0, sticky="w")
        self.entry_nome = ctk.CTkEntry(grid, placeholder_text="Ex: Alimentacao",
                                        height=38, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Tipo", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=1, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(
            grid, values=["receita", "despesa"], height=38, corner_radius=8,
            fg_color=self.colors.get("bg_dark", "#0f0f1a"),
            border_color=self.colors.get("border", "#2d2d44"),
            button_color=self.colors.get("primary", "#6c5ce7"),
        )
        self.combo_tipo.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Cor", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=2, sticky="w")
        self.entry_cor = ctk.CTkEntry(grid, placeholder_text="#6c5ce7",
                                       height=38, corner_radius=8,
                                       fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                       border_color=self.colors.get("border", "#2d2d44"))
        self.entry_cor.insert(0, "#6c5ce7")
        self.entry_cor.grid(row=1, column=2, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            grid,
            text="+ Adicionar",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._adicionar,
        ).grid(row=1, column=3, sticky="ew")

    def _criar_lista(self):
        container = ctk.CTkFrame(
            self,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        container.grid(row=2, column=0, sticky="nsew")

        self.lista = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=self.colors.get("border", "#2d2d44"),
        )
        self.lista.pack(fill="both", expand=True, padx=4, pady=4)
        self.lista.grid_columnconfigure(0, weight=1)

        self._atualizar()

    def _adicionar(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get()
        cor = self.entry_cor.get().strip()

        if not nome:
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO categorias (nome, cor, tipo) VALUES (?, ?, ?)",
                (nome, cor, tipo),
            )
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

        self.entry_nome.delete(0, "end")
        self.entry_cor.delete(0, "end")
        self.entry_cor.insert(0, "#6c5ce7")

        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        conn = get_connection()
        rows = conn.execute(
            "SELECT id, nome, cor, tipo FROM categorias ORDER BY tipo, nome"
        ).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.lista,
                text="Nenhuma categoria cadastrada",
                text_color=self.colors.get("text_dim", "#a0a0a0"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=60)
            return

        header = ctk.CTkFrame(self.lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        for col, txt in enumerate(["", "Nome", "Tipo", ""]):
            ctk.CTkLabel(
                header, text=txt, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=col, sticky="w", padx=12)

        for i, c in enumerate(rows):
            row = ctk.CTkFrame(
                self.lista,
                fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                corner_radius=8,
                height=44,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            indicator = ctk.CTkFrame(row, fg_color=c["cor"], width=16, height=16, corner_radius=4)
            indicator.grid(row=0, column=0, padx=16, pady=14)

            ctk.CTkLabel(row, text=c["nome"], font=ctk.CTkFont(size=14)).grid(
                row=0, column=1, padx=8, pady=10, sticky="w")

            tipo_color = self.colors.get("green", "#00b894") if c["tipo"] == "receita" else self.colors.get("red", "#d63031")
            ctk.CTkLabel(row, text=c["tipo"].capitalize(), font=ctk.CTkFont(size=12),
                          text_color=tipo_color).grid(
                row=0, column=2, padx=8, pady=10, sticky="w")

            ctk.CTkButton(
                row, text="X", width=32, height=32,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors.get("red", "#d63031"),
                hover_color="#c0392b",
                command=lambda cid=c["id"]: self._excluir(cid),
            ).grid(row=0, column=3, padx=12, pady=6)

    def _excluir(self, cid):
        modal = ConfirmarExclusaoModal(
            self, "Excluir Categoria", "Deseja excluir esta categoria?",
            colors=self.colors,
        )
        self.wait_window(modal)
        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM categorias WHERE id = ?", (cid,))
            conn.commit()
            conn.close()
            self._atualizar()
