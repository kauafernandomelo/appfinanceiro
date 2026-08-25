import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda, obter_data_atual
from components.toast import mostrar_toast
from components.modals import ConfirmarExclusaoModal


TIPOS_INVESTIMENTO = [
    "Acoes",
    "FIIs",
    "Renda Fixa",
    "Tesouro Direto",
    "Criptomoedas",
    "Fundos",
    "Poupanca",
    "Previdencia",
    "Debentures",
    "CDB",
    "LCI/LCA",
    "Outros",
]


class InvestimentosView(ctk.CTkFrame):
    def __init__(self, master, colors=None):
        super().__init__(master, fg_color="transparent")
        self.colors = colors or {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._criar_header()
        self._criar_cards_resumo()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ctk.CTkLabel(header, text="Investimentos", font=ctk.CTkFont(size=28, weight="bold"),
                      text_color=self.colors.get("text", "#fff")).pack(side="left")

    def _criar_cards_resumo(self):
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        dados = self._obter_resumo()

        self._card(cards, "Total Investido", formatar_moeda(dados["investido"]),
                   self.colors.get("primary", "#6c5ce7"), 0)
        self._card(cards, "Valor Atual", formatar_moeda(dados["atual"]),
                   self.colors.get("accent", "#00cec9"), 1)

        lucro = dados["atual"] - dados["investido"]
        cor_lucro = self.colors.get("green", "#00b894") if lucro >= 0 else self.colors.get("red", "#d63031")
        self._card(cards, "Lucro/Prejuizo", formatar_moeda(lucro), cor_lucro, 2)

    def _card(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=self.colors.get("bg_card", "#1a1a2e"),
                             corner_radius=12, height=90)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        card.grid_propagate(False)

        ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=2).pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).pack(anchor="w", padx=16, pady=(10, 0))
        ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=cor).pack(anchor="w", padx=16, pady=(2, 0))

    def _criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=16)
        g.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(g, text="Nome", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=0, sticky="w")
        self.entry_nome = ctk.CTkEntry(g, placeholder_text="PETR4, Tesouro IPCA...",
                                        height=36, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Tipo", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=1, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(g, values=TIPOS_INVESTIMENTO, height=36, corner_radius=8,
                                           fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                           border_color=self.colors.get("border", "#2d2d44"),
                                           button_color=self.colors.get("primary", "#6c5ce7"))
        self.combo_tipo.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Valor Investido", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=2, sticky="w")
        self.entry_investido = ctk.CTkEntry(g, placeholder_text="0,00", height=36, corner_radius=8,
                                             fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                             border_color=self.colors.get("border", "#2d2d44"))
        self.entry_investido.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Valor Atual", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=3, sticky="w")
        self.entry_atual = ctk.CTkEntry(g, placeholder_text="0,00", height=36, corner_radius=8,
                                         fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                         border_color=self.colors.get("border", "#2d2d44"))
        self.entry_atual.grid(row=1, column=3, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(g, text="Data", font=ctk.CTkFont(size=11),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=4, sticky="w")
        self.entry_data = ctk.CTkEntry(g, height=36, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_data.insert(0, obter_data_atual())
        self.entry_data.grid(row=1, column=4, sticky="ew", padx=(0, 6))

        ctk.CTkButton(g, text="+ Adicionar", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("green", "#00b894"), hover_color="#00a884",
                       command=self._adicionar).grid(row=1, column=5, sticky="ew")

    def _criar_lista(self):
        container = ctk.CTkFrame(self, fg_color=self.colors.get("bg_card", "#1a1a2e"), corner_radius=12)
        container.grid(row=3, column=0, sticky="nsew")

        self.lista = ctk.CTkScrollableFrame(container, fg_color="transparent",
                                             scrollbar_button_color=self.colors.get("border", "#2d2d44"))
        self.lista.pack(fill="both", expand=True, padx=4, pady=4)
        self.lista.grid_columnconfigure(0, weight=1)
        self._atualizar()

    def _obter_resumo(self):
        conn = get_connection()
        rows = conn.execute("SELECT valor_investido, valor_atual FROM investimentos").fetchall()
        conn.close()
        investido = sum(r["valor_investido"] for r in rows)
        atual = sum(r["valor_atual"] for r in rows)
        return {"investido": investido, "atual": atual}

    def _adicionar(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get()
        inv = self.entry_investido.get().replace(",", ".").strip()
        atu = self.entry_atual.get().replace(",", ".").strip()
        data = self.entry_data.get().strip()

        if not nome:
            mostrar_toast(self, "Informe o nome do investimento", "erro")
            return
        if not inv:
            mostrar_toast(self, "Informe o valor investido", "erro")
            return

        atual_val = float(atu) if atu else float(inv)

        conn = get_connection()
        conn.execute(
            "INSERT INTO investimentos (nome, tipo, valor_investido, valor_atual, data) VALUES (?, ?, ?, ?, ?)",
            (nome, tipo, float(inv), atual_val, data),
        )
        conn.commit()
        conn.close()

        for e in [self.entry_nome, self.entry_investido, self.entry_atual]:
            e.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, obter_data_atual())

        mostrar_toast(self, f"Investimento '{nome}' adicionado!")
        self._atualizar()
        self._refresh_cards()

    def _refresh_cards(self):
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkFrame) and w != self.lista.master:
                pass

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        conn = get_connection()
        rows = conn.execute(
            "SELECT id, nome, tipo, valor_investido, valor_atual, data FROM investimentos ORDER BY data DESC"
        ).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhum investimento cadastrado",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=50)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(["Nome", "Tipo", "Investido", "Atual", "Lucro", "Data", ""]):
            ctk.CTkLabel(hdr, text=txt, font=ctk.CTkFont(size=10, weight="bold"),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=0, column=col, padx=10)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=42)
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=r["nome"], font=ctk.CTkFont(size=13)).grid(
                row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=r["tipo"], font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("accent", "#00cec9")).grid(
                row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=formatar_moeda(r["valor_investido"]),
                          font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=10, pady=8, sticky="w")

            lucro = r["valor_atual"] - r["valor_investido"]
            lucro_pct = (lucro / r["valor_investido"] * 100) if r["valor_investido"] > 0 else 0
            cor_lucro = self.colors.get("green", "#00b894") if lucro >= 0 else self.colors.get("red", "#d63031")
            sinal = "+" if lucro >= 0 else ""

            ctk.CTkLabel(row, text=formatar_moeda(r["valor_atual"]),
                          font=ctk.CTkFont(size=12, weight="bold"), text_color=cor_lucro).grid(
                row=0, column=3, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=f"{sinal}{formatar_moeda(lucro)} ({sinal}{lucro_pct:.1f}%)",
                          font=ctk.CTkFont(size=11), text_color=cor_lucro).grid(
                row=0, column=4, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=r["data"], font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
                row=0, column=5, padx=10, pady=8, sticky="w")

            ctk.CTkButton(row, text="X", width=30, height=28, corner_radius=6,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda rid=r["id"]: self._excluir(rid)).grid(
                row=0, column=6, padx=10, pady=8)

    def _excluir(self, rid):
        modal = ConfirmarExclusaoModal(self, "Excluir Investimento",
                                        "Deseja excluir este investimento?", colors=self.colors)
        self.wait_window(modal)
        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM investimentos WHERE id = ?", (rid,))
            conn.commit()
            conn.close()
            mostrar_toast(self, "Investimento excluido!", "sucesso")
            self._atualizar()
