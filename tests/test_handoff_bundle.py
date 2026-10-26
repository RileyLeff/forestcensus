import importlib.util
import json
from pathlib import Path
import tarfile

import pytest

spec = importlib.util.spec_from_file_location("handoff_bundle", Path(__file__).parents[1] / "scripts/handoff_bundle.py")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def test_bundle_round_trip_and_no_overwrite(tmp_path):
    source = tmp_path / "source"
    (source / "output" / "run").mkdir(parents=True)
    (source / "output" / "run" / "review_decisions.jsonl").write_text('{"action":"edit"}\n')
    (source / ".env").write_text("EXAMPLE=not-for-export")
    (source / "output" / "_dev_fixture").mkdir()
    (source / "output" / "_dev_fixture" / "fake.csv").write_text("fake")
    archive = tmp_path / "bundle.tar.gz"
    assert bundle.pack(source, archive)["files"] == 1
    target = tmp_path / "restored"
    assert bundle.verify(archive, target)["restored_files"] == 1
    assert bundle.verify(archive, target)["restored_files"] == 0
    assert not (target / ".env").exists()
    (target / "output" / "run" / "review_decisions.jsonl").write_text("new edits")
    with pytest.raises(ValueError, match="overwrite"):
        bundle.verify(archive, target)
    assert (target / "output" / "run" / "review_decisions.jsonl").read_text() == "new edits"


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a/../../escape", "a\\b", "C:/x", "a//b"])
def test_unsafe_paths(name):
    with pytest.raises(ValueError, match="Unsafe"):
        bundle.safe_name(name)


def test_tampered_content_rejected_before_any_restore(tmp_path):
    archive = tmp_path / "bad.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        bundle._add(tar, "output/a", b"valid")
        bundle._add(tar, "output/b", b"changed")
        manifest = {"version": 1, "files": {
            "output/a": {"sha256": bundle.digest(b"valid"), "bytes": 5},
            "output/b": {"sha256": bundle.digest(b"original"), "bytes": 8},
        }}
        bundle._add(tar, bundle.MANIFEST, json.dumps(manifest).encode())
    destination = tmp_path / "restored"
    with pytest.raises(ValueError, match="Hash/size"):
        bundle.verify(archive, destination)
    assert not destination.exists()


def test_symlink_member_rejected(tmp_path):
    archive = tmp_path / "link.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("output/link")
        info.type = tarfile.SYMTYPE
        info.linkname = "../../escape"
        tar.addfile(info)
        bundle._add(tar, bundle.MANIFEST, b"{}")
    with pytest.raises(ValueError, match="Non-regular"):
        bundle.verify(archive)


def test_symlink_destination_rejected(tmp_path):
    source = tmp_path / "source"
    (source / "output").mkdir(parents=True)
    (source / "output" / "a").write_text("valid")
    archive = tmp_path / "data.tar.gz"
    bundle.pack(source, archive)
    destination = tmp_path / "restored"
    destination.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (destination / "output").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match="Unsafe destination"):
        bundle.verify(archive, destination)
    assert not (elsewhere / "a").exists()
