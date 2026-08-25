import os
import shutil
import sqlite3
from datetime import datetime

import customtkinter as ctk

from components.base_view import BaseView
from components.toast import mostrar_toast
from constants import (
    BUTTON_CORNER_RADIUS,
    FONT_CARD_TITLE,
    FONT_LABEL,
    FONT_SECTION,
    ICONS,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    __version__,
)
from database import DB_PATH


class ConfiguracoesView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(1, weight=1)
        self._criar_header()
        self._criar_conteudo()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, f"{ICONS['configuracoes']}  Configuracoes").pack(side="left")

    def _criar_conteudo(self):
        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=self.colors.get("border", "#2a2a48"),
        )
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        sec_backup = self._criar_card_frame(container)
        sec_backup.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_MD))
        inner = ctk.CTkFrame(sec_backup, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)

        self._criar_label(
            inner,
            f"{ICONS['info']}  Backup e Restauracao",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        ).pack(anchor="w")

        self._criar_label(
            inner,
            "Exporte ou importe seus dados financeiros.",
            font=ctk.CTkFont(size=FONT_LABEL),
        ).pack(anchor="w", pady=(SPACING_XS, SPACING_LG))

        btns_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btns_frame.pack(fill="x")

        ctk.CTkButton(
            btns_frame,
            text=f"{ICONS['check']}  Exportar Backup",
            height=36,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            fg_color=self.colors.get("positive", "#00b894"),
            hover_color=self.colors.get("positive_muted", "#00875f"),
            command=self._exportar_backup,
        ).pack(side="left", expand=True, fill="x", padx=(0, SPACING_SM))

        ctk.CTkButton(
            btns_frame,
            text=f"{ICONS['warning']}  Importar Backup",
            height=36,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_CARD_TITLE, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._importar_backup,
        ).pack(side="right", expand=True, fill="x", padx=(SPACING_SM, 0))

        sec_atalhos = self._criar_card_frame(container)
        sec_atalhos.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_MD))
        inner2 = ctk.CTkFrame(sec_atalhos, fg_color="transparent")
        inner2.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)

        self._criar_label(
            inner2,
            f"{ICONS['menu']}  Atalhos de Teclado",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        ).pack(anchor="w")

        atalhos = [
            ("Ctrl+N", "Novo registro na view atual"),
            ("Ctrl+R", "Ir para Receitas"),
            ("Ctrl+D", "Ir para Despesas"),
            ("Ctrl+I", "Ir para Investimentos"),
            ("Ctrl+B", "Ir para Categorias"),
            ("Ctrl+O", "Ir para Orcamento"),
            ("Ctrl+M", "Ir para Metas"),
            ("Ctrl+C", "Ir para Recorrentes"),
            ("Ctrl+T", "Ir para Configuracoes"),
            ("Ctrl+L", "Ir para Relatorios"),
            ("Esc", "Voltar ao Dashboard"),
        ]

        for tecla, desc in atalhos:
            linha = ctk.CTkFrame(inner2, fg_color="transparent")
            linha.pack(fill="x", pady=SPACING_XS)
            ctk.CTkLabel(
                linha,
                text=tecla,
                font=ctk.CTkFont(size=FONT_LABEL, weight="bold"),
                text_color=self.colors.get("primary", "#6c5ce7"),
                width=80,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                linha,
                text=desc,
                font=ctk.CTkFont(size=FONT_LABEL),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).pack(side="left", padx=(SPACING_SM, 0))

        sec_sobre = self._criar_card_frame(container)
        sec_sobre.grid(row=2, column=0, sticky="ew", pady=(0, SPACING_MD))
        inner3 = ctk.CTkFrame(sec_sobre, fg_color="transparent")
        inner3.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)

        self._criar_label(
            inner3,
            f"{ICONS['info']}  Sobre",
            font=ctk.CTkFont(size=FONT_SECTION, weight="bold"),
            text_color=self.colors.get("text", "#f0f0f8"),
        ).pack(anchor="w")

        self._criar_label(
            inner3,
            f"FinancePro v{__version__} - Controle Financeiro Pessoal",
            font=ctk.CTkFont(size=FONT_LABEL),
        ).pack(anchor="w", pady=(SPACING_XS, 0))

        self._criar_label(
            inner3,
            "Gerencie suas receitas, despesas, investimentos e metas financeiras.",
            font=ctk.CTkFont(size=FONT_LABEL),
            text_color=self.colors.get("text_dim", "#606078"),
        ).pack(anchor="w", pady=(SPACING_XS, 0))

    def _exportar_backup(self):
        try:
            downloads = os.path.expanduser("~/Downloads")
            os.makedirs(downloads, exist_ok=True)
            filename = f"financeiro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            filepath = os.path.join(downloads, filename)
            shutil.copy2(str(DB_PATH), filepath)
            mostrar_toast(self, f"Backup exportado: {filename}", "sucesso")
        except Exception as e:
            mostrar_toast(self, f"Erro ao exportar backup: {e}", "erro")

    def _importar_backup(self):
        try:
            from tkinter import filedialog

            filepath = filedialog.askopenfilename(
                title="Selecionar backup",
                filetypes=[("SQLite Database", "*.db"), ("Todos os arquivos", "*.*")],
            )
            if not filepath:
                return

            try:
                test_conn = sqlite3.connect(filepath)
                integrity = test_conn.execute("PRAGMA integrity_check").fetchone()[0]
                if integrity != "ok":
                    mostrar_toast(self, "Arquivo corrompido! Integrity check falhou.", "erro")
                    test_conn.close()
                    return

                tables = [
                    r[0]
                    for r in test_conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                ]
                required = {"categorias", "receitas", "despesas", "investimentos"}
                if not required.issubset(set(tables)):
                    missing = required - set(tables)
                    mostrar_toast(self, f"Tabelas faltando: {', '.join(missing)}", "erro")
                    test_conn.close()
                    return

                test_conn.close()
            except Exception as e:
                mostrar_toast(self, f"Arquivo invalido: {e}", "erro")
                return

            backup_path = str(DB_PATH) + ".backup"
            shutil.copy2(str(DB_PATH), backup_path)

            shutil.copy2(filepath, str(DB_PATH))
            mostrar_toast(self, "Backup importado com sucesso! Reinicie o app.", "sucesso")
        except Exception as e:
            mostrar_toast(self, f"Erro ao importar backup: {e}", "erro")
