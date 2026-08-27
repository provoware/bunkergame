# Regression Attribution 6.0

## Goal

Move from run-level regression detection to change-level attribution.

For every relevant run capture:
- UTC timestamp
- run ID
- branch
- commit
- dirty state
- base commit
- commit metadata
- changed files and statuses
- diff statistics
- patch SHA-256
- platform/build environment
- toolchain snapshot hash when available
- test case IDs.

## Association model

Failure
→ changed files
→ impacted test cases
→ candidate files
→ confidence score.

The system explicitly distinguishes:
- HIGH confidence candidate
- MEDIUM confidence
- LOW confidence
- NONE.

A candidate file is never presented as proven causal merely because it changed before a failure.

## Bisect

When the evidence is insufficient, use a guided `git bisect` plan.
Git documents `git bisect run` for automating good/bad commit classification. citeturn270684search2turn270684search0

## Diff evidence

Git provides machine-readable changed-file and status views through diff options such as `--name-status`; this is used for attribution input. citeturn270684search1

## Safety

Automatic checkout/reset/bisect is disabled by default.
Repository state must remain under explicit developer control.
