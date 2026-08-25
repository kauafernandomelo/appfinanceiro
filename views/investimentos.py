import customtkinter as ctk

from components.base_view import BaseView
from components.datepicker import DatePicker
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from database import get_connection
from enums import TipoInvestimento
from utils import formatar_moeda, obter_data_atual

ITENS_POR_PAGINA = 15


class InvestimentosView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._edit_id = None
        self._pagina_atual = 0
        self._termo_busca = ""
        self._criar_header()
        self._criar_cards()
        self._criar_formulario()
        self._criar_barra_busca()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._criar_titulo(header, "Investimentos").pack(side="left")

    def _criar_cards(self):
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self._atualizar_cards()

    def _atualizar_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        d = self._resumo()
        self._card(self.cards_frame, "Total Investido", formatar_moeda(d["inv"]),
                   self.colors.get("primary", "#6c5ce7"), 0)
        self._card(self.cards_frame, "Valor Atual", formatar_moeda(d["atu"]),
                   self.colors.get("accent", "#00cec9"), 1)
        lucro = d["atu"] - d["inv"]
        cl = self.colors.get("green", "#00b894") if lucro >= 0 else self.colors.get("red", "#d63031")
        self._card(self.cards_frame, "Lucro/Prejuizo", formatar_moeda(lucro), cl, 2)

    def _card(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=self.colors.get("bg_card", "#1a1a2e"),
                             corner_radius=12, height=85)
        card.grid(row=0, column=col, padx=4, sticky="ew")
        card.grid_propagate(False)
        ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=2).pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(anchor="w", padx=14, pady=(8, 0))
        ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=cor).pack(anchor="w", padx=14, pady=(2, 0))

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=14)
        g.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._criar_label(g, "Nome*").grid(row=0, column=0, sticky="w")
        self.entry_nome = self._criar_entry(g, "PETR4, Tesouro IPCA...")
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Tipo").grid(row=0, column=1, sticky="w")
        tipos = [t.value for t in TipoInvestimento]
        self.combo_tipo = self._criar_combo(g, tipos)
        self.combo_tipo.grid(row=1, column=1, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Investido*").grid(row=0, column=2, sticky="w")
        self.entry_inv = self._criar_entry(g, "0,00")
        self.entry_inv.grid(row=1, column=2, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Atual").grid(row=0, column=3, sticky="w")
        self.entry_atu = self._criar_entry(g, "0,00")
        self.entry_atu.grid(row=1, column=3, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Data*").grid(row=0, column=4, sticky="w")
        self.dp_data = DatePicker(g)
        self.dp_data.grid(row=1, column=4, sticky="ew", padx=(0, 5))

        self.btn_add = ctk.CTkButton(
            g, text="+ Adicionar", height=36, corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors.get("green", "#00b894"), hover_color="#00a884",
            command=self._salvar,
        )
        self.btn_add.grid(row=1, column=5, sticky="ew")

    def _criar_barra_busca(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        self.grid_rowconfigure(3, weight=1)
        barra.grid_columnconfigure(0, weight=1)

        self.entry_busca = self._criar_entry(barra, "Buscar por nome ou tipo...")
        self.entry_busca.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._on_busca())

        self.lbl_resultados = ctk.CTkLabel(barra, text="", font=ctk.CTkFont(size=11),
                                            text_color=self.colors.get("text_dim", "#a0a0a0"))
        self.lbl_resultados.grid(row=0, column=1, padx=(0, 8))

        self.btn_prev = ctk.CTkButton(barra, text="\u25C0", width=36, height=30, corner_radius=6,
                                       font=ctk.CTkFont(size=12),
                                       fg_color=self.colors.get("bg_card", "#1a1a2e"),
                                       border_color=self.colors.get("border", "#2d2d44"),
                                       border_width=1,
                                       hover_color=self.colors.get("bg_hover", "#16213e"),
                                       command=self._pagina_anterior)
        self.btn_prev.grid(row=0, column=2, padx=(0, 4))

        self.btn_next = ctk.CTkButton(barra, text="\u25B6", width=36, height=30, corner_radius=6,
                                       font=ctk.CTkFont(size=12),
                                       fg_color=self.colors.get("bg_card", "#1a1a2e"),
                                       border_color=self.colors.get("border", "#2d2d44"),
                                       border_width=1,
                                       hover_color=self.colors.get("bg_hover", "#16213e"),
                                       command=self._proxima_pagina)
        self.btn_next.grid(row=0, column=3)

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._atualizar()

    def _resumo(self):
        try:
            with get_connection() as conn:
                rows = conn.execute("SELECT valor_investido, valor_atual FROM investimentos").fetchall()
        except Exception:
            mostrar_toast(self, "Erro ao carregar resumo.", "erro")
            return {"inv": 0, "atu": 0}
        inv = sum(r["valor_investido"] for r in rows)
        atu = sum(r["valor_atual"] for r in rows)
        return {"inv": inv, "atu": atu}

    def _on_busca(self):
        self._termo_busca = self.entry_busca.get().strip().lower()
        self._pagina_atual = 0
        self._atualizar()

    def _pagina_anterior(self):
        if self._pagina_atual > 0:
            self._pagina_atual -= 1
            self._atualizar()

    def _proxima_pagina(self):
        try:
            with get_connection() as conn:
                total = self._contar_total(conn)
        except Exception:
            return
        max_paginas = max(0, (total - 1) // ITENS_POR_PAGINA)
        if self._pagina_atual < max_paginas:
            self._pagina_atual += 1
            self._atualizar()

    def _contar_total(self, conn):
        query = "SELECT COUNT(*) as cnt FROM investimentos"
        params = ()
        if self._termo_busca:
            query += " WHERE LOWER(nome) LIKE ? OR LOWER(tipo) LIKE ?"
            params = (f"%{self._termo_busca}%", f"%{self._termo_busca}%")
        return conn.execute(query, params).fetchone()["cnt"]

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get()
        inv_str = self.entry_inv.get().replace(",", ".").strip()
        atu_str = self.entry_atu.get().replace(",", ".").strip()
        data = self.dp_data.get()

        if not self._validar_campos({"Nome": nome, "Valor Investido": inv_str, "Data": data}):
            return
        val_inv = self._validar_valor(inv_str)
        if val_inv is None:
            return
        val_atu = self._validar_valor(atu_str) if atu_str else val_inv

        try:
            with get_connection() as conn:
                if self._edit_id:
                    conn.execute(
                        "UPDATE investimentos SET nome=?,tipo=?,valor_investido=?,valor_atual=?,data=? WHERE id=?",
                        (nome, tipo, val_inv, val_atu, data, self._edit_id))
                    mostrar_toast(self, f"'{nome}' atualizado!")
                    self._edit_id = None
                    self.btn_add.configure(text="+ Adicionar", fg_color=self.colors.get("green", "#00b894"))
                else:
                    conn.execute(
                        "INSERT INTO investimentos (nome,tipo,valor_investido,valor_atual,data) VALUES (?,?,?,?,?)",
                        (nome, tipo, val_inv, val_atu, data))
                    mostrar_toast(self, f"'{nome}' adicionado!")
        except Exception as e:
            mostrar_toast(self, f"Erro ao salvar: {e}", "erro")
            return

        self.entry_nome.delete(0, "end")
        self.entry_inv.delete(0, "end")
        self.entry_atu.delete(0, "end")
        self.dp_data.set(obter_data_atual())
        self._atualizar_cards()
        self._atualizar()

    def _editar(self, rid):
        try:
            with get_connection() as conn:
                r = conn.execute("SELECT * FROM investimentos WHERE id=?", (rid,)).fetchone()
        except Exception:
            mostrar_toast(self, "Erro ao carregar investimento.", "erro")
            return
        if not r:
            return
        self._edit_id = rid
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, r["nome"])
        self.combo_tipo.set(r["tipo"])
        self.entry_inv.delete(0, "end")
        self.entry_inv.insert(0, str(r["valor_investido"]))
        self.entry_atu.delete(0, "end")
        self.entry_atu.insert(0, str(r["valor_atual"]))
        self.dp_data.set(r["data"])
        self.btn_add.configure(text="Salvar Edicao", fg_color=self.colors.get("accent", "#00cec9"))

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        try:
            with get_connection() as conn:
                total = self._contar_total(conn)
                query = "SELECT id, nome, tipo, valor_investido, valor_atual, data FROM investimentos"
                params = ()
                if self._termo_busca:
                    query += " WHERE LOWER(nome) LIKE ? OR LOWER(tipo) LIKE ?"
                    params = (f"%{self._termo_busca}%", f"%{self._termo_busca}%")
                query += " ORDER BY data DESC LIMIT ? OFFSET ?"
                params = params + (ITENS_POR_PAGINA, self._pagina_atual * ITENS_POR_PAGINA)
                rows = conn.execute(query, params).fetchall()
        except Exception:
            mostrar_toast(self, "Erro ao carregar investimentos.", "erro")
            return

        total_paginas = max(1, (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
        inicio = self._pagina_atual * ITENS_POR_PAGINA + 1 if rows else 0
        fim = min(inicio + len(rows) - 1, total) if rows else 0
        self.lbl_resultados.configure(text=f"{inicio}-{fim} de {total}" if rows else "0 de 0")
        self.btn_prev.configure(state="normal" if self._pagina_atual > 0 else "disabled")
        self.btn_next.configure(state="normal" if self._pagina_atual < total_paginas - 1 else "disabled")

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhum investimento encontrado",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=50)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Nome", "Tipo", "Investido", "Atual", "Lucro", "Data", "", ""]):
            self._criar_label(hdr, txt, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=col, padx=8)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=40)
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(row, text=r["nome"], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=8, pady=7, sticky="w")
            ctk.CTkLabel(row, text=r["tipo"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("accent", "#00cec9")).grid(row=0, column=1, padx=8, pady=7, sticky="w")
            ctk.CTkLabel(row, text=formatar_moeda(r["valor_investido"]),
                          font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=8, pady=7, sticky="w")

            lucro = r["valor_atual"] - r["valor_investido"]
            pct = (lucro / r["valor_investido"] * 100) if r["valor_investido"] > 0 else 0
            cl = self.colors.get("green", "#00b894") if lucro >= 0 else self.colors.get("red", "#d63031")
            sinal = "+" if lucro >= 0 else ""

            ctk.CTkLabel(row, text=formatar_moeda(r["valor_atual"]), font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=cl).grid(row=0, column=3, padx=8, pady=7, sticky="w")
            ctk.CTkLabel(row, text=f"{sinal}{formatar_moeda(lucro)} ({sinal}{pct:.1f}%)",
                          font=ctk.CTkFont(size=10), text_color=cl).grid(row=0, column=4, padx=8, pady=7, sticky="w")
            ctk.CTkLabel(row, text=r["data"], font=ctk.CTkFont(size=10),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=5, padx=8, pady=7, sticky="w")

            btn_edit = ctk.CTkButton(row, text="\u270E", width=26, height=26, corner_radius=6,
                                      font=ctk.CTkFont(size=11),
                                      fg_color=self.colors.get("accent", "#00cec9"), hover_color="#00a3a3",
                                      command=lambda rid=r["id"]: self._editar(rid))
            btn_edit.grid(row=0, column=6, padx=(6, 3), pady=7)
            Tooltip(btn_edit, "Editar investimento", self.colors)

            btn_del = ctk.CTkButton(row, text="\u2715", width=26, height=26, corner_radius=6,
                                      font=ctk.CTkFont(size=11),
                                      fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                                      command=lambda rid=r["id"]: self._excluir(rid))
            btn_del.grid(row=0, column=7, padx=(3, 8), pady=7)
            Tooltip(btn_del, "Excluir investimento", self.colors)

    def _excluir(self, rid):
        if self._confirmar_exclusao("Excluir Investimento", "Deseja excluir este investimento?"):
            try:
                with get_connection() as conn:
                    conn.execute("DELETE FROM investimentos WHERE id=?", (rid,))
                    conn.commit()
                mostrar_toast(self, "Investimento excluido!", "sucesso")
                self._atualizar_cards()
                self._atualizar()
            except Exception as e:
                mostrar_toast(self, f"Erro ao excluir: {e}", "erro")
