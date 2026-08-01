# Acceptance Checklist

Use this checklist after backlog refinement and again before accepting a feature delivery.

- [ ] The GitHub Issue has one INVEST user story with the intended user value.
- [ ] Scope, assumptions, dependencies, and out-of-scope behavior are explicit.
- [ ] Every primary user-visible flow is an independent Gherkin scenario.
- [ ] Gherkin includes applicable success, empty, validation-error, and lock/error paths.
- [ ] Each scenario has an observable result; it does not prescribe implementation details.
- [ ] Each Gherkin scenario maps to a domain, persistence, UI, or property regression test.
- [ ] New Streamlit flows have AppTest coverage for the visible behavior they introduce.
- [ ] Financial rules have deterministic pytest coverage independent of UI tests.
- [ ] Test files pass and provide evidence for the changed scenarios.
- [ ] Documentation and the Spec Kit artifact match the delivered scope.