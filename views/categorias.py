import logging
import re
import sqlite3

import customtkinter as ctk

from components.base_view import BaseView
from components.empty_state import EmptyState
from components.pagination import PaginationBar
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from constants import (
    ACTION_BUTTON_SIZE,
    BUTTON_CORNER_RADIUS,
    CARD_CORNER_RADIUS,
    FONT_BODY,
    FONT_SMALL,
    ICONS,
    ITENS_POR_PAGINA,
    ROW_HEIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
)
from database import get_connection

logger = logging.getLogger("financeiro.categorias")

HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class CategoriasView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(4, weight=1)
        self._edit_id = None
        self._pagina_atual = 1
        self._termo_busca = ""
        self._total_paginas = 1
        self._criar_header()
        self._criar_filtro()
        self._criar_formulario()
        self._criar_barra_busca()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, "Categorias").pack(side="left")
        self.lbl_count = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=FONT_BODY),
                                       text_color=self.colors.get("text_dim", "#606078"))
        self.lbl_count.pack(side="right")

    def _criar_filtro(self):
        filtro = ctk.CTkFrame(self, fg_color="transparent")
        filtro.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_LG))
        self.filtro_var = ctk.StringVar(value="Todas")
        for txt in ["Todas", "Receita", "Despesa"]:
            ctk.CTkRadioButton(
                filtro, text=txt, variable=self.filtro_var, value=txt,
                font=ctk.CTkFont(size=FONT_BODY),
                fg_color=self.colors.get("primary", "#6c5ce7"),
                hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                command=self._on_filtro_mudou,
            ).pack(side="left", padx=(0, SPACING_XL))

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=2, column=0, sticky="ew", pady=(0, SPACING_LG))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)
        g.grid_columnconfigure((0, 1, 2), weight=1)

        self._criar_label(g, "Nome*").grid(row=0, column=0, sticky="w", pady=(0, SPACING_SM))
        self.entry_nome = self._criar_entry(g, "Ex: Alimentacao")
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Tipo").grid(row=0, column=1, sticky="w", pady=(0, SPACING_SM))
        self.combo_tipo = self._criar_combo(g, ["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=1, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Cor (hex)").grid(row=0, column=2, sticky="w", pady=(0, SPACING_SM))
        self.entry_cor = self._criar_entry(g, "#6c5ce7")
        self.entry_cor.insert(0, "#6c5ce7")
        self.entry_cor.grid(row=1, column=2, sticky="ew", padx=(0, SPACING_SM))
        self.entry_cor.bind("<FocusOut>", lambda e: self._validar_cor_hex())
        self.entry_cor.bind("<KeyRelease>", lambda e: self._validar_cor_hex())

        self.btn_add = ctk.CTkButton(
            g, text=f"{ICONS['add']} Adicionar", height=38, corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._salvar,
        )
        self.btn_add.grid(row=1, column=3, sticky="ew")

    def _validar_cor_hex(self):
        cor = self.entry_cor.get().strip()
        if cor and not HEX_PATTERN.match(cor):
            self.entry_cor.configure(border_color=self.colors.get("red", "#d63031"))
        else:
            self.entry_cor.configure(border_color=self.colors.get("border", "#2a2a48"))

    def _criar_barra_busca(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=3, column=0, sticky="ew", pady=(0, SPACING_SM))
        barra.grid_columnconfigure(0, weight=1)

        self.entry_busca = self._criar_entry(barra, f"{ICONS['search']} Buscar categoria...")
        self.entry_busca.grid(row=0, column=0, sticky="ew", padx=(0, SPACING_SM))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._on_busca())

        self.pagination = PaginationBar(barra, colors=self.colors, on_page_change=self._on_page_change)
        self.pagination.grid(row=0, column=1, sticky="e")

    def _on_page_change(self, nova_pagina):
        self._pagina_atual = nova_pagina
        self._atualizar()

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=4, column=0, sticky="nsew")
        self._atualizar()

    def _on_filtro_mudou(self):
        self._pagina_atual = 1
        self._atualizar()

    def _on_busca(self):
        self._termo_busca = self.entry_busca.get().strip().lower()
        self._pagina_atual = 1
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

        if cor and not HEX_PATTERN.match(cor):
            mostrar_toast(self, "Formato de cor invalido! Use #RRGGBB.", "erro")
            return

        try:
            with get_connection() as conn:
                if self._edit_id:
                    conn.execute("UPDATE categorias SET nome=?,cor=?,tipo=? WHERE id=?",
                                 (nome, cor, tipo, self._edit_id))
                    conn.commit()
                    mostrar_toast(self, f"Categoria '{nome}' atualizada!")
                    self._edit_id = None
                    self.btn_add.configure(text=f"{ICONS['add']} Adicionar",
                                           fg_color=self.colors.get("primary", "#6c5ce7"))
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
        self.entry_cor.configure(border_color=self.colors.get("border", "#2a2a48"))
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
        self.btn_add.configure(text=f"{ICONS['check']} Salvar Edicao",
                               fg_color=self.colors.get("accent", "#00cec9"))

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
                self._total_paginas = max(1, (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
                if self._pagina_atual > self._total_paginas:
                    self._pagina_atual = self._total_paginas
                offset = (self._pagina_atual - 1) * ITENS_POR_PAGINA
                paginated_query = query + " LIMIT ? OFFSET ?"
                paginated_params = params + (ITENS_POR_PAGINA, offset)
                rows = conn.execute(paginated_query, paginated_params).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categorias: %s", e)
            mostrar_toast(self, "Erro ao carregar categorias.", "erro")
            return

        inicio = (self._pagina_atual - 1) * ITENS_POR_PAGINA + 1 if rows else 0
        fim = min(inicio + len(rows) - 1, total) if rows else 0
        self.lbl_count.configure(text=f"{total} categorias")
        self.pagination.atualizar(self._pagina_atual, self._total_paginas, total, inicio, fim)

        if not rows:
            empty = EmptyState(
                self.lista,
                icone=ICONS["categorias"],
                titulo="Nenhuma categoria encontrada",
                subtitulo="Adicione categorias para organizar seus lancamentos",
                colors=self.colors,
            )
            empty.pack(expand=True, fill="both")
            return

        hdr = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_card", "#161630"),
                            corner_radius=CARD_CORNER_RADIUS, height=ROW_HEIGHT,
                            border_width=1, border_color=self.colors.get("border", "#2a2a48"))
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_SM))
        hdr.grid_propagate(False)
        for col, txt in enumerate(["Cor", "Nome", "Tipo", "", ""]):
            ctk.CTkLabel(hdr, text=txt,
                         font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                         text_color=self.colors.get("text", "#f0f0f8")).grid(
                row=0, column=col, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

        for i, c in enumerate(rows):
            bg = self.colors.get("bg_card", "#161630") if i % 2 == 0 else self.colors.get("bg_elevated", "#1e1e3a")
            row = ctk.CTkFrame(self.lista, fg_color=bg,
                                corner_radius=CARD_CORNER_RADIUS, height=ROW_HEIGHT,
                                border_width=1, border_color=self.colors.get("border", "#2a2a48"))
            row.grid(row=i + 1, column=0, sticky="ew", pady=1)
            row.grid_propagate(False)

            def _enter(e, r=row):
                r.configure(fg_color=self.colors.get("bg_hover", "#252550"))

            def _leave(e, r=row, idx=i):
                c_bg = self.colors.get("bg_card", "#161630") if idx % 2 == 0 else self.colors.get("bg_elevated", "#1e1e3a")
                r.configure(fg_color=c_bg)

            row.bind("<Enter>", _enter)
            row.bind("<Leave>", _leave)

            ctk.CTkFrame(row, fg_color=c["cor"], width=14, height=14, corner_radius=4).grid(
                row=0, column=0, padx=SPACING_MD, pady=SPACING_SM)
            ctk.CTkLabel(row, text=c["nome"], font=ctk.CTkFont(size=FONT_BODY),
                         text_color=self.colors.get("text", "#f0f0f8")).grid(
                row=0, column=1, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

            tc = self.colors.get("green", "#00b894") if c["tipo"] == "receita" else self.colors.get("red", "#d63031")
            badge = ctk.CTkFrame(row, fg_color=tc, corner_radius=10)
            badge.grid(row=0, column=2, padx=SPACING_MD, pady=SPACING_SM)
            ctk.CTkLabel(badge, text=c["tipo"].capitalize(),
                         font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                         text_color="#fff").pack(padx=SPACING_SM, pady=2)

            btn_edit = ctk.CTkButton(
                row, text=ICONS["edit"], width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS, font=ctk.CTkFont(size=FONT_BODY),
                fg_color=self.colors.get("primary", "#6c5ce7"),
                hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                command=lambda cid=c["id"]: self._editar(cid))
            btn_edit.grid(row=0, column=3, padx=(SPACING_SM, 2), pady=SPACING_SM)
            Tooltip(btn_edit, "Editar categoria", self.colors)

            btn_del = ctk.CTkButton(
                row, text=ICONS["delete"], width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS, font=ctk.CTkFont(size=FONT_BODY),
                fg_color=self.colors.get("red", "#d63031"),
                hover_color=self.colors.get("red_hover", "#a32525"),
                command=lambda cid=c["id"]: self._excluir(cid))
            btn_del.grid(row=0, column=4, padx=(2, SPACING_MD), pady=SPACING_SM)
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
