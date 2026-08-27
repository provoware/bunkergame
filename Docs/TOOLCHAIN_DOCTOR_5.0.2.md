# Toolchain Doctor 5.0.2

## External/verified UE 5.8 requirements

Epic's current UE 5.8 documentation specifies:
- Linux: Ubuntu 22.04 / Rocky Linux 8 / Red Hat Linux 8+; Clang 20.1.8; native toolchain v26; glibc >= 2.28.
- Windows: Visual Studio 2022 17.14 minimum; MSVC 14.38 minimum; Windows SDK 10.0.22621.0 minimum; recommended VS 2026/MSVC 14.50/SDK 10.0.26100.0.

## Implementation

The Doctor:
- discovers engine paths
- inspects platform toolchains
- parses versions robustly
- classifies requirements
- maps findings to repair recipes
- records structured evidence
- turns recurring issues (>=2 observations) into generated preflight rules.

## Repair safety

System-wide installs, OS upgrades, sudo/root and unknown downloads remain assisted, never silent.
