# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from __future__ import annotations

import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal, cast

from fastmcp import FastMCP
from loguru import logger

from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

LOG_FILE = os.environ.get("OKTA_LOG_FILE")
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")


@dataclass
class OktaAppContext:
    okta_auth_manager: OktaAuthManager | None = None


@asynccontextmanager
async def okta_authorisation_flow(server: FastMCP) -> AsyncIterator[OktaAppContext]:
    """
    Manages the application lifecycle. In stdio mode, initializes OktaAuthManager
    for device/JWT flow. In HTTP mode with OAuthProxy, authentication is handled
    via browser redirect — no OktaAuthManager needed.
    """
    if MCP_TRANSPORT == "streamable-http":
        logger.info("HTTP transport: OAuthProxy handles authentication via browser redirect")
        yield OktaAppContext()
    else:
        logger.info("Initializing OktaAuthManager (authentication deferred to first tool call)")
        manager = OktaAuthManager()
        try:
            yield OktaAppContext(okta_auth_manager=manager)
        finally:
            logger.debug("Clearing Okta tokens")
            manager.clear_tokens()


# --- Build the FastMCP instance based on transport mode ---

if MCP_TRANSPORT == "streamable-http":
    from fastmcp.server.auth import OAuthProxy
    from fastmcp.server.auth.providers.introspection import IntrospectionTokenVerifier

    _mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
    _okta_org_url = os.environ.get("OKTA_ORG_URL", "").rstrip("/")
    _okta_client_id = os.environ.get("OKTA_CLIENT_ID", "")
    _okta_client_secret = os.environ.get("OKTA_CLIENT_SECRET", "")
    _okta_scopes = os.environ.get("OKTA_SCOPES", "openid profile email offline_access")
    # Cache introspection results to avoid hitting Okta on every tool call.
    # Tune via OKTA_TOKEN_CACHE_TTL (seconds). Default: 60s balances revocation
    # freshness with reduced load. Set to 0 to disable caching.
    _token_cache_ttl = int(os.environ.get("OKTA_TOKEN_CACHE_TTL", "60")) or None

    _auth = OAuthProxy(
        upstream_authorization_endpoint=f"{_okta_org_url}/oauth2/v1/authorize",
        upstream_token_endpoint=f"{_okta_org_url}/oauth2/v1/token",
        upstream_client_id=_okta_client_id,
        upstream_client_secret=_okta_client_secret,
        token_verifier=IntrospectionTokenVerifier(
            introspection_url=f"{_okta_org_url}/oauth2/v1/introspect",
            client_id=_okta_client_id,
            client_secret=_okta_client_secret,
            cache_ttl_seconds=_token_cache_ttl,
        ),
        base_url=_mcp_server_url,
        require_authorization_consent=False,
        extra_authorize_params={"scope": _okta_scopes},
    )

    mcp = FastMCP(
        "Okta IDaaS MCP Server",
        lifespan=okta_authorisation_flow,
        auth=_auth,
    )
else:
    mcp = FastMCP(
        "Okta IDaaS MCP Server",
        lifespan=okta_authorisation_flow,
    )


def main():
    """Run the Okta MCP server."""
    logger.remove()

    if LOG_FILE:
        logger.add(
            LOG_FILE,
            mode="w",
            level=os.environ.get("OKTA_LOG_LEVEL", "INFO"),
            retention="5 days",
            enqueue=True,
            serialize=True,
        )

    logger.add(
        sys.stderr, level=os.environ.get("OKTA_LOG_LEVEL", "INFO"), format="{time} {level} {message}", serialize=True
    )

    logger.info("Starting Okta MCP Server")
    from okta_mcp_server.tools.applications import applications  # noqa: F401
    from okta_mcp_server.tools.group_rules import group_rules  # noqa: F401
    from okta_mcp_server.tools.groups import groups  # noqa: F401
    from okta_mcp_server.tools.policies import policies  # noqa: F401
    from okta_mcp_server.tools.system_logs import system_logs  # noqa: F401
    from okta_mcp_server.tools.users import users  # noqa: F401

    if MCP_TRANSPORT == "streamable-http":
        mcp.run(transport=cast(Literal["streamable-http"], MCP_TRANSPORT), host="0.0.0.0", port=8000)
    else:
        mcp.run(transport=cast(Literal["stdio", "sse", "streamable-http"], MCP_TRANSPORT))
