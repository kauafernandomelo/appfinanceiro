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

## v4.0 - Production-Grade

### Bugs Criticos Corrigidos
- **conn.commit()** - Dados agora persistem corretamente em todas as operacoes
- **Backup validation** - Arquivos importados sao validados antes de substituir o banco
- **Ctrl+Shift+C** - Atalho para Recorrentes nao sobrescreve mais o Copy do sistema
- **Tooltip cleanup** - Janelas Toplevel sao destruidas corretamente (sem memory leak)
- **WAL mode** - SQLite com journal_mode=WAL e busy_timeout=5000

### Arquitetura DRY
- **LancamentoView** - Classe base generica para receitas/despesas (reduz 600+ linhas de duplicacao)
- **EvolucaoTemporalChart** - Componente compartilhado entre dashboard e relatorios
- **Constants centralizadas** - Cores, meses, versao em um unico lugar
- **Dead code removido** - models.py e services/ nao utilizados foram removidos

### Seguranca e Confiabilidade
- **Logging estruturado** - Erros salvos em logs/financeiro.log
- **Migracao de banco** - Sistema de versionamento com db_version
- **Versao unica** - __version__ = "4.0.0" em constants.py
- **Validacao de valores** - Rejeita valores negativos em receitas/despesas
- **Exception types** - sqlite3.Error e ValueError em vez de Exception generica

### Performance
- **Filtro em SQL** - WHERE + LIKE + LIMIT/OFFSET no banco (nao carrega tudo na memoria)
- **Uma conexao por operacao** - Dashboard usa queries agregadas em vez de N+1
- **matplotlib cleanup** - Figure.clear() + del canvas para evitar memory leak

### Testes
- **61 testes** passando (era 26)
- **test_parcelas.py** - 12 testes de calculo de parcelas
- **test_recorrentes.py** - 13 testes de logica de recorrentes
- **test_integration.py** - 10 testes de integracao (commit, rollback, cascade, WAL)

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
| Ctrl+Shift+C | Ir para Recorrentes |
| Ctrl+T | Ir para Configuracoes |
| Ctrl+L | Ir para Relatorios |
| Esc | Voltar ao Dashboard |

## Tecnologias

- **Python 3.11+**
- **CustomTkinter** - Interface grafica moderna
- **Matplotlib** - Geracao de graficos
- **ReportLab** - Exportacao PDF
- **SQLite** - Armazenamento local de dados (WAL mode)

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
├── main.py                     # Ponto de entrada
├── database.py                 # Conexao SQLite (WAL mode)
├── constants.py                # Constantes centralizadas
├── enums.py                    # Enums de tipos
├── logger.py                   # Logging estruturado
├── utils.py                    # Funcoes auxiliares
├── views/
│   ├── dashboard.py            # Tela principal
│   ├── receitas.py             # Subclass de LancamentoView
│   ├── despesas.py             # Subclass de LancamentoView
│   ├── investimentos.py        # Gerenciamento de investimentos
│   ├── categorias.py           # Gerenciamento de categorias
│   ├── orcamento.py            # Controle de orcamento
│   ├── metas.py                # Metas de economia
│   ├── recorrentes.py          # Contas recorrentes
│   ├── relatorios.py           # Relatorios
│   └── configuracoes.py        # Backup/Restore e configs
├── components/
│   ├── base_view.py            # Classe base para views
│   ├── lancamento_view.py      # View generica CRUD
│   ├── evolucao_chart.py       # Grafico de evolucao temporal
│   ├── sidebar.py              # Menu lateral
│   ├── charts.py               # Graficos
│   ├── datepicker.py           # Seletor de data
│   ├── modals.py               # Janelas modais
│   ├── toast.py                # Notificacoes
│   └── tooltip.py              # Dicas
├── tests/
│   ├── test_utils.py           # Testes de utilitarios
│   ├── test_database.py        # Testes de banco
│   ├── test_parcelas.py        # Testes de parcelas
│   ├── test_recorrentes.py     # Testes de recorrentes
│   └── test_integration.py     # Testes de integracao
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD com GitHub Actions
├── pyproject.toml              # Configuracao de lint/testes
└── requirements.txt            # Dependencias
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
