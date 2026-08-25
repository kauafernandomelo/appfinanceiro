from components.lancamento_view import LancamentoView


class ReceitasView(LancamentoView):
    TIPO = "receita"
    TITULO = "Receitas"
    COR = "#00b894"
    COR_HOVER = "#00a884"
    CATEGORIA_TIPO = "receita"
    ICONE = "💰"
