from components.lancamento_view import LancamentoView


class DespesasView(LancamentoView):
    TIPO = "despesa"
    TITULO = "Despesas"
    COR = "#d63031"
    COR_HOVER = "#c0392b"
    CATEGORIA_TIPO = "despesa"
    ICONE = "💸"
