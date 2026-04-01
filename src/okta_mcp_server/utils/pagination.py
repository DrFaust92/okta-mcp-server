# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from loguru import logger


def extract_after_cursor(response) -> Optional[str]:
    """Extract the 'after' pagination cursor from the okta SDK v3 ApiResponse.

    The v3 SDK returns an ApiResponse with a 'headers' mapping. Okta signals
    the next page via a Link header: <url>; rel="next".
    """
    if not response or not hasattr(response, "headers") or not response.headers:
        return None

    link_header = response.headers.get("link") or response.headers.get("Link", "")
    if not link_header or 'rel="next"' not in link_header:
        return None

    for part in link_header.split(","):
        if 'rel="next"' in part:
            url = part.split(";")[0].strip().strip("<>")
            try:
                parsed = urlparse(url)
                return parse_qs(parsed.query).get("after", [None])[0]
            except Exception as e:
                logger.warning(f"Failed to parse next-page URL from Link header: {e}")

    return None


def has_next_page(response) -> bool:
    """Return True if the ApiResponse indicates another page is available."""
    return extract_after_cursor(response) is not None


async def paginate_all_results(
    api_fn: Callable,
    base_params: Dict[str, Any],
    initial_items: List,
    initial_response,
    max_pages: int = 50,
    delay_between_requests: float = 0.1,
) -> Tuple[List, Dict[str, Any]]:
    """Auto-paginate through all pages of results using the okta SDK v3 cursor pattern.

    Args:
        api_fn: The client method to call for subsequent pages (e.g. client.list_users).
        base_params: The base query-parameter dict to use for every call.
        initial_items: The first page of items already fetched.
        initial_response: The ApiResponse from the first call (used to read the first cursor).
        max_pages: Safety limit on the number of pages to fetch.
        delay_between_requests: Seconds to wait between calls to avoid rate-limiting.

    Returns:
        Tuple of (all_items, pagination_info dict).
    """
    all_items = list(initial_items) if initial_items else []
    pages_fetched = 1
    response = initial_response

    pagination_info: dict[str, Any] = {
        "pages_fetched": 1,
        "total_items": len(all_items),
        "stopped_early": False,
        "stop_reason": None,
    }

    try:
        while pages_fetched < max_pages:
            after = extract_after_cursor(response)
            if not after:
                break

            if delay_between_requests > 0:
                await asyncio.sleep(delay_between_requests)

            try:
                next_params = {**base_params, "after": after}
                next_items, response, err = await api_fn(**next_params)

                if err:
                    logger.warning(f"Error fetching page {pages_fetched + 1}: {err}")
                    pagination_info["stopped_early"] = True
                    pagination_info["stop_reason"] = f"API error: {err}"
                    break

                if next_items:
                    all_items.extend(next_items)
                    pages_fetched += 1
                    logger.debug(f"Fetched page {pages_fetched}, total items: {len(all_items)}")
                else:
                    break

            except Exception as e:
                logger.error(f"Exception during pagination on page {pages_fetched + 1}: {e}")
                pagination_info["stopped_early"] = True
                pagination_info["stop_reason"] = f"Exception: {e}"
                break

        if pages_fetched >= max_pages and has_next_page(response):
            pagination_info["stopped_early"] = True
            pagination_info["stop_reason"] = f"Reached maximum page limit ({max_pages})"
            logger.warning(f"Stopped pagination at {max_pages} pages limit")

    except Exception as e:
        logger.error(f"Unexpected error during pagination: {e}")
        pagination_info["stopped_early"] = True
        pagination_info["stop_reason"] = f"Unexpected error: {e}"

    pagination_info["pages_fetched"] = pages_fetched
    pagination_info["total_items"] = len(all_items)

    return all_items, pagination_info


def create_paginated_response(
    items: List, response, fetch_all_used: bool = False, pagination_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a standardized paginated response dict."""
    result: Dict[str, Any] = {
        "items": items,
        "total_fetched": len(items),
        "has_more": False,
        "next_cursor": None,
        "fetch_all_used": fetch_all_used,
    }

    if not fetch_all_used and response:
        cursor = extract_after_cursor(response)
        result["has_more"] = cursor is not None
        result["next_cursor"] = cursor

    if pagination_info:
        result["pagination_info"] = pagination_info

    return result


def build_query_params(
    search: str = "",
    filter: Optional[str] = None,
    q: Optional[str] = None,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Build a query-parameter dict for Okta v3 SDK keyword-argument calls."""
    query_params: Dict[str, Any] = {}

    if search:
        query_params["search"] = search
    if filter:
        query_params["filter"] = filter
    if q:
        query_params["q"] = q
    if after:
        query_params["after"] = after
    if limit:
        query_params["limit"] = limit

    for key, value in kwargs.items():
        if value is not None and value != "":
            query_params[key] = value

    return query_params
