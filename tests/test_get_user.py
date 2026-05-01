# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

"""Regression tests for get_user tuple unpacking from the v3 Okta SDK."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from okta_mcp_server.tools.users.users import get_user


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.users.users.get_okta_client")
async def test_get_user_unpacks_tuple_and_summarizes(mock_get_client):
    fake_user = MagicMock()
    fake_user.model_dump.return_value = {
        "id": "00u123",
        "status": "ACTIVE",
        "created": "2024-01-01T00:00:00Z",
        "profile": {"login": "x@y.ai", "email": "x@y.io"},
        "type": {"id": "oty1"},
    }

    client = AsyncMock()
    client.get_user.return_value = (fake_user, None, None)
    mock_get_client.return_value = client

    result = await get_user(user_id="00u123")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "00u123"
    assert result[0]["status"] == "ACTIVE"
    assert result[0]["profile"]["login"] == "x@y.ai"


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.users.users.get_okta_client")
async def test_get_user_returns_error_string_on_okta_err(mock_get_client):
    client = AsyncMock()
    client.get_user.return_value = (None, None, "API Error: not found")
    mock_get_client.return_value = client

    result = await get_user(user_id="00u123")

    assert "Error" in result[0]


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.users.users.get_okta_client")
async def test_get_user_returns_empty_list_when_user_is_none(mock_get_client):
    client = AsyncMock()
    client.get_user.return_value = (None, None, None)
    mock_get_client.return_value = client

    result = await get_user(user_id="00u123")

    assert result == []
