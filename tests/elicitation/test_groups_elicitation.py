# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for group deletion."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from okta_mcp_server.tools.groups.groups import confirm_delete_group, delete_group

GROUP_ID = "00g1234567890ABCDEF"


# ---------------------------------------------------------------------------
# delete_group — always returns confirmation prompt (sync function)
# ---------------------------------------------------------------------------


class TestDeleteGroup:
    """delete_group is now a sync function that always returns a confirmation dict."""

    def test_returns_confirmation_dict(self):
        result = delete_group(GROUP_ID, ctx=None)

        assert result[0]["confirmation_required"] is True
        assert GROUP_ID in result[0]["message"]
        assert result[0]["group_id"] == GROUP_ID

    def test_returns_confirmation_dict_without_ctx(self):
        result = delete_group(GROUP_ID)

        assert result[0]["confirmation_required"] is True


# ---------------------------------------------------------------------------
# confirm_delete_group — legacy two-step flow
# ---------------------------------------------------------------------------


class TestConfirmDeleteGroupDeprecated:
    """Tests for the confirm_delete_group tool."""

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.groups.groups.get_okta_client")
    async def test_correct_confirmation_deletes(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await confirm_delete_group(GROUP_ID, "DELETE", ctx=ctx_elicit_accept_true)

        mock_okta_client.delete_group.assert_awaited_once_with(GROUP_ID)
        assert result[0]["message"] == f"Group {GROUP_ID} deleted successfully"

    @pytest.mark.asyncio
    async def test_incorrect_confirmation_cancels(self, ctx_elicit_accept_true):
        result = await confirm_delete_group(GROUP_ID, "wrong", ctx=ctx_elicit_accept_true)

        assert "error" in result[0]
        assert "cancelled" in result[0]["error"].lower() or "Deletion cancelled" in result[0]["error"]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.groups.groups.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        from unittest.mock import AsyncMock

        client = AsyncMock()
        client.delete_group.return_value = (None, None, "API Error")
        mock_get_client.return_value = client

        result = await confirm_delete_group(GROUP_ID, "DELETE", ctx=ctx_elicit_accept_true)

        assert "error" in result[0]
