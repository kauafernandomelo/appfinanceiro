import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual


class OrcamentoView(ctk.CTkFrame):
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
            text="Orcamento Mensal",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=obter_mes_atual(),
            font=ctk.CTkFont(size=14),
            text_color=self.colors.get("text_dim", "#a0a0a0"),
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
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(grid, text="Categoria", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=0, sticky="w")
        cats = self._obter_categorias()
        self.combo_cat = ctk.CTkComboBox(
            grid, values=cats, height=38, corner_radius=8,
            fg_color=self.colors.get("bg_dark", "#0f0f1a"),
            border_color=self.colors.get("border", "#2d2d44"),
            button_color=self.colors.get("primary", "#6c5ce7"),
        )
        self.combo_cat.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Limite (R$)", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=1, sticky="w")
        self.entry_limite = ctk.CTkEntry(grid, placeholder_text="0,00",
                                          height=38, corner_radius=8,
                                          fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                          border_color=self.colors.get("border", "#2d2d44"))
        self.entry_limite.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            grid,
            text="Definir Limite",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("yellow", "#fdcb6e"),
            hover_color="#e0b341",
            text_color="#000",
            command=self._adicionar,
        ).grid(row=1, column=2, sticky="ew")

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
        cats = conn.execute("SELECT nome FROM categorias WHERE tipo = 'despesa'").fetchall()
        conn.close()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def _adicionar(self):
        cat_nome = self.combo_cat.get()
        limite = self.entry_limite.get().replace(",", ".").strip()

        if not limite:
            return

        conn = get_connection()
        cat = conn.execute("SELECT id FROM categorias WHERE nome = ?", (cat_nome,)).fetchone()
        if not cat:
            conn.close()
            return

        mes = obter_mes_atual()
        existing = conn.execute(
            "SELECT id FROM orcamento WHERE categoria_id = ? AND mes = ?",
            (cat["id"], mes),
        ).fetchone()

        if existing:
            conn.execute("UPDATE orcamento SET limite = ? WHERE id = ?",
                         (float(limite), existing["id"]))
        else:
            conn.execute(
                "INSERT INTO orcamento (categoria_id, limite, mes) VALUES (?, ?, ?)",
                (cat["id"], float(limite), mes),
            )

        conn.commit()
        conn.close()
        self.entry_limite.delete(0, "end")
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        conn = get_connection()
        mes = obter_mes_atual()

        rows = conn.execute(
            """SELECT o.id, COALESCE(c.nome, 'Sem categoria') as categoria, o.limite,
                      COALESCE(SUM(d.valor), 0) as gasto
               FROM orcamento o
               LEFT JOIN categorias c ON o.categoria_id = c.id
               LEFT JOIN despesas d ON d.categoria_id = c.id AND strftime('%Y-%m', d.data) = o.mes
               WHERE o.mes = ?
               GROUP BY o.id""",
            (mes,),
        ).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.lista,
                text="Nenhum orcamento definido para este mes",
                text_color=self.colors.get("text_dim", "#a0a0a0"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=60)
            return

        for i, o in enumerate(rows):
            row = ctk.CTkFrame(
                self.lista,
                fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                corner_radius=8,
                height=60,
            )
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=o["categoria"], font=ctk.CTkFont(size=14)).grid(
                row=0, column=0, padx=16, pady=12, sticky="w")

            pct = (o["gasto"] / o["limite"] * 100) if o["limite"] > 0 else 0
            bar_color = self.colors.get("green", "#00b894") if pct <= 80 else self.colors.get("yellow", "#fdcb6e") if pct <= 100 else self.colors.get("red", "#d63031")

            bar_frame = ctk.CTkFrame(row, fg_color="transparent")
            bar_frame.grid(row=0, column=1, padx=12, pady=12, sticky="ew")
            bar_frame.grid_columnconfigure(0, weight=1)

            bar = ctk.CTkProgressBar(bar_frame, progress_color=bar_color, height=8, corner_radius=4)
            bar.grid(row=0, column=0, sticky="ew")
            bar.set(min(pct / 100, 1.0))

            ctk.CTkLabel(
                bar_frame,
                text=f"{formatar_moeda(o['gasto'])} / {formatar_moeda(o['limite'])}  ({pct:.0f}%)",
                font=ctk.CTkFont(size=11),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=1, column=0, sticky="w", pady=(4, 0))

            ctk.CTkButton(
                row, text="X", width=32, height=32,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors.get("red", "#d63031"),
                hover_color="#c0392b",
                command=lambda oid=o["id"]: self._excluir(oid),
            ).grid(row=0, column=2, padx=12, pady=12)

    def _excluir(self, oid):
        conn = get_connection()
        conn.execute("DELETE FROM orcamento WHERE id = ?", (oid,))
        conn.commit()
        conn.close()
        self._atualizar()
