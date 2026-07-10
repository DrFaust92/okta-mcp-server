# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

"""Tests for /health version resolution and health-probe log filtering."""

from __future__ import annotations

import logging

from okta_mcp_server.server import _HealthProbeAccessFilter, _resolve_version


def _access_record(path: str) -> logging.LogRecord:
    # Mirrors uvicorn.access's record shape: msg template + positional args.
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='%s - "%s %s HTTP/%s" %s',
        args=("172.23.32.161:41128", "GET", path, "1.1", 200),
        exc_info=None,
    )


def test_health_probe_lines_are_dropped():
    assert _HealthProbeAccessFilter().filter(_access_record("/health")) is False


def test_real_request_lines_are_kept():
    assert _HealthProbeAccessFilter().filter(_access_record("/mcp")) is True


def test_prefers_app_version_env(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.6.0")
    assert _resolve_version() == "1.6.0"


def test_falls_back_to_package_metadata(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    # Installed package metadata reports the pyproject version (e.g. "0.1.0"),
    # never the empty string / None.
    assert _resolve_version()


def test_blank_app_version_ignored(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "")
    # Empty string is falsy → must fall through to package metadata, not return "".
    assert _resolve_version()
