import customtkinter as ctk
from database import get_connection
from components.modals import ConfirmarExclusaoModal


class CategoriasView(ctk.CTkFrame):
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
            text="Categorias",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

    def criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(form, text="Nome:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_nome = ctk.CTkEntry(form, placeholder_text="Nome da categoria")
        self.entry_nome.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Tipo:").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(form, values=["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Cor:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.entry_cor = ctk.CTkEntry(form, placeholder_text="#3B82F6")
        self.entry_cor.insert(0, "#3B82F6")
        self.entry_cor.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            form,
            text="Adicionar",
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.adicionar,
        ).grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")

    def criar_lista(self):
        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.lista_frame.grid(row=2, column=0, sticky="nsew")
        self.lista_frame.grid_columnconfigure(0, weight=1)

        self.atualizar_lista()

    def adicionar(self):
        nome = self.entry_nome.get()
        tipo = self.combo_tipo.get()
        cor = self.entry_cor.get()

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
        self.entry_cor.insert(0, "#3B82F6")

        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        categorias = conn.execute(
            "SELECT id, nome, cor, tipo FROM categorias ORDER BY tipo, nome"
        ).fetchall()
        conn.close()

        if not categorias:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma categoria cadastrada",
                text_color="#a0a0a0",
            ).grid(row=0, column=0, pady=20)
            return

        for i, c in enumerate(categorias):
            row = ctk.CTkFrame(self.lista_frame, fg_color="#16213e", corner_radius=8)
            row.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            cor_indicator = ctk.CTkFrame(row, fg_color=c["cor"], width=20, height=20, corner_radius=4)
            cor_indicator.grid(row=0, column=0, padx=10, pady=10)

            ctk.CTkLabel(
                row,
                text=c["nome"],
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

            tipo_color = "#10b981" if c["tipo"] == "receita" else "#ef4444"
            ctk.CTkLabel(
                row,
                text=c["tipo"].capitalize(),
                font=ctk.CTkFont(size=12),
                text_color=tipo_color,
            ).grid(row=0, column=2, padx=10, pady=10)

            ctk.CTkButton(
                row,
                text="Excluir",
                width=60,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda cid=c["id"]: self.excluir(cid),
            ).grid(row=0, column=3, padx=10, pady=10)

    def excluir(self, categoria_id: int):
        modal = ConfirmarExclusaoModal(
            self,
            "Excluir Categoria",
            "Tem certeza que deseja excluir esta categoria?",
        )
        self.wait_window(modal)

        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
            conn.commit()
            conn.close()
            self.atualizar_lista()
