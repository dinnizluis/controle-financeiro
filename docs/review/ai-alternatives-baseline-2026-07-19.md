# AI Alternatives Baseline - 2026-07-19

## Scope

Initial baseline scoring using the rubric in [docs/review/ai-alternatives-evaluation.md](ai-alternatives-evaluation.md).

This baseline is a starting point, not a final decision. Scores should be revised after one full week of real usage.

## Baseline Scores (1-5)

| Tool | Setup Time | Signal/Noise | Spec-Awareness | Actionability | Repeatability | Cost Transparency | Baseline Total | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Public Prompt/Skill Pack | 5 | 3 | 4 | 3 | 3 | 5 | 23 | Lowest setup, quality depends on prompt discipline and maintenance of pack |
| CodeRabbit | 4 | 4 | 3 | 4 | 4 | 3 | 22 | Strong PR review signal, but spec-awareness needs explicit project context |
| Continue.dev | 3 | 3 | 4 | 4 | 3 | 4 | 21 | Flexible and open, but requires workflow curation to keep output consistent |
| Aider | 3 | 4 | 3 | 5 | 4 | 4 | 23 | High actionability for iterative code/test loops in terminal flow |
| Sourcegraph Cody | 4 | 4 | 3 | 3 | 4 | 3 | 21 | Good repository Q&A, less direct for structured review checklist execution |

## Initial Recommendation

1. Primary daily pair: Public Prompt/Skill Pack + Aider.
2. PR gate layer: CodeRabbit.
3. Fallback deep-dive: Continue.dev or Cody when cross-file exploration is needed.

## Week-1 Trial Tasks

Run each candidate on the same tasks:

1. Detect spec drift for cycle lock behavior.
2. Propose tests for summary status thresholds.
3. Review invalid cycle key handling and suggest UX-safe error behavior.

## Re-Scoring Rules

- Update scores only with concrete evidence (found issue, false positive, missing case).
- Keep notes short and evidence-based.
- Re-rank top 2 tools at the end of week-1.