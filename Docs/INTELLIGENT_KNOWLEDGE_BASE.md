# BUNKER BEATS — Intelligent Knowledge Base

## Purpose

This file is the human-readable operating memory of the quality system.

The launcher learns from repeated, evidence-backed incidents. It does not rewrite gameplay or execute arbitrary repairs by itself.

## Learning loop

1. Observe a concrete failure.
2. Store immutable run evidence.
3. Attach branch, commit, diff, files, tests, platform and toolchain context.
4. Generate candidate causes.
5. Rank candidate solutions.
6. Offer safe/assisted actions.
7. Re-run validation.
8. Record the outcome.
9. Promote repeated failures into durable preflight rules.
10. Add a regression-prevention recommendation.

## Confidence

- HIGH: reproduced or independently confirmed; a specific change is a strong candidate.
- MEDIUM: strong temporal/file/test evidence, but not yet reproduced.
- LOW: weak correlation.
- NONE: no meaningful attribution.

## Solution selection

Solutions are scored by:
- expected value
- risk
- reversibility
- evidence strength
- scope size
- user interruption cost.

The tool recommends the smallest sustainable change.

## Persistence

Machine-readable:
`Diagnostics/Knowledge/knowledge.jsonl`

Human-readable:
`Diagnostics/Knowledge/KNOWLEDGE_INSIGHTS.md`

Attribution:
`Diagnostics/Attribution/`

Regression:
`Diagnostics/Regression/`

## Non-negotiable rule

A repeated error must create a regression-prevention artifact.
A solution is not considered successful until the same relevant test/path has been revalidated.
