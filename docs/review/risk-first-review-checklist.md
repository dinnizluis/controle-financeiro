# Risk-First Review Checklist

## Objective

Review AI-generated code quickly without sacrificing behavioral confidence.

## Severity Order

1. Critical correctness and data integrity.
2. Business-rule drift from spec.
3. Regression risk due to weak tests.
4. Maintainability and coupling.

## Step-by-Step Pass

1. Spec Alignment
- Validate scope against the linked `specs/<number>-<feature>/spec.md` and GitHub Issue.
- Confirm no out-of-scope behavior was introduced.
- Confirm `/speckit.analyze` and `/speckit.converge` have no unresolved finding.

2. Lock and Lifecycle Integrity
- Verify update lock behavior at boundary dates.
- Check that lock errors are explicit and user-visible.

3. Monetary and Date Consistency
- Validate Decimal normalization and DB precision.
- Validate cycle boundary calculations and assumptions.

4. History and Current-State Semantics
- Verify duplicate weekly check-ins preserve history.
- Verify only intended rows are current for projections.

5. Summary Determinism
- Verify projected margin formulas for open vs closed cycle.
- Verify status mapping is deterministic and tested.

6. Testing Adequacy
- Confirm each critical rule has at least one test.
- Confirm changed rules have deterministic tests before relying on generated cases.
- Confirm every Gherkin scenario has a matching regression-map row and implemented test evidence.
- Confirm each changed Streamlit flow has AppTest coverage for its visible success, empty, or error
  state. Keep financial calculations and lock rules covered at domain or persistence level.
- Use Hypothesis only for domain or persistence invariants such as money normalization, cycle
	boundaries, and locks.
- Log missing scenarios as explicit test tasks.

7. Automated Gates
- Confirm the `quality` workflow is green.
- Review type-check and dependency-audit output; document any accepted exception.

## Minimum Commands

```bash
pytest -q
pytest -q --cov=controle_financeiro --cov-report=term-missing
ruff format --check .
ruff check .
pyright
pip-audit
```

## Review Output Template

Use this structure for every review note:

- Severity: `critical|high|medium|low`
- Rule: short business rule statement
- Evidence: implementation pointer + test pointer
- Risk: what can break in production
- Action: fix or test to add