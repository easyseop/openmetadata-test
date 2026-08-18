"""Structured failures for planning workflows."""

from __future__ import annotations


class PlanControlError(RuntimeError):
    """A plan cannot be collected or validated reliably."""

    def __init__(self, code: str, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
