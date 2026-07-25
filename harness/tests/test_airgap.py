"""T94 air-gap inventory and signature verification tests."""
import copy

from acgh import airgap as A
from acgh import verdict as V

_RELEASE = "sha256:" + "a" * 64


def _manifest(tmp_path):
    (tmp_path / "source.bundle").write_bytes(b"git bundle")
    (tmp_path / "image.oci").write_bytes(b"image bytes")
    manifest = A.build_airgap_manifest(
        tmp_path,
        release_lock_digest=_RELEASE,
        source_commit_sha="b" * 40,
        files=[
            {"type": "git-bundle", "path": "source.bundle"},
            {"type": "image", "path": "image.oci"},
        ],
        signature_algorithm="minisign",
        key_identity="offline-release-key",
        signature_path="SHA256SUMS.minisig",
    )
    (tmp_path / "SHA256SUMS.minisig").write_text("signature")
    return manifest


def _verify(tmp_path, manifest, verifier=lambda *args: True, **changes):
    args = {
        "expected_release_lock_digest": _RELEASE,
        "signature_verifier": verifier,
    }
    args.update(changes)
    return A.verify_airgap_bundle(tmp_path, manifest, **args)


def test_all_files_release_lock_and_offline_signature_pass(tmp_path):
    calls = []

    def verifier(digest, path, identity, algorithm):
        calls.append((digest, path.name, identity, algorithm))
        return True

    result = _verify(tmp_path, _manifest(tmp_path), verifier)
    assert result.verdict == V.PASS
    assert calls[0][2:] == ("offline-release-key", "minisign")


def test_missing_verifier_is_analysis_error_not_unsigned_pass(tmp_path):
    result = _verify(tmp_path, _manifest(tmp_path), verifier=None)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "unavailable" in result.reasons[0]


def test_tampered_or_missing_file_blocks(tmp_path):
    manifest = _manifest(tmp_path)
    (tmp_path / "image.oci").write_bytes(b"tampered")
    assert _verify(tmp_path, manifest).verdict == V.BLOCK
    manifest = _manifest(tmp_path)
    (tmp_path / "source.bundle").unlink()
    assert _verify(tmp_path, manifest).verdict == V.BLOCK


def test_stale_release_or_payload_tampering_is_analysis_error(tmp_path):
    manifest = _manifest(tmp_path)
    result = _verify(
        tmp_path,
        manifest,
        expected_release_lock_digest="sha256:" + "0" * 64,
    )
    assert result.verdict == V.ANALYSIS_ERROR
    manifest = copy.deepcopy(_manifest(tmp_path))
    manifest["payload"]["source_commit_sha"] = "0" * 40
    assert _verify(tmp_path, manifest).verdict == V.ANALYSIS_ERROR


def test_bad_signature_blocks_and_verifier_crash_is_analysis_error(tmp_path):
    manifest = _manifest(tmp_path)
    assert _verify(tmp_path, manifest, verifier=lambda *args: False).verdict == V.BLOCK

    def crashing(*args):
        raise RuntimeError("keyring unavailable")

    assert _verify(tmp_path, manifest, verifier=crashing).verdict == V.ANALYSIS_ERROR


def test_unsafe_or_duplicate_paths_are_rejected(tmp_path):
    manifest = _manifest(tmp_path)
    manifest["payload"]["files"][0]["path"] = "../escape"
    assert _verify(tmp_path, manifest).verdict == V.ANALYSIS_ERROR
    manifest = _manifest(tmp_path)
    manifest["payload"]["files"][1]["path"] = manifest["payload"]["files"][0]["path"]
    assert _verify(tmp_path, manifest).verdict == V.ANALYSIS_ERROR
    manifest = _manifest(tmp_path)
    manifest["payload"]["files"][0]["path"] = "nested//file"
    assert _verify(tmp_path, manifest).verdict == V.ANALYSIS_ERROR
