# Controle Financeiro

Aplicacao pessoal de planejamento financeiro mensal, desenvolvida em Python, Streamlit,
SQLAlchemy e SQLite. O projeto usa um **Agentic Development Life Cycle (ADLC)** baseado em
Spec Kit e GitHub Copilot: cada entrega nasce de um escopo de usuario, passa por backlog,
especificacao e testes, e so entao chega a implementacao e revisao.

## Inicio Rapido

### Requisitos

- Python 3.11 ou 3.12
- Git
- GitHub CLI (`gh`) autenticado, para criar Issues pelo fluxo de refinamento

### Instalar e executar

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/streamlit run streamlit_app.py
```

Abra a URL exibida pelo Streamlit. Por padrao, os dados locais sao armazenados em
`data/controle_financeiro.db`.

Para executar a interface com outro banco SQLite, inclusive em testes:

```bash
CONTROLE_FINANCEIRO_DB_PATH=/caminho/para/budget.sqlite .venv/bin/streamlit run streamlit_app.py
```

## Comece Por Aqui

1. Leia a [Constituicao do Projeto](.specify/memory/constitution.md). Ela define as regras que
	 nao podem ser flexibilizadas: integridade financeira, `Decimal`, ciclos, locks e testes.
2. Leia o [Fluxo de IA](docs/process/ai-workflow.md) para entender a sequencia completa e os pontos de
	 aprovacao humana.
3. Para uma nova funcionalidade, abra o chat do Copilot no repositorio e execute
	 [`/speckit.refine`](.github/prompts/speckit.refine.prompt.md) com o escopo informado pelo
	 usuario.
4. Use a [Definition of Done](docs/process/definition-of-done.md), a
	[Checklist de Aceite](docs/process/acceptance-checklist.md) e a
	 [Checklist de Revisao por Risco](docs/review/risk-first-review-checklist.md) antes de aprovar
	 uma entrega.

## Ciclo Agentico de Desenvolvimento

```mermaid
flowchart LR
		A[Escopo do usuario] --> B[Refinar backlog]
		B --> C[GitHub Issue INVEST]
		C --> D[Especificar]
		D --> E[Clarificar se necessario]
		E --> F[Planejar]
		F --> G[Gerar tarefas]
		G --> H[Analisar consistencia]
		H --> I[Implementar]
		I --> J[Convergir e revisar]
		J --> K[Pull request e gates]
