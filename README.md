# FinancePro - Controle Financeiro

Aplicativo desktop para controle financeiro pessoal desenvolvido em Python com interface moderna usando CustomTkinter.

## Funcionalidades

- **Dashboard** - Visao geral com saldo, receitas e despesas do mes, navegacao por mes e grafico de evolucao temporal
- **Receitas** - CRUD com busca, filtro por categoria, paginacao e suporte a parcelas
- **Despesas** - CRUD com busca, filtro por categoria, paginacao e suporte a parcelas
- **Investimentos** - Gerenciamento de investimentos com tipos (Acao, FII, Crypto, etc) e calculo de lucro/prejuizo
- **Categorias** - Organizacao por categorias com cores personalizadas, busca e protecao contra exclusao
- **Orcamento Mensal** - Definicao de limites por categoria com indicador visual e alertas de uso
- **Metas de Economia** - Acompanhamento de objetivos financeiros com adicao de valor inline
- **Contas Recorrentes** - Lancamentos que se repetem mensalmente com geracao automatica
- **Relatorios** - Analise detalhada por periodo com graficos, exportacao PDF e CSV
- **Configuracoes** - Backup/Restore do banco, atalhos de teclado e informacoes do app

## Melhorias v3.0

- **Tema Dark/Light** - Alterne entre temas claro e escuro
- **Sidebar Colapsavel** - Minimize a sidebar para mostrar apenas icones
- **Busca e Filtros** - Busca por descricao e filtro por categoria em todas as listas
- **Paginacao** - Listas paginadas com 15 itens por pagina
- **Lancamentos Parcelados** - Divida compras em N parcelas mensais
- **Grafico de Evolucao Temporal** - Visualize receitas vs despesas nos ultimos 6 meses
- **Exportacao CSV** - Exporte relatorios em formato CSV
- **Backup/Restore** - Exporte e importe backups do banco de dados
- **Alertas de Orcamento** - Notificacoes quando o orcamento atinge 80% ou 100%
- **Tooltips** - Dicas em todos os botoes de acao
- **Icones Unicode** - Botoes de editar/excluir com icones visuais
- **Tratamento de Erros** - Mensagens de erro em todas as operacoes de banco
- **Anos Bissextos** - Calculo correto de dias para fevereiro
- **ON DELETE CASCADE** - Integridade referencial nas foreign keys
- **Enums** - Tipos como枚 em vez de strings

## Atalhos de Teclado

| Atalho | Acao |
|--------|------|
| Ctrl+N | Novo registro na view atual |
| Ctrl+R | Ir para Receitas |
| Ctrl+D | Ir para Despesas |
| Ctrl+I | Ir para Investimentos |
| Ctrl+B | Ir para Categorias |
| Ctrl+O | Ir para Orcamento |
| Ctrl+M | Ir para Metas |
| Ctrl+C | Ir para Recorrentes |
| Ctrl+T | Ir para Configuracoes |
| Ctrl+L | Ir para Relatorios |
| Esc | Voltar ao Dashboard |

## Tecnologias

- **Python 3.11+**
- **CustomTkinter** - Interface grafica moderna
- **Matplotlib** - Geracao de graficos
- **ReportLab** - Exportacao PDF
- **SQLite** - Armazenamento local de dados

## Instalacao

### Pre-requisitos

- Python 3.11 ou superior
- pip

### Passos

1. Clone o repositorio:
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

3. Instale as dependencias:
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
├── database.py             # Conexao e migrations do SQLite
├── models.py               # Modelos de dados
├── utils.py                # Funcoes auxiliares
├── enums.py                # Enums de tipos
├── pyproject.toml          # Configuracao de lint
├── views/
│   ├── dashboard.py        # Tela principal
│   ├── receitas.py         # Gerenciamento de receitas
│   ├── despesas.py         # Gerenciamento de despesas
│   ├── categorias.py       # Gerenciamento de categorias
│   ├── orcamento.py        # Controle de orcamento
│   ├── metas.py            # Metas de economia
│   ├── recorrentes.py      # Contas recorrentes
│   ├── relatorios.py       # Relatorios
│   └── configuracoes.py    # Configuracoes do app
├── components/
│   ├── base_view.py        # Classe base para views
│   ├── sidebar.py          # Menu lateral
│   ├── charts.py           # Graficos
│   ├── datepicker.py       # Seletor de data
│   ├── modals.py           # Janelas modais
│   ├── toast.py            # Notificacoes
│   └── tooltip.py          # Dicas
├── services/
│   └── receitas_repository.py  # Repository de receitas
├── tests/
│   ├── test_utils.py       # Testes de utilitarios
│   └── test_database.py    # Testes de banco
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD com GitHub Actions
└── requirements.txt        # Dependencias
```

## Contribuicao

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudancas (`git commit -m 'Adicionar nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Status do Projeto

[![CI](https://github.com/kauafernandomelo/appfinanceiro/actions/workflows/ci.yml/badge.svg)](https://github.com/kauafernandomelo/appfinanceiro/actions/workflows/ci.yml)

## Licenca

Este projeto esta sob a licenca MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
