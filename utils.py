from datetime import datetime


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data: str) -> str:
    try:
        return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data


def obter_mes_atual() -> str:
    return datetime.now().strftime("%Y-%m")


def obter_data_atual() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def parse_data_br(data_br: str) -> str:
    try:
        return datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return data_br


def validar_data(data: str) -> bool:
    try:
        datetime.strptime(data, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validar_valor(valor: str) -> bool:
    try:
        float(valor.replace(",", "."))
        return True
    except (ValueError, AttributeError):
        return False


def formatar_percentual(valor: float) -> str:
    """Formata um valor como percentual: 85.5 -> '85,5%'"""
    return f"{valor:.1f}%".replace(".", ",")


def parse_valor(valor: str) -> float:
    """Converte string de valor para float."""
    return float(valor.replace(",", "."))
