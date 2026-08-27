#!/usr/bin/env python3
"""Shared non-secret identity helpers for UE runner evidence binding.

The machine fingerprint is intentionally pseudonymous and lightweight. It is
meant to prevent accidental/casual evidence reuse across machines, not to act
as hardware attestation or a cryptographic proof of machine ownership.
"""

from __future__ import annotations

import hashlib
import platform
import re
import subprocess
from pathlib import Path

EXPECTED_REPOSITORY = "provoware/bunkergame"
MACHINE_IDENTITY_SCHEME = "hostname-os-arch-sha256-v1"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HTTPS_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", re.IGNORECASE)
SSH_SCP_RE = re.compile(r"^(?:[^@]+@)?github\.com:([^/]+)/([^/]+?)(?:\.git)?$", re.IGNORECASE)
SSH_URL_RE = re.compile(r"^ssh://(?:[^@]+@)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", re.IGNORECASE)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def normalize_repository_identity(remote_url: str) -> str | None:
    text = (remote_url or "").strip()
    for pattern in (HTTPS_RE, SSH_SCP_RE, SSH_URL_RE):
        match = pattern.fullmatch(text)
        if match:
            owner, repo = match.groups()
            return f"{owner}/{repo}".lower()
    return None


def current_repository_identity(root: Path) -> tuple[str | None, str]:
    result = _git(root, "remote", "get-url", "origin")
    if result.returncode != 0:
        return None, f"origin remote unavailable: {result.stderr.strip()}"
    identity = normalize_repository_identity(result.stdout)
    if identity is None:
        return None, "origin remote is not a recognized github.com repository URL"
    return identity, "recognized origin repository"


def current_git_head(root: Path) -> tuple[str | None, str]:
    result = _git(root, "rev-parse", "HEAD")
    if result.returncode != 0:
        return None, f"git HEAD unavailable: {result.stderr.strip()}"
    sha = result.stdout.strip().lower()
    if not SHA40_RE.fullmatch(sha):
        return None, "git HEAD is not a full 40-character SHA"
    return sha, "full git HEAD resolved"


def git_worktree_clean(root: Path) -> tuple[bool, str]:
    result = _git(root, "status", "--porcelain")
    if result.returncode != 0:
        return False, f"git status unavailable: {result.stderr.strip()}"
    dirty = [line for line in result.stdout.splitlines() if line.strip()]
    return not dirty, "clean" if not dirty else f"{len(dirty)} changed/untracked path(s)"


def machine_fingerprint() -> tuple[str | None, str]:
    node = platform.node().strip()
    system = platform.system().strip()
    machine = platform.machine().strip()
    if not node or not system or not machine:
        return None, "hostname/OS/architecture identity is incomplete"
    material = f"BUNKER_BEATS_RUNNER_ID_V1|{node}|{system}|{machine}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()
    return digest, MACHINE_IDENTITY_SCHEME
