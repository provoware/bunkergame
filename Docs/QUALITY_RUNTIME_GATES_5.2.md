# Quality Runtime Gates 5.2

## Regression attribution

Every run stores:
- UTC timestamp
- Run ID
- branch
- commit
- dirty working tree status
- platform
- OS release / machine
- project metadata
- selected runtime/build environment
- toolchain snapshot hash.

## P0/P1 promotion

Two independent run observations promote a stable error code to a persistent preflight rule.

P0:
- blocks all dependent starts.

P1:
- permits independent Core QA,
- blocks dependent runtime/CP gates.

## Real toolchain repair

The repair planner differentiates:
- read-only discovery
- explicit user-authorized package installation
- assisted engine setup.

The script never silently executes `sudo`.

Linux Clang repair may use `apt-get install clang-20 lld-20` only through explicit `--apply --yes` execution by the operator. Prefer Epic's project/engine native toolchain setup once UE 5.8 is installed.
