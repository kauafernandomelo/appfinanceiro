# Controle Financeiro

Aplicativo desktop para controle financeiro pessoal desenvolvido em Python com interface moderna usando CustomTkinter.

## Funcionalidades

- **Dashboard** - Visão geral com saldo, receitas e despesas do mês
- **Receitas** - Cadastro e gerenciamento de entradas financeiras
- **Despesas** - Cadastro e gerenciamento de saídas financeiras
- **Categorias** - Organização por categorias com cores personalizadas
- **Orçamento Mensal** - Definição de limites por categoria com indicador visual
- **Metas de Economia** - Acompanhamento de objetivos financeiros
- **Contas Recorrentes** - Lançamentos que se repetem mensalmente
- **Relatórios** - Análise detalhada por período com gráficos

## Tecnologias

- **Python 3.11+**
- **CustomTkinter** - Interface gráfica moderna
- **Matplotlib** - Geração de gráficos
- **SQLite** - Armazenamento local de dados

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/kauafernandomelo/appfinanceiro.git
cd appfinanceiro
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o aplicativo:
```bash
python main.py
```

## Estrutura do Projeto

```
appfinanceiro/
├── main.py                 # Ponto de entrada
├── database.py             # Conexão e migrations do SQLite
├── models.py               # Modelos de dados
├── utils.py                # Funções auxiliares
├── views/
│   ├── dashboard.py        # Tela principal
│   ├── receitas.py         # Gerenciamento de receitas
│   ├── despesas.py         # Gerenciamento de despesas
│   ├── categorias.py       # Gerenciamento de categorias
│   ├── orcamento.py        # Controle de orçamento
│   ├── metas.py            # Metas de economia
│   ├── recorrentes.py      # Contas recorrentes
│   └── relatorios.py       # Relatórios
├── components/
│   ├── sidebar.py          # Menu lateral
│   ├── charts.py           # Gráficos
│   └── modals.py           # Janelas modais
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD com GitHub Actions
└── requirements.txt        # Dependências
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adicionar nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Status do Projeto

[![CI](https://github.com/kauafernandomelo/appfinanceiro/actions/workflows/ci.yml/badge.svg)](https://github.com/kauafernandomelo/appfinanceiro/actions/workflows/ci.yml)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
