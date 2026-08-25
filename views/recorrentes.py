import customtkinter as ctk
from datetime import datetime
from database import get_connection
from utils import formatar_moeda, obter_mes_atual
from components.toast import mostrar_toast
from components.base_view import BaseView
from components.modals import ConfirmarExclusaoModal


class RecorrentesView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Contas Recorrentes").pack(side="left")

        ctk.CTkButton(header, text="Gerar Lancamentos do Mes", height=32, corner_radius=8,
                       font=ctk.CTkFont(size=12, weight="bold"),
                       fg_color=self.colors.get("yellow", "#fdcb6e"), hover_color="#e0b341",
                       text_color="#000", command=self._gerar_mes).pack(side="right")

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=14)
        g.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._criar_label(g, "Descricao*").grid(row=0, column=0, sticky="w")
        self.entry_desc = self._criar_entry(g, "Ex: Aluguel")
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Valor (R$)*").grid(row=0, column=1, sticky="w")
        self.entry_valor = self._criar_entry(g, "0,00")
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Tipo").grid(row=0, column=2, sticky="w")
        self.combo_tipo = self._criar_combo(g, ["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=2, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Categoria").grid(row=0, column=3, sticky="w")
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=3, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Dia do Mes*").grid(row=0, column=4, sticky="w")
        self.entry_dia = self._criar_entry(g, "1-31")
        self.entry_dia.grid(row=1, column=4, sticky="ew", padx=(0, 5))

        ctk.CTkButton(g, text="+ Adicionar", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=12, weight="bold"),
                       fg_color=self.colors.get("primary", "#6c5ce7"),
                       hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                       command=self._adicionar).grid(row=1, column=5, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=2, column=0, sticky="nsew")
        self._atualizar()

    def _cats(self):
        with get_connection() as conn:
            cats = conn.execute("SELECT nome FROM categorias ORDER BY nome").fetchall()
        return [c["nome"] for c in cats] if cats else ["Sem categoria"]

    def _adicionar(self):
        desc = self.entry_desc.get().strip()
        val_str = self.entry_valor.get().replace(",", ".").strip()
        tipo = self.combo_tipo.get()
        cat = self.combo_cat.get()
        dia = self.entry_dia.get().strip()

        if not self._validar_campos({"Descricao": desc, "Valor": val_str, "Dia": dia}):
            return
        val = self._validar_valor(val_str)
        if val is None:
            return
        try:
            dia_int = int(dia)
            if not 1 <= dia_int <= 31:
                raise ValueError
        except ValueError:
            mostrar_toast(self, "Dia invalido! Use 1-31", "erro")
            return

        with get_connection() as conn:
            c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
            cid = c["id"] if c else None
            conn.execute("INSERT INTO recorrentes (descricao,valor,tipo,categoria_id,dia_mes) VALUES (?,?,?,?,?)",
                         (desc, val, tipo, cid, dia_int))
            conn.commit()

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_dia.delete(0, "end")
        mostrar_toast(self, f"'{desc}' adicionada!")
        self._atualizar()

    def _gerar_mes(self):
        mes = obter_mes_atual()
        ano, mes_num = mes.split("-")
        dias_no_mes = 31 if mes_num in ("01","03","05","07","08","10","12") else 30 if mes_num != "02" else 28

        with get_connection() as conn:
            ativos = conn.execute("SELECT * FROM recorrentes WHERE ativo=1").fetchall()
            ja_existe = conn.execute(
                "SELECT COUNT(*) FROM (SELECT descricao FROM despesas WHERE strftime('%Y-%m',data)=? UNION ALL "
                "SELECT descricao FROM receitas WHERE strftime('%Y-%m',data)=?)",
                (mes, mes)
            ).fetchone()[0]

            if ja_existe > 0:
                mostrar_toast(self, f"Ja existem lancamentos em {mes}. Ignorando duplicatas.", "erro")
                return

            gerados = 0
            for r in ativos:
                dia = min(r["dia_mes"], dias_no_mes)
                data = f"{ano}-{mes_num:02d}-{dia:02d}"
                cat = conn.execute("SELECT id FROM categorias WHERE id=?", (r["categoria_id"],)).fetchone()
                cid = cat["id"] if cat else None

                if r["tipo"] == "receita":
                    conn.execute("INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                                 (r["descricao"], r["valor"], data, cid))
                else:
                    conn.execute("INSERT INTO despesas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                                 (r["descricao"], r["valor"], data, cid))
                gerados += 1

            conn.commit()

        mostrar_toast(self, f"{gerados} lancamentos gerados para {mes}!")

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        with get_connection() as conn:
            rows = conn.execute(
                "SELECT r.id, r.descricao, r.valor, r.tipo, r.dia_mes, r.ativo, "
                "COALESCE(c.nome,'Sem categoria') as cat "
                "FROM recorrentes r LEFT JOIN categorias c ON r.categoria_id=c.id "
                "ORDER BY r.tipo, r.dia_mes"
            ).fetchall()

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma conta recorrente\n\nAdicione contas que se repetem todo mes",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Descricao", "Tipo", "Categoria", "Dia", "Valor", "Status", ""]):
            self._criar_label(hdr, txt, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=col, padx=8)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=42)
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(row, text=r["descricao"], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=8, pady=8, sticky="w")

            tc = self.colors.get("green", "#00b894") if r["tipo"] == "receita" else self.colors.get("red", "#d63031")
            badge = ctk.CTkFrame(row, fg_color=tc, corner_radius=10)
            badge.grid(row=0, column=1, padx=6, pady=8)
            ctk.CTkLabel(badge, text=r["tipo"].capitalize(), font=ctk.CTkFont(size=9, weight="bold"),
                          text_color="#fff").pack(padx=8, pady=2)

            ctk.CTkLabel(row, text=r["cat"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=f"Dia {r['dia_mes']}", font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=3, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=formatar_moeda(r["valor"]), font=ctk.CTkFont(size=12, weight="bold"),
                          text_color=tc).grid(row=0, column=4, padx=8, pady=8, sticky="w")

            st = "Ativo" if r["ativo"] else "Inativo"
            sc = self.colors.get("green", "#00b894") if r["ativo"] else self.colors.get("text_dim", "#a0a0a0")
            ctk.CTkButton(row, text=st, width=52, height=26, corner_radius=6,
                           font=ctk.CTkFont(size=10), fg_color=sc, hover_color="#00a884",
                           command=lambda rid=r["id"], at=r["ativo"]: self._toggle(rid, at)).grid(row=0, column=5, padx=6, pady=8)

            ctk.CTkButton(row, text="X", width=26, height=26, corner_radius=6,
                           font=ctk.CTkFont(size=10, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda rid=r["id"]: self._excluir(rid)).grid(row=0, column=6, padx=8, pady=8)

    def _toggle(self, rid, atual):
        with get_connection() as conn:
            conn.execute("UPDATE recorrentes SET ativo=? WHERE id=?", (0 if atual else 1, rid))
            conn.commit()
        mostrar_toast(self, "Status atualizado!")
        self._atualizar()

    def _excluir(self, rid):
        if self._confirmar_exclusao("Excluir Recorrente", "Deseja excluir esta conta?"):
            with get_connection() as conn:
                conn.execute("DELETE FROM recorrentes WHERE id=?", (rid,))
                conn.commit()
            mostrar_toast(self, "Conta excluida!", "sucesso")
            self._atualizar()
