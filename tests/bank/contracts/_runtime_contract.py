"""Runtime helpers for bank contracts that need a live OpenMetadata stack."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

import pytest


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} is required for this live contract")
    return value


@dataclass(frozen=True)
class ApiClient:
    base_url: str
    token: str | None

    @classmethod
    def from_env(cls) -> "ApiClient":
        return cls(
            required_env("OPENMETADATA_BASE_URL").rstrip("/"),
            os.environ.get("OPENMETADATA_AUTH_TOKEN"),
        )

    def request(self, method: str, path: str, body=None):
        headers = {"Accept": "application/json"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            pytest.fail(f"{method} {path} returned {exc.code}: {detail}")
        except urllib.error.URLError as exc:
            pytest.fail(f"{method} {path} could not connect: {exc}")

    def get(self, path: str):
        return self.request("GET", path)

    def post(self, path: str, body):
        return self.request("POST", path, body)

    def put(self, path: str, body):
        return self.request("PUT", path, body)

    def delete(self, path: str):
        return self.request("DELETE", path)


def encoded(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def wait_for(predicate, *, timeout: float = 30.0, interval: float = 1.0):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    pytest.fail(f"condition was not met within {timeout}s; last={last!r}")
