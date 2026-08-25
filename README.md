# FinancePro - Controle Financeiro

Aplicativo desktop para controle financeiro pessoal desenvolvido em Python com interface moderna usando CustomTkinter.

## Funcionalidades

- **Dashboard** - Visao geral com saldo, receitas e despesas do mes, navegacao por mes e grafico de evolucao temporal
- **Receitas** - CRUD com busca, filtro por categoria, paginacao e suporte a parcelas
- **Despesas** - CRUD com busca, filtro por categoria, paginacao e suporte a parcelas
- **Investimentos** - Gerenciamento de investimentos com tipos e calculo de lucro/prejuizo
- **Categorias** - Organizacao por categorias com cores personalizadas e protecao contra exclusao
- **Orcamento Mensal** - Definicao de limites por categoria com indicador visual e alertas
- **Metas de Economia** - Acompanhamento de objetivos com adicao de valor inline
- **Contas Recorrentes** - Lancamentos mensais com geracao automatica
- **Relatorios** - Analise por periodo com graficos, exportacao PDF e CSV
- **Configuracoes** - Backup/Restore, atalhos de teclado e informacoes do app

## v5.0 - Dark Premium UI

### Design Visual
- **Dark Premium Theme** - Paleta escura elegante com bordas sutis e elevacao
- **Cards com borda** - Border sutil em todos os cards para profundidade visual
- **Linhas alternadas** - Zebra-striping em todas as listas
- **Hover effects** - Mudanca de cor ao passar o mouse nas linhas
- **Botoes padronizados** - Primary (roxo), positive (verde), negative (vermelho)
- **Tipografia consistente** - Escala de fontes: 24, 16, 13, 12, 11, 10
- **Espacamento 4px grid** - Todos os espacos sao multiplos de 4

### Componentes Novos
- **PaginationBar** - Paginacao reutilizavel com setas e info de registros
- **EmptyState** - Componente para listas vazias com icone e texto
- **StatusBadge** - Badge colorido para status (Receita/Despesa/Ativo/Inativo)

### Sidebar Redesenhada
- **Icones Unicode consistentes** - Substituem emojis por caracteres monospace
- **Separadores de secao** - Grupos visuais no menu
- **Indicador ativo** - Fundo destacado no item selecionado
- **Logo "FP"** - Estilizado em vez de "$"

### Melhorias de Layout
- **Dashboard cards** - 105px altura, 4px linha colorida no topo
- **Progress bars** - 12px altura (era 8px)
- **Botoes de acao** - 32x32px (era 26x26)
- **Formularios** - Max 4 colunas por linha
- **Labels** - 12px com cor secundaria

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
- **SQLite** - Armazenamento local (WAL mode)

## Instalacao

1. Clone o repositorio:
```bash
git clone https://github.com/kauafernandomelo/appfinanceiro.git
cd appfinanceiro
```

2. Instale as dependencias:
```bash
pip install -r requirements.txt
```

3. Execute:
```bash
python main.py
```

## Estrutura do Projeto

```
appfinanceiro/
├── main.py
├── database.py
├── constants.py
├── enums.py
├── logger.py
├── utils.py
├── views/
│   ├── dashboard.py
│   ├── receitas.py
│   ├── despesas.py
│   ├── investimentos.py
│   ├── categorias.py
│   ├── orcamento.py
│   ├── metas.py
│   ├── recorrentes.py
│   ├── relatorios.py
│   └── configuracoes.py
├── components/
│   ├── base_view.py
│   ├── lancamento_view.py
│   ├── evolucao_chart.py
│   ├── pagination.py
│   ├── empty_state.py
│   ├── sidebar.py
│   ├── charts.py
│   ├── datepicker.py
│   ├── modals.py
│   ├── toast.py
│   └── tooltip.py
├── tests/
│   ├── test_utils.py
│   ├── test_database.py
│   ├── test_parcelas.py
│   ├── test_recorrentes.py
│   └── test_integration.py
└── pyproject.toml
```

## Status

[![CI](https://github.com/kauafernandomelo/appfinanceiro/actions/workflows/ci.yml/badge.svg)](https://github.com/kauafernandomelo/appfinanceiro/actions/workflows/ci.yml)

## Licenca

MIT License
