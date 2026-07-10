# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

"""Tests for list_applications pagination / fetch_all support."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from okta_mcp_server.tools.applications.applications import list_applications


def _fake_app(app_id: str):
    app = MagicMock()
    app.model_dump.return_value = {
        "id": app_id,
        "name": "oidc_client",
        "label": f"App {app_id}",
        "status": "ACTIVE",
        "signOnMode": "AUTO_LOGIN",
    }
    return app


def _response(headers=None):
    resp = MagicMock()
    resp.headers = headers or {}
    return resp


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.applications.applications.get_okta_client")
async def test_single_page_returns_paginated_dict(mock_get_client):
    client = AsyncMock()
    client.list_applications.return_value = ([_fake_app("0oa1")], _response(), None)
    mock_get_client.return_value = client

    result = await list_applications(ctx=MagicMock(request_context=None))

    assert isinstance(result, dict)
    assert result["total_fetched"] == 1
    assert result["fetch_all_used"] is False
    assert result["has_more"] is False
    assert result["items"][0]["id"] == "0oa1"


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.applications.applications.paginate_all_results")
@patch("okta_mcp_server.tools.applications.applications.has_next_page")
@patch("okta_mcp_server.tools.applications.applications.get_okta_client")
async def test_fetch_all_aggregates_pages(mock_get_client, mock_has_next, mock_paginate):
    client = AsyncMock()
    client.list_applications.return_value = ([_fake_app("0oa1")], _response(), None)
    mock_get_client.return_value = client
    mock_has_next.return_value = True
    mock_paginate.return_value = (
        [_fake_app("0oa1"), _fake_app("0oa2"), _fake_app("0oa3")],
        {"pages_fetched": 2, "total_items": 3, "stopped_early": False, "stop_reason": None},
    )

    result = await list_applications(ctx=MagicMock(request_context=None), fetch_all=True)

    assert result["fetch_all_used"] is True
    assert result["total_fetched"] == 3
    assert {i["id"] for i in result["items"]} == {"0oa1", "0oa2", "0oa3"}
    assert result["pagination_info"]["pages_fetched"] == 2
    mock_paginate.assert_awaited_once()


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.applications.applications.get_okta_client")
async def test_okta_error_returns_error_dict(mock_get_client):
    client = AsyncMock()
    client.list_applications.return_value = (None, _response(), "boom")
    mock_get_client.return_value = client

    result = await list_applications(ctx=MagicMock(request_context=None))

    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.asyncio
@patch("okta_mcp_server.tools.applications.applications.get_okta_client")
async def test_no_apps_returns_empty_paginated_dict(mock_get_client):
    client = AsyncMock()
    client.list_applications.return_value = ([], _response(), None)
    mock_get_client.return_value = client

    result = await list_applications(ctx=MagicMock(request_context=None))

    assert result["items"] == []
    assert result["total_fetched"] == 0
