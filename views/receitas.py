import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_data_atual, validar_data
from components.toast import mostrar_toast
from components.base_view import BaseView
from components.datepicker import DatePicker


class ReceitasView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._edit_id = None
        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Receitas").pack(side="left")
        self.lbl_total = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=15, weight="bold"),
                                       text_color=self.colors.get("green", "#00b894"))
        self.lbl_total.pack(side="right")
        self._atualizar_total()

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=16)
        g.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._criar_label(g, "Descricao*").grid(row=0, column=0, sticky="w")
        self.entry_desc = self._criar_entry(g, "Ex: Salario, Freelance...")
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Valor (R$)*").grid(row=0, column=1, sticky="w")
        self.entry_valor = self._criar_entry(g, "0,00")
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Data*").grid(row=0, column=2, sticky="w")
        self.dp_data = DatePicker(g)
        self.dp_data.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Categoria").grid(row=0, column=3, sticky="w")
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=3, sticky="ew", padx=(0, 6))

        self.btn_add = ctk.CTkButton(
            g, text="+ Adicionar", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("green", "#00b894"), hover_color="#00a884",
            command=self._salvar,
        )
        self.btn_add.grid(row=1, column=4, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=2, column=0, sticky="nsew")
        self._atualizar()

    def _cats(self):
        with get_connection() as conn:
            cats = conn.execute("SELECT nome FROM categorias WHERE tipo='receita' ORDER BY nome").fetchall()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def _atualizar_total(self):
        with get_connection() as conn:
            t = conn.execute("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE strftime('%Y-%m',data)=?",
                             (obter_data_atual()[:7],)).fetchone()[0]
        self.lbl_total.configure(text=f"Total: {formatar_moeda(t)}")

    def _salvar(self):
        desc = self.entry_desc.get().strip()
        val_str = self.entry_valor.get().replace(",", ".").strip()
        data = self.dp_data.get()

        if not self._validar_campos({"Descricao": desc, "Valor": val_str, "Data": data}):
            return
        if not validar_data(data):
            mostrar_toast(self, "Data invalida! Use AAAA-MM-DD", "erro")
            return
        val = self._validar_valor(val_str)
        if val is None:
            return

        cat = self.combo_cat.get()
        with get_connection() as conn:
            c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
            cid = c["id"] if c else None
            if self._edit_id:
                conn.execute("UPDATE receitas SET descricao=?,valor=?,data=?,categoria_id=? WHERE id=?",
                             (desc, val, data, cid, self._edit_id))
                mostrar_toast(self, f"Receita '{desc}' atualizada!")
                self._edit_id = None
                self.btn_add.configure(text="+ Adicionar", fg_color=self.colors.get("green", "#00b894"))
            else:
                conn.execute("INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                             (desc, val, data, cid))
                mostrar_toast(self, f"Receita '{desc}' adicionada!")

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.dp_data.set(obter_data_atual())
        self._atualizar()
        self._atualizar_total()

    def _editar(self, rid):
        with get_connection() as conn:
            r = conn.execute("SELECT * FROM receitas WHERE id=?", (rid,)).fetchone()
        if not r:
            return
        self._edit_id = rid
        self.entry_desc.delete(0, "end")
        self.entry_desc.insert(0, r["descricao"])
        self.entry_valor.delete(0, "end")
        self.entry_valor.insert(0, str(r["valor"]))
        self.dp_data.set(r["data"])
        if r["categoria_id"]:
            c = conn.execute("SELECT nome FROM categorias WHERE id=?", (r["categoria_id"],)).fetchone()
            if c:
                self.combo_cat.set(c["nome"])
        self.btn_add.configure(text="Salvar Edicao", fg_color=self.colors.get("accent", "#00cec9"))

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        with get_connection() as conn:
            rows = conn.execute(
                """SELECT r.id, r.descricao, r.valor, r.data, COALESCE(c.nome,'Sem categoria') as cat
                   FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                   ORDER BY r.data DESC"""
            ).fetchall()

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma receita cadastrada\n\nClique em '+ Adicionar' acima",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Data", "Descricao", "Categoria", "Valor", "", ""]):
            self._criar_label(hdr, txt, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=col, padx=10)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=42)
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(row, text=r["data"], font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=r["descricao"], font=ctk.CTkFont(size=13)).grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=r["cat"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=formatar_moeda(r["valor"]), font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=self.colors.get("green", "#00b894")).grid(row=0, column=3, padx=10, pady=8, sticky="w")
            ctk.CTkButton(row, text="E", width=28, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color=self.colors.get("accent", "#00cec9"), hover_color="#00a3a3",
                           command=lambda rid=r["id"]: self._editar(rid)).grid(row=0, column=4, padx=(10, 4), pady=8)
            ctk.CTkButton(row, text="X", width=28, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda rid=r["id"]: self._excluir(rid)).grid(row=0, column=5, padx=(4, 10), pady=8)

    def _excluir(self, rid):
        if self._confirmar_exclusao("Excluir Receita", "Deseja excluir esta receita?"):
            with get_connection() as conn:
                conn.execute("DELETE FROM receitas WHERE id=?", (rid,))
                conn.commit()
            mostrar_toast(self, "Receita excluida!", "sucesso")
            self._atualizar()
            self._atualizar_total()
