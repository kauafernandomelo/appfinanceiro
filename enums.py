from enum import StrEnum


class TipoLancamento(StrEnum):
    RECEITA = "receita"
    DESPESA = "despesa"


class TipoInvestimento(StrEnum):
    ACAO = "Acao"
    FII = "FII"
    TESOURO_DIRETO = "Tesouro Direto"
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    POUPANCA = "Poupanca"
    CRYPTO = "Crypto"
    FOREX = "Forex"
    FIXA = "Renda Fixa"
    VARIAVEL = "Renda Variavel"
    OUTROS = "Outros"


MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro",
}
