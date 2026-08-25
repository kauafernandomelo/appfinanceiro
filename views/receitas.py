import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_data_atual
from components.modals import ConfirmarExclusaoModal


class ReceitasView(ctk.CTkFrame):
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
            text="Receitas",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

    def criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(form, text="Descrição:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_descricao = ctk.CTkEntry(form, placeholder_text="Descrição")
        self.entry_descricao.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Valor:").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.entry_valor = ctk.CTkEntry(form, placeholder_text="0,00")
        self.entry_valor.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Data:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.entry_data = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD")
        self.entry_data.insert(0, obter_data_atual())
        self.entry_data.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Categoria:").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.combo_categoria = ctk.CTkComboBox(form, values=self.obter_categorias())
        self.combo_categoria.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            form,
            text="Adicionar",
            fg_color="#10b981",
            hover_color="#059669",
            command=self.adicionar,
        ).grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")

    def criar_lista(self):
        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.lista_frame.grid(row=2, column=0, sticky="nsew")
        self.lista_frame.grid_columnconfigure(0, weight=1)

        self.atualizar_lista()

    def obter_categorias(self) -> list:
        conn = get_connection()
        cats = conn.execute("SELECT nome FROM categorias WHERE tipo = 'receita'").fetchall()
        conn.close()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def adicionar(self):
        descricao = self.entry_descricao.get()
        valor = self.entry_valor.get().replace(",", ".")
        data = self.entry_data.get()
        categoria_nome = self.combo_categoria.get()

        if not descricao or not valor:
            return

        conn = get_connection()
        cat = conn.execute("SELECT id FROM categorias WHERE nome = ?", (categoria_nome,)).fetchone()
        cat_id = cat["id"] if cat else None

        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            (descricao, float(valor), data, cat_id),
        )
        conn.commit()
        conn.close()

        self.entry_descricao.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, obter_data_atual())

        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        receitas = conn.execute(
            """SELECT r.id, r.descricao, r.valor, r.data, c.nome as categoria
               FROM receitas r
               LEFT JOIN categorias c ON r.categoria_id = c.id
               ORDER BY r.data DESC"""
        ).fetchall()
        conn.close()

        if not receitas:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma receita cadastrada",
                text_color="#a0a0a0",
            ).grid(row=0, column=0, pady=20)
            return

        for i, r in enumerate(receitas):
            row = ctk.CTkFrame(self.lista_frame, fg_color="#16213e", corner_radius=8)
            row.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=r["data"],
                font=ctk.CTkFont(size=12),
                text_color="#a0a0a0",
            ).grid(row=0, column=0, padx=10, pady=10)

            ctk.CTkLabel(
                row,
                text=r["descricao"],
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

            ctk.CTkLabel(
                row,
                text=r["categoria"] or "Sem categoria",
                font=ctk.CTkFont(size=12),
                text_color="#a0a0a0",
            ).grid(row=0, column=2, padx=10, pady=10)

            ctk.CTkLabel(
                row,
                text=formatar_moeda(r["valor"]),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#10b981",
            ).grid(row=0, column=3, padx=10, pady=10)

            ctk.CTkButton(
                row,
                text="Excluir",
                width=60,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda rid=r["id"]: self.excluir(rid),
            ).grid(row=0, column=4, padx=10, pady=10)

    def excluir(self, receita_id: int):
        modal = ConfirmarExclusaoModal(
            self,
            "Excluir Receita",
            "Tem certeza que deseja excluir esta receita?",
        )
        self.wait_window(modal)

        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM receitas WHERE id = ?", (receita_id,))
            conn.commit()
            conn.close()
            self.atualizar_lista()
