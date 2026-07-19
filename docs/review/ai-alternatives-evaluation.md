# AI Alternatives Evaluation (Low-Setup)

## Goal

Select practical, reusable AI assistance that improves review quality with minimal configuration overhead.

## Candidate Stack

1. Public prompt/skill packs for VS Code + Copilot chat workflows.
2. CodeRabbit for automated PR review feedback.
3. Continue.dev for open-source agent workflows in-editor.
4. Aider for terminal-first pair programming and change iteration.
5. Sourcegraph Cody for semantic codebase Q&A and navigation.

## Evaluation Rubric

Score each from 1 (poor) to 5 (excellent):

- Setup time
- Signal-to-noise in findings
- Spec-awareness (can it reason from docs/spec)
- Actionability (clear fix/test suggestions)
- Repeatability (consistent quality week to week)
- Cost transparency

## Standard Trial Task

Run each tool on the same mini-task:

1. Review spec alignment for summary status rules.
2. Identify top 3 test gaps.
3. Propose one concrete test case and one bug-risk fix.

## Results Table

| Tool | Setup Time | Signal/Noise | Spec-Awareness | Actionability | Repeatability | Cost Transparency | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Public Prompt/Skill Pack |  |  |  |  |  |  |  |
| CodeRabbit |  |  |  |  |  |  |  |
| Continue.dev |  |  |  |  |  |  |  |
| Aider |  |  |  |  |  |  |  |
| Sourcegraph Cody |  |  |  |  |  |  |  |

## Decision Rule

- Keep at most two primary tools for daily use.
- Keep one fallback tool for deep-dive investigations.
- Re-evaluate monthly because agent capabilities change quickly.

## Public Skills/Prompts Discovery Checklist

When evaluating public skills/prompt packs:

- Check maintenance recency (recent commits/releases).
- Check license compatibility.
- Check whether examples match your stack (Python + Streamlit + SQLAlchemy).
- Check if prompts enforce evidence-based outputs (file pointers, tests, risk ranking).