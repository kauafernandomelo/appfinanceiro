"""Constantes centralizadas do FinancePro - Dark Premium Theme."""

__version__ = "5.0.0"

# === DARK PREMIUM THEME ===
COLORS_DEFAULTS = {
    # Backgrounds (levels de profundidade)
    "bg_dark": "#0d0d1a",
    "bg_card": "#161630",
    "bg_elevated": "#1e1e3a",
    "bg_hover": "#252550",

    # Accent colors (apenas 3 principais)
    "primary": "#6c5ce7",
    "primary_hover": "#5a4bd1",
    "primary_muted": "#3d3580",

    # Status colors
    "positive": "#00b894",
    "positive_muted": "#00875f",
    "negative": "#d63031",
    "negative_muted": "#a32525",
    "warning": "#fdcb6e",
    "warning_muted": "#c49a3e",

    # Neutrals
    "text": "#f0f0f8",
    "text_secondary": "#a0a0b8",
    "text_dim": "#606078",

    # Borders
    "border": "#2a2a48",
    "border_light": "#353560",
    "border_focus": "#6c5ce7",

    # Sidebar
    "sidebar_bg": "#12122a",
    "sidebar_active_bar": "#6c5ce7",
}

# Backward compatibility aliases
COLORS_DEFAULTS["green"] = COLORS_DEFAULTS["positive"]
COLORS_DEFAULTS["green_hover"] = COLORS_DEFAULTS["positive_muted"]
COLORS_DEFAULTS["red"] = COLORS_DEFAULTS["negative"]
COLORS_DEFAULTS["red_hover"] = COLORS_DEFAULTS["negative_muted"]
COLORS_DEFAULTS["yellow"] = COLORS_DEFAULTS["warning"]
COLORS_DEFAULTS["yellow_hover"] = COLORS_DEFAULTS["warning_muted"]

LIGHT_COLORS_DEFAULTS = {
    "bg_dark": "#f5f5fa",
    "bg_card": "#ffffff",
    "bg_elevated": "#f0f0f8",
    "bg_hover": "#e8e8f2",
    "primary": "#6c5ce7",
    "primary_hover": "#5a4bd1",
    "primary_muted": "#c4bffc",
    "positive": "#009874",
    "positive_muted": "#b2dfdb",
    "negative": "#c0392b",
    "negative_muted": "#f8d7da",
    "warning": "#d4a017",
    "warning_muted": "#fff3cd",
    "text": "#1a1a2e",
    "text_secondary": "#555570",
    "text_dim": "#888898",
    "border": "#d0d0e0",
    "border_light": "#e0e0f0",
    "border_focus": "#6c5ce7",
    "sidebar_bg": "#ffffff",
    "sidebar_active_bar": "#6c5ce7",
}
LIGHT_COLORS_DEFAULTS["green"] = LIGHT_COLORS_DEFAULTS["positive"]
LIGHT_COLORS_DEFAULTS["green_hover"] = LIGHT_COLORS_DEFAULTS["positive_muted"]
LIGHT_COLORS_DEFAULTS["red"] = LIGHT_COLORS_DEFAULTS["negative"]
LIGHT_COLORS_DEFAULTS["red_hover"] = LIGHT_COLORS_DEFAULTS["negative_muted"]
LIGHT_COLORS_DEFAULTS["yellow"] = LIGHT_COLORS_DEFAULTS["warning"]
LIGHT_COLORS_DEFAULTS["yellow_hover"] = LIGHT_COLORS_DEFAULTS["warning_muted"]

# === SPACING (4px grid) ===
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 16
SPACING_XL = 20
SPACING_2XL = 24
SPACING_3XL = 32

# === TYPOGRAPHY ===
FONT_TITLE = 24
FONT_SECTION = 16
FONT_CARD_TITLE = 13
FONT_BODY = 12
FONT_LABEL = 12
FONT_SMALL = 11
FONT_CAPTION = 10

# === LAYOUT ===
ITENS_POR_PAGINA = 15
CARD_CORNER_RADIUS = 12
BUTTON_CORNER_RADIUS = 8
ROW_HEIGHT = 48
ACTION_BUTTON_SIZE = 32
DASHBOARD_CARD_HEIGHT = 105
PROGRESS_BAR_HEIGHT = 12

# === ICONS (Unicode consistent) ===
ICONS = {
    "dashboard": "\u25A0",
    "receitas": "\u25B2",
    "despesas": "\u25BC",
    "investimentos": "\u25C6",
    "categorias": "\u25CF",
    "orcamento": "\u2610",
    "metas": "\u25CE",
    "recorrentes": "\u21BB",
    "relatorios": "\u25A1",
    "configuracoes": "\u2699",
    "edit": "\u270E",
    "delete": "\u2716",
    "add": "\u271A",
    "search": "\u2315",
    "prev": "\u25C0",
    "next": "\u25B6",
    "close": "\u2715",
    "chart": "\u2581",
    "check": "\u2714",
    "warning": "\u26A0",
    "info": "\u2139",
    "calendar": "\u25B4",
    "menu": "\u2261",
    "moon": "\u263E",
    "sun": "\u2600",
    "logo": "FP",
}

# === MONTHS ===
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

MESES_ABREV = {
    1: "Jan", 2: "Fev", 3: "Mar",
    4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set",
    10: "Out", 11: "Nov", 12: "Dez",
}

MAX_PARCELAS = 120
DB_VERSION = 2
