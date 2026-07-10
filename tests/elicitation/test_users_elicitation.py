# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for user deactivation and deletion."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp.exceptions import ToolError

from okta_mcp_server.tools.users.users import (
    deactivate_user,
    delete_deactivated_user,
)

USER_ID = "00u1234567890ABCDEF"


# ===================================================================
# deactivate_user — calls Okta directly
# ===================================================================


class TestDeactivateUserElicitation:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_accept_confirmed_deactivates(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_user(user_id=USER_ID, ctx=ctx_elicit_accept_true)

        mock_okta_client.deactivate_user.assert_awaited_once_with(USER_ID)
        assert "deactivated successfully" in result[0]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.deactivate_user.return_value = (None, None, "API Error: user not found")
        mock_get_client.return_value = client

        with pytest.raises(ToolError):
            await deactivate_user(user_id=USER_ID, ctx=ctx_elicit_accept_true)

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_exception_during_deactivate(self, mock_get_client, ctx_elicit_accept_true):
        mock_get_client.side_effect = Exception("Connection refused")

        with pytest.raises(ToolError):
            await deactivate_user(user_id=USER_ID, ctx=ctx_elicit_accept_true)


class TestDeactivateUserFallback:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_fallback_proceeds_with_deactivation(self, mock_get_client, ctx_no_elicitation, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_user(user_id=USER_ID, ctx=ctx_no_elicitation)

        mock_okta_client.deactivate_user.assert_awaited_once_with(USER_ID)
        assert "deactivated successfully" in result[0]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_exception_fallback_proceeds_with_deactivation(
        self, mock_get_client, ctx_elicit_exception, mock_okta_client
    ):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_user(user_id=USER_ID, ctx=ctx_elicit_exception)

        mock_okta_client.deactivate_user.assert_awaited_once_with(USER_ID)
        assert "deactivated successfully" in result[0]


# ===================================================================
# delete_deactivated_user — calls Okta directly
# ===================================================================


class TestDeleteDeactivatedUserElicitation:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_accept_confirmed_deletes(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_deactivated_user(user_id=USER_ID, ctx=ctx_elicit_accept_true)

        mock_okta_client.delete_user.assert_awaited_once_with(USER_ID)
        assert "deleted successfully" in result[0]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.delete_user.return_value = (None, None, "API Error: user not found")
        mock_get_client.return_value = client

        with pytest.raises(ToolError):
            await delete_deactivated_user(user_id=USER_ID, ctx=ctx_elicit_accept_true)

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_exception_during_delete(self, mock_get_client, ctx_elicit_accept_true):
        mock_get_client.side_effect = Exception("Connection refused")

        with pytest.raises(ToolError):
            await delete_deactivated_user(user_id=USER_ID, ctx=ctx_elicit_accept_true)


class TestDeleteDeactivatedUserFallback:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_fallback_proceeds_with_deletion(self, mock_get_client, ctx_no_elicitation, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_deactivated_user(user_id=USER_ID, ctx=ctx_no_elicitation)

        mock_okta_client.delete_user.assert_awaited_once_with(USER_ID)
        assert "deleted successfully" in result[0]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.users.users.get_okta_client")
    async def test_exception_fallback_proceeds_with_deletion(
        self, mock_get_client, ctx_elicit_exception, mock_okta_client
    ):
        mock_get_client.return_value = mock_okta_client

        result = await delete_deactivated_user(user_id=USER_ID, ctx=ctx_elicit_exception)

        mock_okta_client.delete_user.assert_awaited_once_with(USER_ID)
        assert "deleted successfully" in result[0]
