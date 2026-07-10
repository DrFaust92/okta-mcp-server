"""Stub for okta.api_client.ApiClient — minimal surface used by okta_compat.

Only the members touched by the lenient-deserialization shim (and its tests) are
declared. ``_ApiClient__deserialize_model`` is the name-mangled internal hook
that ``okta_compat.apply_okta_sdk_leniency`` wraps.
"""

from typing import Any

class ApiClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def deserialize(self, response_text: str, response_type: Any) -> Any: ...
    def _ApiClient__deserialize_model(self, data: Any, klass: Any) -> Any: ...
