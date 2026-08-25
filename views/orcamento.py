import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual


class OrcamentoView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_header()
        self.criar_formulario()
        self.criar_lista()

    def criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Orçamento Mensal",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

    def criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(form, text="Categoria:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_categoria = ctk.CTkComboBox(form, values=self.obter_categorias())
        self.combo_categoria.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Limite:").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.entry_limite = ctk.CTkEntry(form, placeholder_text="0,00")
        self.entry_limite.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            form,
            text="Definir Limite",
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=self.adicionar,
        ).grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

    def criar_lista(self):
        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.lista_frame.grid(row=2, column=0, sticky="nsew")
        self.lista_frame.grid_columnconfigure(0, weight=1)

        self.atualizar_lista()

    def obter_categorias(self) -> list:
        conn = get_connection()
        cats = conn.execute("SELECT nome FROM categorias WHERE tipo = 'despesa'").fetchall()
        conn.close()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def adicionar(self):
        categoria_nome = self.combo_categoria.get()
        limite = self.entry_limite.get().replace(",", ".")

        if not limite:
            return

        conn = get_connection()
        cat = conn.execute("SELECT id FROM categorias WHERE nome = ?", (categoria_nome,)).fetchone()
        if not cat:
            conn.close()
            return

        mes = obter_mes_atual()

        existing = conn.execute(
            "SELECT id FROM orcamento WHERE categoria_id = ? AND mes = ?",
            (cat["id"], mes),
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE orcamento SET limite = ? WHERE id = ?",
                (float(limite), existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO orcamento (categoria_id, limite, mes) VALUES (?, ?, ?)",
                (cat["id"], float(limite), mes),
            )

        conn.commit()
        conn.close()

        self.entry_limite.delete(0, "end")
        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        mes = obter_mes_atual()

        orcamentos = conn.execute(
            """SELECT o.id, c.nome as categoria, o.limite,
                      COALESCE(SUM(d.valor), 0) as gasto
               FROM orcamento o
               LEFT JOIN categorias c ON o.categoria_id = c.id
               LEFT JOIN despesas d ON d.categoria_id = c.id AND strftime('%Y-%m', d.data) = o.mes
               WHERE o.mes = ?
               GROUP BY o.id""",
            (mes,),
        ).fetchall()
        conn.close()

        if not orcamentos:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhum orçamento definido para este mês",
                text_color="#a0a0a0",
            ).grid(row=0, column=0, pady=20)
            return

        for i, o in enumerate(orcamentos):
            row = ctk.CTkFrame(self.lista_frame, fg_color="#16213e", corner_radius=8)
            row.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=o["categoria"] or "Sem categoria",
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

            percentual = (o["gasto"] / o["limite"] * 100) if o["limite"] > 0 else 0
            cor_barra = "#10b981" if percentual <= 80 else "#f59e0b" if percentual <= 100 else "#ef4444"

            progress_frame = ctk.CTkFrame(row, fg_color="transparent")
            progress_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
            progress_frame.grid_columnconfigure(0, weight=1)

            progress = ctk.CTkProgressBar(progress_frame, progress_color=cor_barra)
            progress.grid(row=0, column=0, sticky="ew")
            progress.set(min(percentual / 100, 1.0))

            ctk.CTkLabel(
                row,
                text=f"{formatar_moeda(o['gasto'])} / {formatar_moeda(o['limite'])}",
                font=ctk.CTkFont(size=12),
                text_color="#a0a0a0",
            ).grid(row=0, column=2, padx=10, pady=10)

            ctk.CTkButton(
                row,
                text="Excluir",
                width=60,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda oid=o["id"]: self.excluir(oid),
            ).grid(row=0, column=3, padx=10, pady=10)

    def excluir(self, orcamento_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM orcamento WHERE id = ?", (orcamento_id,))
        conn.commit()
        conn.close()
        self.atualizar_lista()
