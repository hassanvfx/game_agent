#!/usr/bin/env python3
"""Shared non-interactive gcloud auth preflight helpers for upload-enabled runs."""

from __future__ import annotations

import subprocess
from typing import Any


DEFAULT_GCLOUD_PROJECT = "jabali-prod"


def run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": "command not found",
            "status": "missing",
        }

    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "status": "passed" if completed.returncode == 0 else "failed",
    }


def run_gcloud_auth_preflight(project: str = DEFAULT_GCLOUD_PROJECT) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    version_check = run_command(["gcloud", "--version"])
    checks.append({"name": "gcloud_version", **version_check})
    if version_check["status"] == "missing":
        return {
            "status": "failed",
            "project": project,
            "message": "upload requested but gcloud is not installed or not on PATH",
            "checks": checks,
        }
    if version_check["status"] != "passed":
        return {
            "status": "failed",
            "project": project,
            "message": "upload requested but gcloud version check failed",
            "checks": checks,
        }

    auth_check = run_command(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"])
    checks.append({"name": "active_account", **auth_check})
    if auth_check["status"] != "passed":
        return {
            "status": "failed",
            "project": project,
            "message": "upload requested but gcloud could not list active accounts",
            "checks": checks,
        }

    active_accounts = [line.strip() for line in auth_check["stdout"].splitlines() if line.strip()]
    if not active_accounts:
        return {
            "status": "failed",
            "project": project,
            "message": "upload requested but gcloud has no active authenticated account",
            "next_action": "Run `gcloud auth login` in an interactive terminal before launching upload-enabled runs.",
            "checks": checks,
        }

    project_check = run_command(["gcloud", "config", "get-value", "project"])
    checks.append({"name": "configured_project", **project_check})
    configured_project = project_check["stdout"].strip() if project_check["status"] == "passed" else None

    return {
        "status": "passed",
        "project": project,
        "configured_project": configured_project,
        "active_account": active_accounts[0],
        "active_accounts": active_accounts,
        "message": "gcloud upload auth preflight passed",
        "checks": checks,
    }