```

| Etapa | Comando no Copilot | Resultado esperado | Referencia |
|-------|--------------------|-------------------|------------|
| Refinar backlog | [`/speckit.refine`](.github/prompts/speckit.refine.prompt.md) | Historia INVEST, cenarios Gherkin, mapa de fluxo UI e cobertura; Issue aprovada | [Agente](.github/agents/speckit.refine.agent.md) |
| Especificar | [`/speckit.specify`](.github/prompts/speckit.specify.prompt.md) | `specs/<numero>-<feature>/spec.md` com escopo, regras e cenarios | [Template de spec](.specify/templates/spec-template.md) |
| Clarificar | [`/speckit.clarify`](.github/prompts/speckit.clarify.prompt.md) | Decisoes ambiguas registradas na spec | [Agente](.github/agents/speckit.clarify.agent.md) |
| Planejar | [`/speckit.plan`](.github/prompts/speckit.plan.prompt.md) | Plano tecnico e estrategia de regressao por cenario | [Template de plano](.specify/templates/plan-template.md) |
| Quebrar em tarefas | [`/speckit.tasks`](.github/prompts/speckit.tasks.prompt.md) | `tasks.md` ordenado, com testes `[DOMAIN]`, `[PERSISTENCE]`, `[UI]` ou `[PROPERTY]` | [Template de tarefas](.specify/templates/tasks-template.md) |
| Analisar | [`/speckit.analyze`](.github/prompts/speckit.analyze.prompt.md) | Divergencias entre spec, plano e tarefas resolvidas | [Agente](.github/agents/speckit.analyze.agent.md) |
| Implementar | [`/speckit.implement`](.github/prompts/speckit.implement.prompt.md) | Tarefas implementadas em fatias pequenas e verificaveis | [Agente](.github/agents/speckit.implement.agent.md) |
| Convergir | [`/speckit.converge`](.github/prompts/speckit.converge.prompt.md) | Pendencias encontradas viram tarefas antes da entrega | [Agente](.github/agents/speckit.converge.agent.md) |

Os comandos sao arquivos versionados do repositorio. No VS Code, digite `/` no chat e selecione o
comando; os links acima mostram as instrucoes completas que o Copilot executa.

## Regras do Fluxo

- Comece cada feature com `/speckit.refine`, nunca pela implementacao.
- O refinamento so cria uma Issue depois de mostrar o corpo completo e receber confirmacao
	explicita. Sem `gh` autenticado, ele salva o conteudo aprovado em `backlog/<slug>.md`.
- Cada Issue deve ter uma historia de usuario INVEST, cenarios Gherkin e uma matriz
	`cenario -> camada de teste -> arquivo planejado`.
- `specs/` e a fonte de verdade para features novas. Os arquivos em `docs/history/feature-specs/` sao registros
	historicos.
- `/speckit.taskstoissues` nao faz parte do fluxo normal: `tasks.md` e o registro detalhado de
	execucao. Use-o apenas quando a equipe decidir dividir uma entrega em varias Issues.
- Copilot pode elaborar, planejar, implementar e revisar; uma pessoa aprova regras financeiras,
	impacto em dados, testes e merge.

## Estrategia de Testes

As regras de dinheiro, datas, ciclos, locks e resumos recebem testes deterministas com pytest.
Persistencia usa SQLite temporario. Fluxos Streamlit e estados visiveis usam
`streamlit.testing.v1.AppTest`. Invariantes de alto valor podem usar Hypothesis.

O guia [Testes de Regressao](docs/process/regression-testing.md) descreve como mapear um cenario Gherkin
para a camada e o arquivo de teste corretos. O exemplo inicial esta em
[tests/test_ui_regression.py](tests/test_ui_regression.py).

## Validacao Local

Execute antes de abrir ou atualizar um pull request:

```bash
.venv/bin/python -m pytest -q --cov=controle_financeiro --cov-report=term-missing
.venv/bin/python -m ruff format --check .
.venv/bin/python -m ruff check .
.venv/bin/python -m pyright
.venv/bin/python -m pip_audit
```

O workflow [quality.yml](.github/workflows/quality.yml) executa os mesmos gates em pull requests
e em pushes para `development`. A [configuracao do Dependabot](.github/dependabot.yml) mantem
dependencias Python e GitHub Actions sob revisao semanal.

## Estrutura do Repositorio

```text
.github/                 Comandos Copilot, templates e automacao de CI
.specify/                Constituicao, scripts e templates do Spec Kit
docs/                    Processo, historico, revisao e planos de evolucao
specs/                   Especificacoes versionadas por feature e planos amplos de evolucao
src/controle_financeiro/ Dominio, servicos, persistencia e interface Streamlit
tests/                   Testes de contrato e regressao de UI
```

## Referencias Operacionais

- [Mapa da Documentacao](docs/README.md)
- [Fluxo de IA](docs/process/ai-workflow.md)
- [Constituicao do Projeto](.specify/memory/constitution.md)
- [Definition of Done](docs/process/definition-of-done.md)
- [Checklist de Aceite](docs/process/acceptance-checklist.md)
- [Checklist de Revisao por Risco](docs/review/risk-first-review-checklist.md)
- [Testes de Regressao](docs/process/regression-testing.md)
- [Planos de Evolucao](docs/evolution/README.md)
- [Template de Issue de Feature](.github/ISSUE_TEMPLATE/feature.md)
- [Template de Pull Request](.github/pull_request_template.md)

