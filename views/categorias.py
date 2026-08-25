import customtkinter as ctk
from database import get_connection
from components.toast import mostrar_toast
from components.base_view import BaseView
from components.modals import ConfirmarExclusaoModal


class CategoriasView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._edit_id = None
        self._criar_header()
        self._criar_filtro()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._criar_titulo(header, "Categorias").pack(side="left")
        self.lbl_count = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=14),
                                       text_color=self.colors.get("text_dim", "#a0a0a0"))
        self.lbl_count.pack(side="right")

    def _criar_filtro(self):
        filtro = ctk.CTkFrame(self, fg_color="transparent")
        filtro.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.filtro_var = ctk.StringVar(value="Todas")
        for txt in ["Todas", "Receita", "Despesa"]:
            ctk.CTkRadioButton(
                filtro, text=txt, variable=self.filtro_var, value=txt,
                font=ctk.CTkFont(size=12),
                fg_color=self.colors.get("primary", "#6c5ce7"),
                hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                command=self._atualizar,
            ).pack(side="left", padx=(0, 16))

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=14)
        g.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._criar_label(g, "Nome*").grid(row=0, column=0, sticky="w")
        self.entry_nome = self._criar_entry(g, "Ex: Alimentacao")
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Tipo").grid(row=0, column=1, sticky="w")
        self.combo_tipo = self._criar_combo(g, ["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Cor (hex)").grid(row=0, column=2, sticky="w")
        self.entry_cor = self._criar_entry(g, "#6c5ce7")
        self.entry_cor.insert(0, "#6c5ce7")
        self.entry_cor.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        self.btn_add = ctk.CTkButton(
            g, text="+ Adicionar", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._salvar,
        )
        self.btn_add.grid(row=1, column=3, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._atualizar()

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get()
        cor = self.entry_cor.get().strip()

        if not self._validar_campos({"Nome": nome}):
            return

        with get_connection() as conn:
            if self._edit_id:
                try:
                    conn.execute("UPDATE categorias SET nome=?,cor=?,tipo=? WHERE id=?",
                                 (nome, cor, tipo, self._edit_id))
                    conn.commit()
                    mostrar_toast(self, f"Categoria '{nome}' atualizada!")
                except Exception:
                    mostrar_toast(self, "Nome ja existe!", "erro")
                self._edit_id = None
                self.btn_add.configure(text="+ Adicionar")
            else:
                try:
                    conn.execute("INSERT INTO categorias (nome,cor,tipo) VALUES (?,?,?)", (nome, cor, tipo))
                    conn.commit()
                    mostrar_toast(self, f"Categoria '{nome}' criada!")
                except Exception:
                    mostrar_toast(self, "Categoria ja existe!", "erro")

        self.entry_nome.delete(0, "end")
        self.entry_cor.delete(0, "end")
        self.entry_cor.insert(0, "#6c5ce7")
        self._atualizar()

    def _editar(self, cid):
        with get_connection() as conn:
            c = conn.execute("SELECT * FROM categorias WHERE id=?", (cid,)).fetchone()
        if not c:
            return
        self._edit_id = cid
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, c["nome"])
        self.combo_tipo.set(c["tipo"])
        self.entry_cor.delete(0, "end")
        self.entry_cor.insert(0, c["cor"])
        self.btn_add.configure(text="Salvar Edicao", fg_color=self.colors.get("accent", "#00cec9"))

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        filtro = self.filtro_var.get()
        query = "SELECT id, nome, cor, tipo FROM categorias"
        params = ()
        if filtro == "Receita":
            query += " WHERE tipo='receita'"
        elif filtro == "Despesa":
            query += " WHERE tipo='despesa'"
        query += " ORDER BY tipo, nome"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        total = len(rows)
        self.lbl_count.configure(text=f"{total} categorias")

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma categoria encontrada",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=50)
            return

        for i, c in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=40)
            row.grid(row=i, column=0, sticky="ew", pady=2)

            ctk.CTkFrame(row, fg_color=c["cor"], width=14, height=14, corner_radius=4).grid(row=0, column=0, padx=14, pady=13)
            ctk.CTkLabel(row, text=c["nome"], font=ctk.CTkFont(size=14)).grid(row=0, column=1, padx=8, pady=8, sticky="w")

            tc = self.colors.get("green", "#00b894") if c["tipo"] == "receita" else self.colors.get("red", "#d63031")
            badge = ctk.CTkFrame(row, fg_color=tc, corner_radius=10)
            badge.grid(row=0, column=2, padx=8, pady=8)
            ctk.CTkLabel(badge, text=c["tipo"].capitalize(), font=ctk.CTkFont(size=10, weight="bold"),
                          text_color="#fff").pack(padx=10, pady=2)

            ctk.CTkButton(row, text="E", width=26, height=26, corner_radius=6,
                           font=ctk.CTkFont(size=10, weight="bold"),
                           fg_color=self.colors.get("accent", "#00cec9"), hover_color="#00a3a3",
                           command=lambda cid=c["id"]: self._editar(cid)).grid(row=0, column=3, padx=(6, 3), pady=6)
            ctk.CTkButton(row, text="X", width=26, height=26, corner_radius=6,
                           font=ctk.CTkFont(size=10, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda cid=c["id"]: self._excluir(cid)).grid(row=0, column=4, padx=(3, 10), pady=6)

    def _excluir(self, cid):
        if self._confirmar_exclusao("Excluir Categoria", "Deseja excluir esta categoria?"):
            with get_connection() as conn:
                conn.execute("DELETE FROM categorias WHERE id=?", (cid,))
                conn.commit()
            mostrar_toast(self, "Categoria excluida!", "sucesso")
            self._atualizar()
