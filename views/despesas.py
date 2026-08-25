import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_data_atual
from components.toast import mostrar_toast
from components.modals import ConfirmarExclusaoModal


class DespesasView(ctk.CTkFrame):
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
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(header, text="Despesas", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=self.colors.get("text", "#fff")).pack(side="left")
        total = self._obter_total()
        ctk.CTkLabel(header, text=f"Total: {formatar_moeda(total)}",
                      font=ctk.CTkFont(size=15, weight="bold"),
                      text_color=self.colors.get("red", "#d63031")).pack(side="right")

    def _criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=16)
        g.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(g, text="Descricao", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=0, sticky="w")
        self.entry_desc = ctk.CTkEntry(g, placeholder_text="Ex: Aluguel, Supermercado...",
                                        height=36, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Valor (R$)", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=1, sticky="w")
        self.entry_valor = ctk.CTkEntry(g, placeholder_text="0,00", height=36, corner_radius=8,
                                         fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                         border_color=self.colors.get("border", "#2d2d44"))
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Data", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, sticky="w")
        self.entry_data = ctk.CTkEntry(g, height=36, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_data.insert(0, obter_data_atual())
        self.entry_data.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Categoria", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=3, sticky="w")
        self.combo_cat = ctk.CTkComboBox(g, values=self._cats(), height=36, corner_radius=8,
                                          fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                          border_color=self.colors.get("border", "#2d2d44"),
                                          button_color=self.colors.get("primary", "#6c5ce7"))
        self.combo_cat.grid(row=1, column=3, sticky="ew", padx=(0, 6))

        ctk.CTkButton(g, text="+ Adicionar", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                       command=self._adicionar).grid(row=1, column=4, sticky="ew")

    def _criar_lista(self):
        container = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        container.grid(row=2, column=0, sticky="nsew")
        self.lista = ctk.CTkScrollableFrame(container, fg_color="transparent",
                                             scrollbar_button_color=self.colors.get("border", "#2d2d44"))
        self.lista.pack(fill="both", expand=True, padx=4, pady=4)
        self.lista.grid_columnconfigure(0, weight=1)
        self._atualizar()

    def _cats(self):
        conn = get_connection()
        cats = conn.execute("SELECT nome FROM categorias WHERE tipo='despesa' ORDER BY nome").fetchall()
        conn.close()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def _obter_total(self):
        conn = get_connection()
        t = conn.execute("SELECT COALESCE(SUM(valor),0) FROM despesas WHERE strftime('%Y-%m',data)=?",
                         (obter_data_atual()[:7],)).fetchone()[0]
        conn.close()
        return t

    def _adicionar(self):
        desc = self.entry_desc.get().strip()
        val = self.entry_valor.get().replace(",", ".").strip()
        data = self.entry_data.get().strip()
        cat = self.combo_cat.get()

        if not desc:
            mostrar_toast(self, "Informe a descricao", "erro")
            return
        if not val:
            mostrar_toast(self, "Informe o valor", "erro")
            return

        conn = get_connection()
        c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
        cid = c["id"] if c else None
        conn.execute("INSERT INTO despesas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                     (desc, float(val), data, cid))
        conn.commit()
        conn.close()

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, obter_data_atual())

        mostrar_toast(self, f"Despesa '{desc}' adicionada!")
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        conn = get_connection()
        rows = conn.execute(
            """SELECT d.id, d.descricao, d.valor, d.data,
                      COALESCE(c.nome,'Sem categoria') as cat
               FROM despesas d LEFT JOIN categorias c ON d.categoria_id=c.id
               ORDER BY d.data DESC"""
        ).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma despesa cadastrada\n\nClique em '+ Adicionar' acima",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Data", "Descricao", "Categoria", "Valor", ""]):
            ctk.CTkLabel(hdr, text=txt, font=ctk.CTkFont(size=10, weight="bold"),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=col, padx=10)

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
                          text_color=self.colors.get("red", "#d63031")).grid(row=0, column=3, padx=10, pady=8, sticky="w")
            ctk.CTkButton(row, text="X", width=30, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda did=r["id"]: self._excluir(did)).grid(row=0, column=4, padx=10, pady=8)

    def _excluir(self, did):
        modal = ConfirmarExclusaoModal(self, "Excluir Despesa", "Deseja excluir esta despesa?", colors=self.colors)
        self.wait_window(modal)
        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM despesas WHERE id=?", (did,))
            conn.commit()
            conn.close()
            mostrar_toast(self, "Despesa excluida!", "sucesso")
            self._atualizar()
