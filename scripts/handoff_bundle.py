"""Create/verify a data-only handoff snapshot; never overwrite changed local data.

Secret scanning is a separate required step before uploading a bundle. This
allowlist excludes credentials and scratch code, but cannot recognize all secrets
someone might accidentally put inside an otherwise legitimate data file.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

MANIFEST = ".handoff/data-manifest.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if (path.is_absolute() or ".." in path.parts or "\\" in name
            or not path.parts or ":" in path.parts[0] or path.as_posix() != name):
        raise ValueError(f"Unsafe archive path: {name}")
    return path


def selected_files(root: Path) -> list[Path]:
    paths = []
    for folder in ("data", "output"):
        for path in (root / folder).rglob("*"):
            relative = path.relative_to(root)
            if any(part.startswith(("handoff", "_dev")) for part in relative.parts[1:]):
                continue
            if path.is_symlink():
                raise ValueError(f"Symlinks are not included: {relative}")
            if not path.is_file() or path.name == ".DS_Store":
                continue
            if (path.name.lower().startswith((".env", "credentials", "service-account"))
                    or path.suffix.lower() in {".pem", ".key"}):
                raise ValueError(f"Credential-like filename: {relative}")
            paths.append(path)
    paths.extend((root / "tmp" / "pdfs").glob("*.pdf"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Source scan cannot be a symlink")
    return sorted(paths)


def _add(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))


def pack(root: Path, destination: Path) -> dict:
    root = root.resolve()
    paths = selected_files(root)
    if destination.resolve() in paths:
        raise ValueError("Bundle destination is also an input")
    manifest = {"version": 1, "created_utc": datetime.now(timezone.utc).isoformat(), "files": {}}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle, tarfile.open(fileobj=handle, mode="w:gz") as archive:
        for path in paths:
            name = path.relative_to(root).as_posix()
            safe_name(name)
            data = path.read_bytes()
            manifest["files"][name] = {"sha256": digest(data), "bytes": len(data)}
            _add(archive, name, data)
        _add(archive, MANIFEST, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    return {"files": len(paths), "archive": str(destination), "sha256": digest(destination.read_bytes())}


def verify(bundle: Path, extract_to: Path | None = None) -> dict:
    root = extract_to.resolve() if extract_to is not None else None
    with tarfile.open(bundle, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or MANIFEST not in names:
            raise ValueError("Missing manifest or duplicate archive members")
        for member in members:
            safe_name(member.name)
            if not member.isfile():
                raise ValueError(f"Non-regular archive member: {member.name}")
        manifest = json.load(archive.extractfile(MANIFEST))
        if manifest.get("version") != 1 or set(names) != set(manifest["files"]) | {MANIFEST}:
            raise ValueError("Manifest does not match archive members")
        # Check the entire snapshot and all destination conflicts before writing.
        for name, expected in manifest["files"].items():
            data = archive.extractfile(name).read()
            if digest(data) != expected["sha256"] or len(data) != expected["bytes"]:
                raise ValueError(f"Hash/size mismatch: {name}")
            if root is not None:
                target = root / name
                if target.is_symlink() or not target.resolve().is_relative_to(root):
                    raise ValueError(f"Unsafe destination: {name}")
                if any(parent.exists() and not parent.is_dir()
                       for parent in target.parents if parent.is_relative_to(root)):
                    raise ValueError(f"Destination parent is not a directory: {name}")
                if target.exists() and (not target.is_file() or digest(target.read_bytes()) != expected["sha256"]):
                    raise ValueError(f"Refusing to overwrite changed local file: {name}")
        restored = 0
        if root is not None:
            for name in manifest["files"]:
                target = root / name
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as handle:
                        handle.write(archive.extractfile(name).read())
                    restored += 1
    return {"verified_files": len(manifest["files"]), "restored_files": restored,
            "created_utc": manifest["created_utc"], "sha256": digest(bundle.read_bytes())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("pack")
    create.add_argument("destination", type=Path)
    create.add_argument("--root", type=Path, default=Path("."))
    check = commands.add_parser("verify")
    check.add_argument("bundle", type=Path)
    check.add_argument("--extract-to", type=Path)
    args = parser.parse_args()
    result = pack(args.root, args.destination) if args.command == "pack" else verify(args.bundle, args.extract_to)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
