import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda
from components.toast import mostrar_toast
from components.modals import ConfirmarExclusaoModal


class RecorrentesView(ctk.CTkFrame):
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
        ctk.CTkLabel(header, text="Contas Recorrentes", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=self.colors.get("text", "#fff")).pack(side="left")

    def _criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=16)
        g.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(g, text="Descricao", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=0, sticky="w")
        self.entry_desc = ctk.CTkEntry(g, placeholder_text="Ex: Aluguel", height=36, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Valor (R$)", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=1, sticky="w")
        self.entry_valor = ctk.CTkEntry(g, placeholder_text="0,00", height=36, corner_radius=8,
                                         fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                         border_color=self.colors.get("border", "#2d2d44"))
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Tipo", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(g, values=["receita", "despesa"], height=36, corner_radius=8,
                                           fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                           border_color=self.colors.get("border", "#2d2d44"),
                                           button_color=self.colors.get("primary", "#6c5ce7"))
        self.combo_tipo.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Dia do Mes", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=3, sticky="w")
        self.entry_dia = ctk.CTkEntry(g, placeholder_text="1-31", height=36, corner_radius=8,
                                       fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                       border_color=self.colors.get("border", "#2d2d44"))
        self.entry_dia.grid(row=1, column=3, sticky="ew", padx=(0, 6))

        ctk.CTkButton(g, text="+ Adicionar", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("primary", "#6c5ce7"),
                       hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                       command=self._adicionar).grid(row=1, column=4, sticky="ew")

    def _criar_lista(self):
        container = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        container.grid(row=2, column=0, sticky="nsew")
        self.lista = ctk.CTkScrollableFrame(container, fg_color="transparent",
                                             scrollbar_button_color=self.colors.get("border", "#2d2d44"))
        self.lista.pack(fill="both", expand=True, padx=4, pady=4)
        self.lista.grid_columnconfigure(0, weight=1)
        self._atualizar()

    def _adicionar(self):
        desc = self.entry_desc.get().strip()
        val = self.entry_valor.get().replace(",", ".").strip()
        tipo = self.combo_tipo.get()
        dia = self.entry_dia.get().strip()
        if not desc or not val or not dia:
            mostrar_toast(self, "Preencha todos os campos", "erro")
            return
        conn = get_connection()
        conn.execute("INSERT INTO recorrentes (descricao,valor,tipo,dia_mes) VALUES (?,?,?,?)",
                     (desc, float(val), tipo, int(dia)))
        conn.commit()
        conn.close()
        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_dia.delete(0, "end")
        mostrar_toast(self, f"Conta recorrente '{desc}' criada!")
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        conn = get_connection()
        rows = conn.execute("SELECT id,descricao,valor,tipo,dia_mes,ativo FROM recorrentes ORDER BY tipo,dia_mes").fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma conta recorrente\n\nAdicione contas que se repetem todo mes",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Descricao", "Tipo", "Dia", "Valor", "Status", ""]):
            ctk.CTkLabel(hdr, text=txt, font=ctk.CTkFont(size=10, weight="bold"),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=col, padx=10)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=42)
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(row, text=r["descricao"], font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=8, sticky="w")

            tc = self.colors.get("green", "#00b894") if r["tipo"] == "receita" else self.colors.get("red", "#d63031")
            badge = ctk.CTkFrame(row, fg_color=tc, corner_radius=10)
            badge.grid(row=0, column=1, padx=6, pady=8)
            ctk.CTkLabel(badge, text=r["tipo"].capitalize(), font=ctk.CTkFont(size=10, weight="bold"),
                          text_color="#fff").pack(padx=8, pady=2)

            ctk.CTkLabel(row, text=f"Dia {r['dia_mes']}", font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=formatar_moeda(r["valor"]), font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=tc).grid(row=0, column=3, padx=10, pady=8, sticky="w")

            st = "Ativo" if r["ativo"] else "Inativo"
            sc = self.colors.get("green", "#00b894") if r["ativo"] else self.colors.get("text_dim", "#a0a0a0")
            ctk.CTkButton(row, text=st, width=56, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=10), fg_color=sc, hover_color="#00a884",
                           command=lambda rid=r["id"], at=r["ativo"]: self._toggle(rid, at)).grid(row=0, column=4, padx=6, pady=8)

            ctk.CTkButton(row, text="X", width=28, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda rid=r["id"]: self._excluir(rid)).grid(row=0, column=5, padx=10, pady=8)

    def _toggle(self, rid, atual):
        conn = get_connection()
        conn.execute("UPDATE recorrentes SET ativo=? WHERE id=?", (0 if atual else 1, rid))
        conn.commit()
        conn.close()
        mostrar_toast(self, "Status atualizado!")
        self._atualizar()

    def _excluir(self, rid):
        modal = ConfirmarExclusaoModal(self, "Excluir Recorrente", "Deseja excluir esta conta?", colors=self.colors)
        self.wait_window(modal)
        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM recorrentes WHERE id=?", (rid,))
            conn.commit()
            conn.close()
            mostrar_toast(self, "Conta excluida!", "sucesso")
            self._atualizar()
