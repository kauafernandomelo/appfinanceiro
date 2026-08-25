from datetime import datetime


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data: str) -> str:
    try:
        dt = datetime.strptime(data, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return data


def obter_mes_atual() -> str:
    return datetime.now().strftime("%Y-%m")


def obter_data_atual() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def parse_data_br(data_br: str) -> str:
    try:
        dt = datetime.strptime(data_br, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return data_br
