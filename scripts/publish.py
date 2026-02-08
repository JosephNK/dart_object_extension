"""
dart_object_extension 모노레포 순차 배포 스크립트.

dart_object_extension → pub.dev 반영 대기 → dart_object_extension_gen 순서로 배포한다.

사용법:
  poetry run publish                # 순차 배포 (확인 프롬프트 포함)
  poetry run publish --dry-run      # dry-run만 실행 (실제 배포 안 함)
  poetry run publish --force        # 확인 없이 바로 배포
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent

PACKAGES = [
    ("dart_object_extension", ROOT / "dart_object_extension"),
    ("dart_object_extension_gen", ROOT / "dart_object_extension_gen"),
]

PUB_API_URL = "https://pub.dev/api/packages"
POLL_INTERVAL = 10
POLL_TIMEOUT = 300


def load_pubspec(pkg_dir: Path) -> dict:
    yaml = YAML()
    yaml.preserve_quotes = True
    return yaml.load(pkg_dir / "pubspec.yaml")


def get_version(pkg_dir: Path) -> str:
    return str(load_pubspec(pkg_dir)["version"])


def check_version_sync() -> str:
    versions = {name: get_version(path) for name, path in PACKAGES}

    print("Version check:")
    for name, version in versions.items():
        print(f"  {name}: {version}")

    unique = set(versions.values())
    if len(unique) != 1:
        print("\n[ERROR] Versions are out of sync! Run: poetry run sync-version <version>")
        sys.exit(1)

    version = unique.pop()
    print(f"\n  [OK] All packages at {version}")
    return version


def run_flutter(pkg_dir: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["flutter", "pub", *args],
        cwd=pkg_dir,
        capture_output=True,
        text=True,
    )


def dry_run(name: str, pkg_dir: Path) -> bool:
    print(f"\n[dry-run] {name} ...")
    result = run_flutter(pkg_dir, ["publish", "--dry-run"])
    combined = result.stdout + "\n" + result.stderr

    has_error = "Package validation found the following error" in combined
    has_warning = "Package has" in combined and "warning" in combined
    validation_ran = "Validating package" in combined

    if has_error:
        print(f"  [FAIL] {name} dry-run failed:")
        print(combined)
        return False

    if validation_ran and has_warning:
        print(f"  [WARN] {name} dry-run passed with warnings:")
        for line in combined.splitlines():
            if "warning" in line.lower() or "modified" in line.lower() or "*" in line:
                print(f"    {line.strip()}")
        return True

    if validation_ran and not has_error:
        print(f"  [OK] {name} dry-run passed.")
        return True

    if result.returncode != 0:
        print(f"  [FAIL] {name} dry-run failed:")
        print(combined)
        return False

    print(f"  [OK] {name} dry-run passed.")
    return True


def publish_package(name: str, pkg_dir: Path, force: bool) -> bool:
    print(f"\n[publish] {name} ...")
    args = ["publish"]
    if force:
        args.append("--force")

    result = subprocess.run(
        ["flutter", "pub", *args],
        cwd=pkg_dir,
    )

    if result.returncode != 0:
        print(f"  [FAIL] {name} publish failed.")
        return False

    print(f"  [OK] {name} published.")
    return True


def fetch_pub_versions(package_name: str) -> list[str]:
    url = f"{PUB_API_URL}/{package_name}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return [v["version"] for v in data.get("versions", [])]
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return []


def wait_for_pub(package_name: str, version: str) -> bool:
    print(f"\n[wait] Waiting for {package_name} {version} on pub.dev ...")
    print(f"  (timeout: {POLL_TIMEOUT}s, interval: {POLL_INTERVAL}s)")

    elapsed = 0
    while elapsed < POLL_TIMEOUT:
        versions = fetch_pub_versions(package_name)
        if version in versions:
            print(f"  [OK] {package_name} {version} is live on pub.dev!")
            return True

        remaining = POLL_TIMEOUT - elapsed
        print(f"  Not yet available. Retrying in {POLL_INTERVAL}s ... ({remaining}s remaining)")
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    print(f"  [TIMEOUT] {package_name} {version} not found after {POLL_TIMEOUT}s.")
    return False


def confirm(message: str) -> bool:
    answer = input(f"\n{message} (y/N): ").strip().lower()
    return answer in ("y", "yes")


def main() -> None:
    args = set(sys.argv[1:])
    is_dry_run = "--dry-run" in args
    force = "--force" in args

    version = check_version_sync()

    source_name, source_dir = PACKAGES[0]
    gen_name, gen_dir = PACKAGES[1]

    if not force:
        ok = dry_run(source_name, source_dir) and dry_run(gen_name, gen_dir)
        if not ok:
            print("\n[ABORT] Fix dry-run errors before publishing.")
            sys.exit(1)

    if is_dry_run:
        print("\n[dry-run] All checks passed. No packages were published.")
        return

    if not force and not confirm(f"Publish both packages at version {version}?"):
        print("\n[ABORT] Cancelled by user.")
        return

    if not publish_package(source_name, source_dir, force):
        sys.exit(1)

    if not wait_for_pub(source_name, version):
        print(f"\n[WARN] {source_name} {version} not detected on pub.dev yet.")
        if not force and not confirm(f"Continue publishing {gen_name} anyway?"):
            print("\n[ABORT] Cancelled. Publish {gen_name} manually later.")
            sys.exit(1)

    print(f"\n[pub-get] {gen_name} ...")
    pub_get_result = run_flutter(gen_dir, ["get"])
    if pub_get_result.returncode != 0:
        print(f"  [FAIL] {gen_name} pub get failed:")
        print(pub_get_result.stdout + "\n" + pub_get_result.stderr)
        sys.exit(1)
    print(f"  [OK] {gen_name} dependencies updated.")

    if not publish_package(gen_name, gen_dir, force):
        sys.exit(1)

    print(f"\n[DONE] Both packages published at version {version}.")


if __name__ == "__main__":
    main()
