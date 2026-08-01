---
name: Feature
about: Create a spec-first feature issue
title: "feat: "
labels: ["feature"]
---

## Problem

## Goal

## User Story

As a [user], I want [goal], so that [value].

## INVEST Check

- [ ] **Independent**: dependencies and blockers are identified.
- [ ] **Negotiable**: minimum scope and deferred options are explicit.
- [ ] **Valuable**: user-visible value is stated in the user story.
- [ ] **Estimable**: scope is clear enough to estimate.
- [ ] **Small**: the item fits one reviewable delivery; otherwise it is split.
- [ ] **Testable**: observable acceptance scenarios are defined.

## Spec Kit Artifact

- [ ] `specs/<number>-<feature>/spec.md` exists or will be created with `/speckit.specify`.

## Business Rules

- [ ] Rules are explicit and testable.
- [ ] Financial-data, cycle, summary, or history impact is identified.

## Acceptance Criteria (Gherkin)

```gherkin
Feature: [user-visible capability]

	Scenario: [successful user outcome]
		Given [starting user-visible state]
		When [user action]
		Then [observable result]

	Scenario: [validation, empty, or lock/error path]
		Given [starting user-visible state]
		When [user action]
		Then [observable error or empty result]
```

## UI Flow and Regression Test Map

| Scenario | Starting state or screen | User action | Observable result | Test layer | Planned test |
|----------|--------------------------|-------------|-------------------|------------|--------------|
| [scenario] | [screen/state] | [action] | [result] | domain/persistence/ui | [test path] |

- [ ] Every visible UI flow has a Gherkin scenario and regression-test target.
- [ ] Streamlit interactions use `streamlit.testing.v1.AppTest` when UI coverage is needed.
- [ ] Financial rules have deterministic domain or persistence coverage.

## Edge Cases

- [ ] Boundary and error scenarios are recorded in the spec.

## Out of Scope
