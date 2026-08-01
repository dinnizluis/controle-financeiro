# Tasks: Authenticated Published Access

**Input**: Design documents from `/specs/002-authenticated-published-access/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Focused regression coverage only for password gate behavior.

**MVP-0 Scope**: Single shared password gate from `st.secrets`, block any financial initialization before unlock, fail-closed when secret is missing/invalid, and no logout flow.

**Out of Scope**: OIDC login, allowlist (subject/email), logout, token expiration, schema/data migration, extra architecture modules, property-based testing.

## Phase 1: Password Gate MVP-0

**Purpose**: Entregar bloqueio simples e rapido para impedir acesso publico aos dados.

- [ ] T001 Add password gate test doubles and session-state helpers in `tests/conftest.py`
- [ ] T002 Add locked/unlocked minimal UI regressions in `tests/test_ui_auth_access.py`
- [ ] T003 Implement single password gate from `st.secrets` and move `get_service()` behind unlocked-only branch in `src/controle_financeiro/app.py`
- [ ] T004 Update MVP-0 validation notes (password setup + manual check) in `specs/002-authenticated-published-access/quickstart.md`

---

## Dependencies & Execution Order

### Phase Order

1. T001 -> T002 -> T003 -> T004

### Dependency Notes

1. T003 depends on test harness and regressions (T001-T002).
2. T004 depends on final behavior after T003.

---

## Implementation Strategy

### Suggested MVP-0 Delivery

1. Implementar gate por senha unica e bloquear inicializacao de servico antes do unlock.
2. Validar locked/unlocked sem OIDC e sem logout.
3. Publicar com segredo forte e revisao manual basica.

### Scope Enforcement

1. Do not add OIDC logic in this slice.
2. Do not add allowlist logic in this slice.
3. Do not add logout/session lifecycle in this slice.
4. Do not add data/schema migration work.

---

## Complexity Heuristic (MVP)

Heuristica usada por task:

- `B` (Blast Radius): 1=arquivo local, 2=arquivo central de fluxo, 3=impacto transversal
- `U` (Unknowns): 1=baixo risco tecnico, 2=medio, 3=alto
- `T` (Test Load): 1=teste simples, 2=multiplos cenarios, 3=cenario com alta friccao
- **Score** = `B + U + T` (min=3, max=9)

Bandas:

- **XS**: 3-4 (~0.25-0.5 dia)
- **S**: 5-6 (~0.5-1 dia)
- **M**: 7-8 (~1-2 dias)
- **L**: 9 (>2 dias)

| Task | B | U | T | Score | Size | Worst-case |
|------|---|---|---|-------|------|------------|
| T001 | 1 | 1 | 1 | 3 | XS | 0.25d |
| T002 | 1 | 1 | 2 | 4 | XS | 0.5d |
| T003 | 2 | 1 | 1 | 4 | XS | 0.5d |
| T004 | 1 | 1 | 1 | 3 | XS | 0.25d |

**Feature aggregate (MVP-0)**:

- Soma dos scores: **14**
- Complexidade media por task: **3.5 (XS)**
- Caminho critico (T001 -> T002 -> T003 -> T004): **~1.5 dias uteis**
- Worst-case consolidado da feature (com folga de integracao): **~1 dia util**
