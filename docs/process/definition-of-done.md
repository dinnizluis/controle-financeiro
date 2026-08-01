# Definition of Done

A feature is done when:

1. A GitHub Issue refined with the INVEST checklist and a versioned Spec Kit artifact under `specs/`
   exist and reference each other.
2. `spec.md` has reviewed Gherkin acceptance scenarios, UI-flow and regression-test mapping,
   business rules, edge cases, data impact, and scope.
3. `plan.md` and `tasks.md` match the accepted spec; `/speckit.analyze` found no unresolved mismatch.
4. Implementation matches the scope and includes deterministic tests for changed business rules.
5. `/speckit.converge` has no remaining work for the delivery.
6. Local validation and the `quality` GitHub Actions workflow pass.
7. The risk-first checklist is complete for any financial-data, cycle, summary, or history change.
8. The pull request records the validation evidence and is reviewed before merge.