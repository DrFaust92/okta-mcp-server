# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for policy and policy-rule deletion/deactivation."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from okta_mcp_server.tools.policies.policies import (
    deactivate_policy,
    deactivate_policy_rule,
    delete_policy,
    delete_policy_rule,
)


POLICY_ID = "00p1234567890ABCDEF"
RULE_ID = "0pr1234567890ABCDEF"


# ===================================================================
# delete_policy — calls Okta directly
# ===================================================================

class TestDeletePolicyElicitation:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_accept_confirmed_deletes(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_policy(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID)

        mock_okta_client.delete_policy.assert_awaited_once_with(POLICY_ID)
        assert result["success"] is True
        assert POLICY_ID in result["message"]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.delete_policy.return_value = (None, "API Error: policy not found")
        mock_get_client.return_value = client

        result = await delete_policy(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID)

        assert "error" in result

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_during_delete(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.delete_policy.side_effect = Exception("Connection refused")
        mock_get_client.return_value = client

        result = await delete_policy(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID)

        assert "error" in result


class TestDeletePolicyFallback:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_fallback_proceeds_with_deletion(self, mock_get_client, ctx_no_elicitation, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_policy(ctx=ctx_no_elicitation, policy_id=POLICY_ID)

        mock_okta_client.delete_policy.assert_awaited_once_with(POLICY_ID)
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_fallback_proceeds_with_deletion(self, mock_get_client, ctx_elicit_exception, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_policy(ctx=ctx_elicit_exception, policy_id=POLICY_ID)

        mock_okta_client.delete_policy.assert_awaited_once_with(POLICY_ID)
        assert result["success"] is True


# ===================================================================
# delete_policy_rule — calls Okta directly
# ===================================================================

class TestDeletePolicyRuleElicitation:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_accept_confirmed_deletes(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_policy_rule(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID, rule_id=RULE_ID)

        mock_okta_client.delete_policy_rule.assert_awaited_once_with(POLICY_ID, RULE_ID)
        assert result["success"] is True
        assert RULE_ID in result["message"]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.delete_policy_rule.return_value = (None, "API Error: rule not found")
        mock_get_client.return_value = client

        result = await delete_policy_rule(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID, rule_id=RULE_ID)

        assert "error" in result

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_during_delete(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.delete_policy_rule.side_effect = Exception("Connection refused")
        mock_get_client.return_value = client

        result = await delete_policy_rule(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID, rule_id=RULE_ID)

        assert "error" in result


class TestDeletePolicyRuleFallback:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_fallback_proceeds_with_deletion(self, mock_get_client, ctx_no_elicitation, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_policy_rule(ctx=ctx_no_elicitation, policy_id=POLICY_ID, rule_id=RULE_ID)

        mock_okta_client.delete_policy_rule.assert_awaited_once_with(POLICY_ID, RULE_ID)
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_fallback_proceeds_with_deletion(self, mock_get_client, ctx_elicit_exception, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await delete_policy_rule(ctx=ctx_elicit_exception, policy_id=POLICY_ID, rule_id=RULE_ID)

        mock_okta_client.delete_policy_rule.assert_awaited_once_with(POLICY_ID, RULE_ID)
        assert result["success"] is True


# ===================================================================
# deactivate_policy_rule — calls Okta directly
# ===================================================================

class TestDeactivatePolicyRuleElicitation:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_accept_confirmed_deactivates(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_policy_rule(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID, rule_id=RULE_ID)

        mock_okta_client.deactivate_policy_rule.assert_awaited_once_with(POLICY_ID, RULE_ID)
        assert result["success"] is True
        assert RULE_ID in result["message"]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.deactivate_policy_rule.return_value = (None, "API Error: rule not found")
        mock_get_client.return_value = client

        result = await deactivate_policy_rule(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID, rule_id=RULE_ID)

        assert "error" in result

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_during_deactivation(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.deactivate_policy_rule.side_effect = Exception("Connection refused")
        mock_get_client.return_value = client

        result = await deactivate_policy_rule(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID, rule_id=RULE_ID)

        assert "error" in result


class TestDeactivatePolicyRuleFallback:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_fallback_auto_confirms(self, mock_get_client, ctx_no_elicitation, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_policy_rule(ctx=ctx_no_elicitation, policy_id=POLICY_ID, rule_id=RULE_ID)

        mock_okta_client.deactivate_policy_rule.assert_awaited_once_with(POLICY_ID, RULE_ID)
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_fallback_auto_confirms(self, mock_get_client, ctx_elicit_exception, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_policy_rule(ctx=ctx_elicit_exception, policy_id=POLICY_ID, rule_id=RULE_ID)

        mock_okta_client.deactivate_policy_rule.assert_awaited_once_with(POLICY_ID, RULE_ID)
        assert result["success"] is True


# ===================================================================
# deactivate_policy — calls Okta directly
# ===================================================================

class TestDeactivatePolicyElicitation:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_accept_confirmed_deactivates(self, mock_get_client, ctx_elicit_accept_true, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_policy(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID)

        mock_okta_client.deactivate_policy.assert_awaited_once_with(POLICY_ID)
        assert result["success"] is True
        assert POLICY_ID in result["message"]

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_okta_api_error(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.deactivate_policy.return_value = (None, "API Error: policy not found")
        mock_get_client.return_value = client

        result = await deactivate_policy(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID)

        assert "error" in result

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_during_deactivation(self, mock_get_client, ctx_elicit_accept_true):
        client = AsyncMock()
        client.deactivate_policy.side_effect = Exception("Connection refused")
        mock_get_client.return_value = client

        result = await deactivate_policy(ctx=ctx_elicit_accept_true, policy_id=POLICY_ID)

        assert "error" in result


class TestDeactivatePolicyFallback:
    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_fallback_auto_confirms(self, mock_get_client, ctx_no_elicitation, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_policy(ctx=ctx_no_elicitation, policy_id=POLICY_ID)

        mock_okta_client.deactivate_policy.assert_awaited_once_with(POLICY_ID)
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("okta_mcp_server.tools.policies.policies.get_okta_client")
    async def test_exception_fallback_auto_confirms(self, mock_get_client, ctx_elicit_exception, mock_okta_client):
        mock_get_client.return_value = mock_okta_client

        result = await deactivate_policy(ctx=ctx_elicit_exception, policy_id=POLICY_ID)

        mock_okta_client.deactivate_policy.assert_awaited_once_with(POLICY_ID)
        assert result["success"] is True
