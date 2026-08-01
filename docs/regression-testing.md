# Regression Testing

Every delivered Gherkin scenario has one row in the feature's **UI Flow and Regression Test
Map**. The row identifies the observable outcome, test layer, and planned test file before
implementation begins.

## Test Layers

| Layer | Use for | Tooling |
|-------|---------|---------|
| `domain` | Decimal normalization, dates, locks, summaries, and validation | pytest |
| `persistence` | Stored records, history, current-state semantics, and SQLite behavior | pytest + temporary SQLite database |
| `ui` | Streamlit forms, filters, visible tables, empty states, and errors | `streamlit.testing.v1.AppTest` + pytest |
| `property` | Invariants across generated values and boundary dates | Hypothesis + pytest |

## Gherkin Mapping

Use the Gherkin scenario title in the test name or docstring. Prefer one primary assertion path per
scenario, then add focused tests for important boundary or error paths.

```gherkin
Scenario: User sees empty fixed-cost guidance
  Given the selected cycle has no fixed costs
  When the user opens the fixed-cost tab
  Then the page shows empty-state guidance and a form to add a fixed cost
```

This maps to a UI regression test that creates a temporary SQLite database, sets
`CONTROLE_FINANCEIRO_DB_PATH`, runs `AppTest.from_file("streamlit_app.py")`, and asserts the
visible form and guidance. The existing [test_ui_regression.py](../tests/test_ui_regression.py)
is the reference implementation.

## UI Test Rules

1. Use a temporary database; never write test data to `data/`.
2. Assert user-visible labels, errors, table content, or navigation state, not Streamlit internals.
3. Keep money, dates, locks, and summary calculations primarily covered by deterministic domain
   tests. A UI test confirms that the result is reachable and visible.
4. Add a UI test for every new primary workflow and for every visible validation or lock error.
5. Avoid duplicating every combination in the UI suite; use Hypothesis and pytest for breadth in
   the domain suite.