# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2026-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

"""Regression tests for the pagination adapter that wraps okta.pagination."""

from __future__ import annotations

from unittest.mock import MagicMock

from okta_mcp_server.utils.pagination import (
    create_paginated_response,
    extract_after_cursor,
    has_next_page,
)


def _resp_with_link(link_value: str | None) -> MagicMock:
    r = MagicMock()
    r.headers = {"Link": link_value} if link_value else {}
    return r


def test_extract_after_cursor_returns_cursor_when_link_has_next():
    r = _resp_with_link('<https://x.okta.com/api/v1/users?after=abc123>; rel="next"')
    assert extract_after_cursor(r) == "abc123"


def test_extract_after_cursor_returns_none_when_no_next_rel():
    r = _resp_with_link('<https://x.okta.com/api/v1/users?after=abc>; rel="self"')
    assert extract_after_cursor(r) is None


def test_extract_after_cursor_handles_missing_response():
    assert extract_after_cursor(None) is None
    assert extract_after_cursor(MagicMock(headers=None)) is None


def test_has_next_page_true_when_cursor_present():
    r = _resp_with_link('<https://x.okta.com/api/v1/users?after=zz>; rel="next"')
    assert has_next_page(r) is True


def test_has_next_page_false_when_no_cursor():
    assert has_next_page(_resp_with_link(None)) is False


def test_create_paginated_response_attaches_cursor_when_more():
    r = _resp_with_link('<https://x.okta.com/api/v1/users?after=cur1>; rel="next"')
    out = create_paginated_response([{"id": "1"}], r)
    assert out["has_more"] is True
    assert out["next_cursor"] == "cur1"
    assert out["fetch_all_used"] is False
    assert out["total_fetched"] == 1


def test_create_paginated_response_omits_cursor_when_fetch_all():
    r = _resp_with_link('<https://x.okta.com/api/v1/users?after=cur1>; rel="next"')
    out = create_paginated_response([{"id": "1"}], r, fetch_all_used=True)
    assert out["fetch_all_used"] is True
    assert out["has_more"] is False
    assert out["next_cursor"] is None
