# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

"""Tests for /health version resolution."""

from __future__ import annotations

from okta_mcp_server.server import _resolve_version


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
