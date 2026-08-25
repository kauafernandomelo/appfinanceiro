from dataclasses import dataclass


@dataclass
class Categoria:
    id: int | None = None
    nome: str = ""
    cor: str = "#3B82F6"
    tipo: str = "despesa"


@dataclass
class Receita:
    id: int | None = None
    descricao: str = ""
    valor: float = 0.0
    data: str = ""
    categoria_id: int | None = None


@dataclass
class Despesa:
    id: int | None = None
    descricao: str = ""
    valor: float = 0.0
    data: str = ""
    categoria_id: int | None = None


@dataclass
class Orcamento:
    id: int | None = None
    categoria_id: int = 0
    limite: float = 0.0
    mes: str = ""


@dataclass
class Meta:
    id: int | None = None
    nome: str = ""
    valor_alvo: float = 0.0
    valor_atual: float = 0.0
    prazo: str = ""


@dataclass
class Recorrente:
    id: int | None = None
    descricao: str = ""
    valor: float = 0.0
    tipo: str = "despesa"
    categoria_id: int | None = None
    dia_mes: int = 1
    ativo: bool = True
