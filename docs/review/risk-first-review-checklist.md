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
- Validate scope against [docs/issues/001-data-model-spec.md](../issues/001-data-model-spec.md).
- Confirm no out-of-scope behavior was introduced.

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
- Log missing scenarios as explicit test tasks.

## Minimum Commands

```bash
pytest -q
ruff check .
```

## Review Output Template

Use this structure for every review note:

- Severity: `critical|high|medium|low`
- Rule: short business rule statement
- Evidence: implementation pointer + test pointer
- Risk: what can break in production
- Action: fix or test to add