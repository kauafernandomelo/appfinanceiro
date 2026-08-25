import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_data_atual
from components.modals import ConfirmarExclusaoModal


class ReceitasView(ctk.CTkFrame):
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
            text="Receitas",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        ).pack(side="left")

        total = self._obter_total()
        ctk.CTkLabel(
            header,
            text=f"Total: {formatar_moeda(total)}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors.get("green", "#00b894"),
        ).pack(side="right")

    def _criar_formulario(self):
        form = ctk.CTkFrame(
            self,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        form.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=20)
        grid.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(grid, text="Descricao", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self.entry_desc = ctk.CTkEntry(grid, placeholder_text="Ex: Salario",
                                        height=38, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Valor (R$)", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=1, sticky="w", padx=(0, 8))
        self.entry_valor = ctk.CTkEntry(grid, placeholder_text="0,00",
                                         height=38, corner_radius=8,
                                         fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                         border_color=self.colors.get("border", "#2d2d44"))
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Data", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=2, sticky="w", padx=(0, 8))
        self.entry_data = ctk.CTkEntry(grid, placeholder_text="AAAA-MM-DD",
                                        height=38, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_data.insert(0, obter_data_atual())
        self.entry_data.grid(row=1, column=2, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Categoria", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=3, sticky="w", padx=(0, 8))
        cats = self._obter_categorias()
        self.combo_cat = ctk.CTkComboBox(
            grid, values=cats, height=38, corner_radius=8,
            fg_color=self.colors.get("bg_dark", "#0f0f1a"),
            border_color=self.colors.get("border", "#2d2d44"),
            button_color=self.colors.get("primary", "#6c5ce7"),
            button_hover_color=self.colors.get("primary_hover", "#5a4bd1"),
        )
        self.combo_cat.grid(row=1, column=3, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            grid,
            text="+ Adicionar",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("green", "#00b894"),
            hover_color="#00a884",
            command=self._adicionar,
        ).grid(row=1, column=4, sticky="ew")

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

    def _obter_categorias(self):
        conn = get_connection()
        cats = conn.execute("SELECT nome FROM categorias WHERE tipo = 'receita'").fetchall()
        conn.close()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def _obter_total(self):
        conn = get_connection()
        mes = obter_data_atual()[:7]
        total = conn.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM receitas WHERE strftime('%Y-%m', data) = ?",
            (mes,),
        ).fetchone()[0]
        conn.close()
        return total

    def _adicionar(self):
        desc = self.entry_desc.get().strip()
        valor = self.entry_valor.get().replace(",", ".").strip()
        data = self.entry_data.get().strip()
        cat_nome = self.combo_cat.get()

        if not desc or not valor:
            return

        conn = get_connection()
        cat = conn.execute("SELECT id FROM categorias WHERE nome = ?", (cat_nome,)).fetchone()
        cat_id = cat["id"] if cat else None

        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            (desc, float(valor), data, cat_id),
        )
        conn.commit()
        conn.close()

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, obter_data_atual())

        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        conn = get_connection()
        rows = conn.execute(
            """SELECT r.id, r.descricao, r.valor, r.data,
                      COALESCE(c.nome, 'Sem categoria') as categoria
               FROM receitas r
               LEFT JOIN categorias c ON r.categoria_id = c.id
               ORDER BY r.data DESC"""
        ).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.lista,
                text="Nenhuma receita cadastrada",
                text_color=self.colors.get("text_dim", "#a0a0a0"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=60)
            return

        header = ctk.CTkFrame(self.lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, txt in enumerate(["Data", "Descricao", "Categoria", "Valor"]):
            ctk.CTkLabel(
                header, text=txt, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=col, sticky="w", padx=12)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(
                self.lista,
                fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                corner_radius=8,
                height=44,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=r["data"], font=ctk.CTkFont(size=13),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
                row=0, column=0, padx=12, pady=10, sticky="w")

            ctk.CTkLabel(row, text=r["descricao"], font=ctk.CTkFont(size=13)).grid(
                row=0, column=1, padx=12, pady=10, sticky="w")

            ctk.CTkLabel(row, text=r["categoria"], font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
                row=0, column=2, padx=12, pady=10, sticky="w")

            ctk.CTkLabel(row, text=formatar_moeda(r["valor"]),
                          font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=self.colors.get("green", "#00b894")).grid(
                row=0, column=3, padx=12, pady=10, sticky="w")

            ctk.CTkButton(
                row, text="X", width=32, height=32,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors.get("red", "#d63031"),
                hover_color="#c0392b",
                command=lambda rid=r["id"]: self._excluir(rid),
            ).grid(row=0, column=4, padx=12, pady=6)

    def _excluir(self, rid):
        modal = ConfirmarExclusaoModal(
            self, "Excluir Receita", "Deseja excluir esta receita?",
            colors=self.colors,
        )
        self.wait_window(modal)
        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM receitas WHERE id = ?", (rid,))
            conn.commit()
            conn.close()
            self._atualizar()
