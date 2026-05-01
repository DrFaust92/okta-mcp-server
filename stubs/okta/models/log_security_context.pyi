"""Stub for okta.models.log_security_context — used for the userBehaviors monkey-patch."""

from typing import Any, ClassVar

class LogSecurityContext:
    model_fields: ClassVar[dict[str, Any]]

    @classmethod
    def model_rebuild(cls, *, force: bool = ...) -> Any: ...
