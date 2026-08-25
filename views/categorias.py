import logging
import sqlite3

import customtkinter as ctk

from components.base_view import BaseView
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from constants import ITENS_POR_PAGINA
from database import get_connection

logger = logging.getLogger("financeiro.categorias")


class CategoriasView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._edit_id = None
        self._pagina_atual = 0
        self._termo_busca = ""
        self._criar_header()
        self._criar_filtro()
        self._criar_formulario()
        self._criar_barra_busca()
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
                command=self._on_filtro_mudou,
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

    def _criar_barra_busca(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        self.grid_rowconfigure(3, weight=1)
        barra.grid_columnconfigure(0, weight=1)

        self.entry_busca = self._criar_entry(barra, "Buscar categoria...")
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

    def _on_filtro_mudou(self):
        self._pagina_atual = 0
        self._atualizar()

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
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao contar categorias: %s", e)
            return
        max_paginas = max(0, (total - 1) // ITENS_POR_PAGINA)
        if self._pagina_atual < max_paginas:
            self._pagina_atual += 1
            self._atualizar()

    def _contar_total(self, conn):
        filtro = self.filtro_var.get()
        query = "SELECT COUNT(*) as cnt FROM categorias"
        params = ()
        conds = []
        if filtro == "Receita":
            conds.append("tipo='receita'")
        elif filtro == "Despesa":
            conds.append("tipo='despesa'")
        if self._termo_busca:
            conds.append("LOWER(nome) LIKE ?")
            params = (f"%{self._termo_busca}%",)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        return conn.execute(query, params).fetchone()["cnt"]

    def _tem_dependencias(self, conn, cid):
        r = conn.execute(
            "SELECT (SELECT COUNT(*) FROM receitas WHERE categoria_id=?) + "
            "(SELECT COUNT(*) FROM despesas WHERE categoria_id=?) + "
            "(SELECT COUNT(*) FROM orcamentos WHERE categoria_id=?) as cnt",
            (cid, cid, cid)).fetchone()
        return r["cnt"] > 0

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get()
        cor = self.entry_cor.get().strip()

        if not self._validar_campos({"Nome": nome}):
            return

        try:
            with get_connection() as conn:
                if self._edit_id:
                    conn.execute("UPDATE categorias SET nome=?,cor=?,tipo=? WHERE id=?",
                                 (nome, cor, tipo, self._edit_id))
                    conn.commit()
                    mostrar_toast(self, f"Categoria '{nome}' atualizada!")
                    self._edit_id = None
                    self.btn_add.configure(text="+ Adicionar")
                else:
                    conn.execute("INSERT INTO categorias (nome,cor,tipo) VALUES (?,?,?)", (nome, cor, tipo))
                    conn.commit()
                    mostrar_toast(self, f"Categoria '{nome}' criada!")
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao salvar categoria: %s", e)
            mostrar_toast(self, f"Erro ao salvar categoria: {e}", "erro")
            return

        self.entry_nome.delete(0, "end")
        self.entry_cor.delete(0, "end")
        self.entry_cor.insert(0, "#6c5ce7")
        self._atualizar()

    def _editar(self, cid):
        try:
            with get_connection() as conn:
                c = conn.execute("SELECT * FROM categorias WHERE id=?", (cid,)).fetchone()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categoria: %s", e)
            mostrar_toast(self, "Erro ao carregar categoria.", "erro")
            return
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
        conds = []
        params = ()
        if filtro == "Receita":
            conds.append("tipo='receita'")
        elif filtro == "Despesa":
            conds.append("tipo='despesa'")
        if self._termo_busca:
            conds.append("LOWER(nome) LIKE ?")
            params = (f"%{self._termo_busca}%",)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY tipo, nome"

        try:
            with get_connection() as conn:
                total = self._contar_total(conn)
                paginated_query = query + " LIMIT ? OFFSET ?"
                paginated_params = params + (ITENS_POR_PAGINA, self._pagina_atual * ITENS_POR_PAGINA)
                rows = conn.execute(paginated_query, paginated_params).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categorias: %s", e)
            mostrar_toast(self, "Erro ao carregar categorias.", "erro")
            return

        total_paginas = max(1, (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
        inicio = self._pagina_atual * ITENS_POR_PAGINA + 1 if rows else 0
        fim = min(inicio + len(rows) - 1, total) if rows else 0
        self.lbl_count.configure(text=f"{total} categorias")
        self.lbl_resultados.configure(text=f"{inicio}-{fim} de {total}" if rows else "0 de 0")
        self.btn_prev.configure(state="normal" if self._pagina_atual > 0 else "disabled")
        self.btn_next.configure(state="normal" if self._pagina_atual < total_paginas - 1 else "disabled")

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

            btn_edit = ctk.CTkButton(row, text="\u270E", width=26, height=26, corner_radius=6,
                                      font=ctk.CTkFont(size=11),
                                      fg_color=self.colors.get("accent", "#00cec9"), hover_color="#00a3a3",
                                      command=lambda cid=c["id"]: self._editar(cid))
            btn_edit.grid(row=0, column=3, padx=(6, 3), pady=6)
            Tooltip(btn_edit, "Editar categoria", self.colors)

            btn_del = ctk.CTkButton(row, text="\u2715", width=26, height=26, corner_radius=6,
                                      font=ctk.CTkFont(size=11),
                                      fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                                      command=lambda cid=c["id"]: self._excluir(cid))
            btn_del.grid(row=0, column=4, padx=(3, 10), pady=6)
            Tooltip(btn_del, "Excluir categoria", self.colors)

    def _excluir(self, cid):
        try:
            with get_connection() as conn:
                if self._tem_dependencias(conn, cid):
                    mostrar_toast(self, "Nao e possivel excluir: existem lancamentos usando esta categoria", "aviso")
                    return
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao verificar dependencias: %s", e)
            mostrar_toast(self, f"Erro ao verificar dependencias: {e}", "erro")
            return
        if self._confirmar_exclusao("Excluir Categoria", "Deseja excluir esta categoria?"):
            try:
                with get_connection() as conn:
                    conn.execute("DELETE FROM categorias WHERE id=?", (cid,))
                    conn.commit()
                mostrar_toast(self, "Categoria excluida!", "sucesso")
                self._atualizar()
            except (sqlite3.Error, ValueError) as e:
                logger.error("Erro ao excluir categoria: %s", e)
                mostrar_toast(self, f"Erro ao excluir: {e}", "erro")
