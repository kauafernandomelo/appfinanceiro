import calendar
from datetime import datetime

import customtkinter as ctk

from components.base_view import BaseView
from components.datepicker import DatePicker
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from database import get_connection
from utils import formatar_moeda, obter_data_atual, validar_data


class ReceitasView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._edit_id = None
        self._page = 1
        self._per_page = 15
        self._all_rows = []
        self._criar_header()
        self._criar_formulario()
        self._criar_search()
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
        g.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

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

        self.chk_parcelado = ctk.CTkCheckBox(
            g, text="Parcelar?", font=ctk.CTkFont(size=11),
            text_color=self.colors.get("text_dim", "#a0a0a0"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._toggle_parcelas,
        )
        self.chk_parcelado.grid(row=0, column=4, sticky="w", padx=(6, 0))
        self.entry_parcelas = self._criar_entry(g, "3x")
        self.entry_parcelas.grid(row=1, column=4, sticky="ew", padx=(6, 0))
        self.entry_parcelas.configure(state="disabled")

        self.btn_add = ctk.CTkButton(
            g, text="+ Adicionar", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("green", "#00b894"), hover_color="#00a884",
            command=self._salvar,
        )
        self.btn_add.grid(row=1, column=5, sticky="ew", padx=(6, 0))

    def _toggle_parcelas(self):
        if self.chk_parcelado.get():
            self.entry_parcelas.configure(state="normal")
        else:
            self.entry_parcelas.configure(state="disabled")

    def _criar_search(self):
        search_card = self._criar_card_frame(self)
        search_card.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        sg = ctk.CTkFrame(search_card, fg_color="transparent")
        sg.pack(fill="x", padx=12, pady=8)
        sg.grid_columnconfigure(0, weight=3)
        sg.grid_columnconfigure(1, weight=1)

        self.entry_search = self._criar_entry(sg, "Buscar receita...")
        self.entry_search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_search.bind("<KeyRelease>", lambda e: self._filtrar())

        cats = ["Todas"] + [c for c in self._cats() if c != "Sem categoria"]
        self.combo_filtro_cat = self._criar_combo(sg, cats, command=lambda v: self._filtrar())
        self.combo_filtro_cat.grid(row=0, column=1, sticky="ew")
        self.combo_filtro_cat.set("Todas")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._carregar_dados()

    def _cats(self):
        try:
            with get_connection() as conn:
                cats = conn.execute("SELECT nome FROM categorias WHERE tipo='receita' ORDER BY nome").fetchall()
            return [c["nome"] for c in cats] if cats else ["Sem categoria"]
        except Exception as e:
            mostrar_toast(self, "Erro ao carregar categorias: " + str(e), "erro")
            return ["Sem categoria"]

    def _atualizar_total(self):
        try:
            with get_connection() as conn:
                t = conn.execute("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE strftime('%Y-%m',data)=?",
                                 (obter_data_atual()[:7],)).fetchone()[0]
            self.lbl_total.configure(text=f"Total: {formatar_moeda(t)}")
        except Exception as e:
            mostrar_toast(self, "Erro ao calcular total: " + str(e), "erro")

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
        parcelado = self.chk_parcelado.get()

        try:
            with get_connection() as conn:
                c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
                cid = c["id"] if c else None

                if self._edit_id:
                    conn.execute("UPDATE receitas SET descricao=?,valor=?,data=?,categoria_id=? WHERE id=?",
                                 (desc, val, data, cid, self._edit_id))
                    mostrar_toast(self, f"Receita '{desc}' atualizada!")
                    self._edit_id = None
                    self.btn_add.configure(text="+ Adicionar", fg_color=self.colors.get("green", "#00b894"))
                elif parcelado:
                    n_str = self.entry_parcelas.get().replace("x", "").replace("X", "").strip()
                    if not n_str or not n_str.isdigit() or int(n_str) < 2:
                        mostrar_toast(self, "Informe o numero de parcelas (minimo 2)", "erro")
                        return
                    n = int(n_str)
                    valor_parcela = round(val / n, 2)
                    dt = datetime.strptime(data, "%Y-%m-%d")
                    for i in range(n):
                        m = dt.month + i
                        y = dt.year + (m - 1) // 12
                        m = (m - 1) % 12 + 1
                        d = min(dt.day, calendar.monthrange(y, m)[1])
                        data_parcela = f"{y:04d}-{m:02d}-{d:02d}"
                        desc_p = f"{desc} ({i+1}/{n})"
                        if i == 0:
                            diff = round(val - valor_parcela * n, 2)
                            valor_p = valor_parcela + diff
                        else:
                            valor_p = valor_parcela
                        conn.execute("INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                                     (desc_p, valor_p, data_parcela, cid))
                    mostrar_toast(self, f"{n} parcelas de {formatar_moeda(valor_parcela)} criadas!")
                else:
                    conn.execute("INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                                 (desc, val, data, cid))
                    mostrar_toast(self, f"Receita '{desc}' adicionada!")

            self.entry_desc.delete(0, "end")
            self.entry_valor.delete(0, "end")
            self.dp_data.set(obter_data_atual())
            self.chk_parcelado.deselect()
            self.entry_parcelas.delete(0, "end")
            self.entry_parcelas.configure(state="disabled")
            self._carregar_dados()
            self._atualizar_total()
        except Exception as e:
            mostrar_toast(self, "Erro ao salvar: " + str(e), "erro")

    def _editar(self, rid):
        try:
            with get_connection() as conn:
                r = conn.execute("SELECT * FROM receitas WHERE id=?", (rid,)).fetchone()
                if not r:
                    return
                cat_name = None
                if r["categoria_id"]:
                    c = conn.execute("SELECT nome FROM categorias WHERE id=?", (r["categoria_id"],)).fetchone()
                    if c:
                        cat_name = c["nome"]

            self._edit_id = rid
            self.entry_desc.delete(0, "end")
            self.entry_desc.insert(0, r["descricao"])
            self.entry_valor.delete(0, "end")
            self.entry_valor.insert(0, str(r["valor"]))
            self.dp_data.set(r["data"])
            if cat_name:
                self.combo_cat.set(cat_name)
            self.btn_add.configure(text="Salvar Edicao", fg_color=self.colors.get("accent", "#00cec9"))
        except Exception as e:
            mostrar_toast(self, "Erro ao carregar receita: " + str(e), "erro")

    def _excluir(self, rid):
        if self._confirmar_exclusao("Excluir Receita", "Deseja excluir esta receita?"):
            try:
                with get_connection() as conn:
                    conn.execute("DELETE FROM receitas WHERE id=?", (rid,))
                    conn.commit()
                mostrar_toast(self, "Receita excluida!", "sucesso")
                self._carregar_dados()
                self._atualizar_total()
            except Exception as e:
                mostrar_toast(self, "Erro ao excluir: " + str(e), "erro")

    def _carregar_dados(self):
        try:
            with get_connection() as conn:
                self._all_rows = conn.execute(
                    """SELECT r.id, r.descricao, r.valor, r.data, COALESCE(c.nome,'Sem categoria') as cat
                       FROM receitas r LEFT JOIN categorias c ON r.categoria_id=c.id
                       ORDER BY r.data DESC"""
                ).fetchall()
        except Exception as e:
            mostrar_toast(self, "Erro ao carregar dados: " + str(e), "erro")
            self._all_rows = []
        self._filtrar()

    def _filtrar(self):
        busca = self.entry_search.get().strip().lower()
        filtro = self.combo_filtro_cat.get()
        filtered = []
        for r in self._all_rows:
            if busca and busca not in r["descricao"].lower():
                continue
            if filtro != "Todas" and r["cat"] != filtro:
                continue
            filtered.append(r)
        total = len(filtered)
        total_pages = max(1, (total + self._per_page - 1) // self._per_page)
        if self._page > total_pages:
            self._page = total_pages
        self._renderizar(filtered, total, total_pages)

    def _renderizar(self, rows, total, total_pages):
        for w in self.lista.winfo_children():
            w.destroy()

        start = (self._page - 1) * self._per_page
        end = min(start + self._per_page, total)
        page_rows = rows[start:end]

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma receita cadastrada\n\nClique em '+ Adicionar' acima",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        info = ctk.CTkLabel(self.lista,
                             text=f"Mostrando {start+1}-{end} de {total} registros",
                             font=ctk.CTkFont(size=11),
                             text_color=self.colors.get("text_dim", "#a0a0b0"))
        info.grid(row=0, column=0, sticky="w", padx=10, pady=(4, 4))

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Data", "Descricao", "Categoria", "Valor", "", ""]):
            self._criar_label(hdr, txt, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=col, padx=10)

        for i, r in enumerate(page_rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=42)
            row.grid(row=i + 2, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(row, text=r["data"], font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=r["descricao"], font=ctk.CTkFont(size=13)).grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=r["cat"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=formatar_moeda(r["valor"]), font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=self.colors.get("green", "#00b894")).grid(row=0, column=3, padx=10, pady=8, sticky="w")

            btn_edit = ctk.CTkButton(row, text="\u270e", width=28, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=13, weight="bold"),
                           fg_color=self.colors.get("accent", "#00cec9"), hover_color="#00a3a3",
                           command=lambda rid=r["id"]: self._editar(rid))
            btn_edit.grid(row=0, column=4, padx=(10, 4), pady=8)
            Tooltip(btn_edit, "Editar", self.colors)

            btn_del = ctk.CTkButton(row, text="\u2715", width=28, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=13, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda rid=r["id"]: self._excluir(rid))
            btn_del.grid(row=0, column=5, padx=(4, 10), pady=8)
            Tooltip(btn_del, "Excluir", self.colors)

        pag = ctk.CTkFrame(self.lista, fg_color="transparent")
        pag.grid(row=len(page_rows) + 2, column=0, sticky="ew", pady=(8, 4))

        btn_prev = ctk.CTkButton(pag, text="< Anterior", width=100, height=30, corner_radius=6,
                                  font=ctk.CTkFont(size=11),
                                  fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                  border_color=self.colors.get("border", "#2d2d44"), border_width=1,
                                  hover_color=self.colors.get("bg_hover", "#16213e"),
                                  command=lambda: self._mudar_pagina(-1, rows, total, total_pages),
                                  state="disabled" if self._page <= 1 else "normal")
        btn_prev.pack(side="left", padx=10)

        ctk.CTkLabel(pag, text=f"Pagina {self._page} de {total_pages}",
                      font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0b0")).pack(side="left", expand=True)

        btn_next = ctk.CTkButton(pag, text="Proximo >", width=100, height=30, corner_radius=6,
                                  font=ctk.CTkFont(size=11),
                                  fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                  border_color=self.colors.get("border", "#2d2d44"), border_width=1,
                                  hover_color=self.colors.get("bg_hover", "#16213e"),
                                  command=lambda: self._mudar_pagina(1, rows, total, total_pages),
                                  state="disabled" if self._page >= total_pages else "normal")
        btn_next.pack(side="right", padx=10)

    def _mudar_pagina(self, delta, rows, total, total_pages):
        self._page += delta
        self._renderizar(rows, total, total_pages)
