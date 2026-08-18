"""Shared fixtures. Real OpenMetadata content comes from the fixed mirror."""
import os
import subprocess
from pathlib import Path

import pytest

_MIRROR = Path(os.environ.get("OM_MIRROR_PATH", "/home/user/om-mirror"))
_AUTH_PATH = (
    "openmetadata-service/src/main/java/org/openmetadata/service/"
    "security/AuthLoginServlet.java"
)


@pytest.fixture(scope="session")
def om_mirror():
    if not (_MIRROR / "HEAD").exists() and not (_MIRROR / ".git").exists():
        pytest.skip(f"OM mirror not present at {_MIRROR}")
    probe = subprocess.run(
        ["git", "-C", str(_MIRROR), "rev-parse", "UPSTREAM_A^{commit}"],
        capture_output=True, text=True,
    )
    if probe.returncode != 0:
        pytest.skip("OM mirror missing UPSTREAM_A tag")
    return _MIRROR


@pytest.fixture(scope="session")
def om_auth_path():
    return _AUTH_PATH


@pytest.fixture(scope="session")
def om_auth_content(om_mirror):
    """Real AuthLoginServlet.java content at 1.12.13 (on-demand blob fetch)."""
    r = subprocess.run(
        ["git", "-C", str(om_mirror), "cat-file", "-p", f"UPSTREAM_A:{_AUTH_PATH}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        pytest.skip("OM auth blob not materializable (offline?)")
    return r.stdout
