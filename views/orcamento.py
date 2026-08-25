import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_mes_atual
from components.toast import mostrar_toast
from components.base_view import BaseView


class OrcamentoView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Orcamento Mensal").pack(side="left")
        ctk.CTkLabel(header, text=obter_mes_atual(), font=ctk.CTkFont(size=14),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(side="right")

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=14)
        g.grid_columnconfigure((0, 1, 2), weight=1)

        self._criar_label(g, "Categoria*").grid(row=0, column=0, sticky="w")
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Limite (R$)*").grid(row=0, column=1, sticky="w")
        self.entry_limite = self._criar_entry(g, "0,00")
        self.entry_limite.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ctk.CTkButton(g, text="Definir Limite", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("yellow", "#fdcb6e"), hover_color="#e0b341",
                       text_color="#000", command=self._salvar).grid(row=1, column=2, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=2, column=0, sticky="nsew")
        self._atualizar()

    def _cats(self):
        with get_connection() as conn:
            cats = conn.execute("SELECT nome FROM categorias WHERE tipo='despesa' ORDER BY nome").fetchall()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def _salvar(self):
        cat = self.combo_cat.get()
        lim_str = self.entry_limite.get().replace(",", ".").strip()
        if not self._validar_campos({"Limite": lim_str}):
            return
        lim = self._validar_valor(lim_str)
        if lim is None:
            return

        with get_connection() as conn:
            c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
            if not c:
                return
            mes = obter_mes_atual()
            ex = conn.execute("SELECT id FROM orcamento WHERE categoria_id=? AND mes=?", (c["id"], mes)).fetchone()
            if ex:
                conn.execute("UPDATE orcamento SET limite=? WHERE id=?", (lim, ex["id"]))
            else:
                conn.execute("INSERT INTO orcamento (categoria_id,limite,mes) VALUES (?,?,?)", (c["id"], lim, mes))
            conn.commit()
        self.entry_limite.delete(0, "end")
        mostrar_toast(self, "Orcamento atualizado!")
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        mes = obter_mes_atual()
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT o.id, COALESCE(c.nome,'?') as cat, o.limite,
                          COALESCE(SUM(d.valor),0) as gasto
                   FROM orcamento o
                   LEFT JOIN categorias c ON o.categoria_id=c.id
                   LEFT JOIN despesas d ON d.categoria_id=c.id AND strftime('%Y-%m',d.data)=o.mes
                   WHERE o.mes=? GROUP BY o.id""", (mes,)).fetchall()

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhum orcamento definido\n\nSelecione uma categoria e defina um limite",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        for i, o in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=65)
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=o["cat"], font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=16, pady=10, sticky="w")

            pct = (o["gasto"] / o["limite"] * 100) if o["limite"] > 0 else 0
            bc = self.colors.get("green", "#00b894") if pct <= 80 else self.colors.get("yellow", "#fdcb6e") if pct <= 100 else self.colors.get("red", "#d63031")

            bf = ctk.CTkFrame(row, fg_color="transparent")
            bf.grid(row=0, column=1, padx=12, pady=10, sticky="ew")
            bf.grid_columnconfigure(0, weight=1)

            bar = ctk.CTkProgressBar(bf, progress_color=bc, height=8, corner_radius=4)
            bar.grid(row=0, column=0, sticky="ew")
            bar.set(min(pct / 100, 1.0))

            ctk.CTkLabel(bf, text=f"{formatar_moeda(o['gasto'])} / {formatar_moeda(o['limite'])}  ({pct:.0f}%)",
                          font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=1, column=0, sticky="w", pady=(4, 0))

            ctk.CTkButton(row, text="X", width=30, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda oid=o["id"]: self._excluir(oid)).grid(row=0, column=2, padx=12, pady=10)

    def _excluir(self, oid):
        with get_connection() as conn:
            conn.execute("DELETE FROM orcamento WHERE id=?", (oid,))
            conn.commit()
        mostrar_toast(self, "Orcamento removido!")
        self._atualizar()
