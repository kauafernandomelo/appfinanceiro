import os
import shutil
from datetime import datetime

import customtkinter as ctk

from components.base_view import BaseView
from components.toast import mostrar_toast
from database import DB_PATH


class ConfiguracoesView(BaseView):
    """View de configuracoes gerais do aplicativo."""

    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(1, weight=1)
        self._criar_header()
        self._criar_conteudo()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Configuracoes").pack(side="left")

    def _criar_conteudo(self):
        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=self.colors.get("border", "#2d2d44"),
        )
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        sec_backup = self._criar_card_frame(container)
        sec_backup.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        inner = ctk.CTkFrame(sec_backup, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=16)

        self._criar_label(inner, "Backup e Restauracao", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self._criar_label(inner, "Exporte ou importe seus dados financeiros.", font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0b0")).pack(anchor="w", pady=(4, 12))

        btns_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btns_frame.pack(fill="x")

        ctk.CTkButton(
            btns_frame, text="Exportar Backup", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("green", "#00b894"), hover_color="#00a884",
            command=self._exportar_backup,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btns_frame, text="Importar Backup", height=36, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("yellow", "#fdcb6e"), hover_color="#f0b840",
            text_color="#000000",
            command=self._importar_backup,
        ).pack(side="right", expand=True, fill="x", padx=(6, 0))

        sec_atalhos = self._criar_card_frame(container)
        sec_atalhos.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        inner2 = ctk.CTkFrame(sec_atalhos, fg_color="transparent")
        inner2.pack(fill="x", padx=16, pady=16)

        self._criar_label(inner2, "Atalhos de Teclado", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

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
            linha.pack(fill="x", pady=2)
            ctk.CTkLabel(
                linha, text=tecla, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors.get("accent", "#00cec9"), width=80, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                linha, text=desc, font=ctk.CTkFont(size=12),
                text_color=self.colors.get("text_dim", "#a0a0b0"),
            ).pack(side="left", padx=(8, 0))

        sec_sobre = self._criar_card_frame(container)
        sec_sobre.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        inner3 = ctk.CTkFrame(sec_sobre, fg_color="transparent")
        inner3.pack(fill="x", padx=16, pady=16)

        self._criar_label(inner3, "Sobre", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self._criar_label(inner3, "FinancePro v3.0.0 - Controle Financeiro Pessoal",
                          font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(4, 0))
        self._criar_label(inner3, "Gerencie suas receitas, despesas, investimentos e metas financeiras.",
                          font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(2, 0))

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
            shutil.copy2(filepath, str(DB_PATH))
            mostrar_toast(self, "Backup importado com sucesso! Reinicie o app.", "sucesso")
        except Exception as e:
            mostrar_toast(self, f"Erro ao importar backup: {e}", "erro")
