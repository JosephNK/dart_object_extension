"""
dart_object_extension / dart_object_extension_gen 버전 동기화 스크립트.

사용법:
  poetry run sync-version                # 현재 버전 확인
  poetry run sync-version 0.4.0          # 두 패키지를 0.4.0으로 동기화 + CHANGELOG 생성
  poetry run sync-version --check        # 동기화 상태만 확인 (CI용)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from git import Repo
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent

PACKAGES = {
    "dart_object_extension": ROOT / "dart_object_extension" / "pubspec.yaml",
    "dart_object_extension_gen": ROOT / "dart_object_extension_gen" / "pubspec.yaml",
}

CHANGELOG_PATHS = {
    "dart_object_extension": ROOT / "dart_object_extension" / "CHANGELOG.md",
    "dart_object_extension_gen": ROOT / "dart_object_extension_gen" / "CHANGELOG.md",
}

SOURCE_PKG = "dart_object_extension"
GEN_PKG = "dart_object_extension_gen"

SKIP_PATTERNS = (
    "Update Version",
    "Merge branch",
    "Merge pull request",
)


def load_yaml(path: Path) -> tuple[dict, YAML]:
    yaml = YAML()
    yaml.preserve_quotes = True
    data = yaml.load(path)
    return data, yaml


def save_yaml(path: Path, data: dict, yaml: YAML) -> None:
    yaml.dump(data, path)


def get_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name, path in PACKAGES.items():
        data, _ = load_yaml(path)
        versions[name] = str(data["version"])
    return versions


def get_dep_version() -> str | None:
    data, _ = load_yaml(PACKAGES[GEN_PKG])
    deps = data.get("dependencies", {})
    return str(deps.get(SOURCE_PKG, "")) if SOURCE_PKG in deps else None


def print_status() -> None:
    versions = get_versions()
    dep_version = get_dep_version()

    print("Current versions:")
    for name, version in versions.items():
        print(f"  {name}: {version}")

    if dep_version:
        print(f"\n  {GEN_PKG} depends on {SOURCE_PKG}: {dep_version}")

    if versions[SOURCE_PKG] == versions[GEN_PKG]:
        print("\n  [OK] Versions are in sync.")
    else:
        print("\n  [WARN] Versions are out of sync!")


def check_sync() -> bool:
    versions = get_versions()
    dep_version = get_dep_version()
    expected_dep = f"^{versions[SOURCE_PKG]}"

    in_sync = (
        versions[SOURCE_PKG] == versions[GEN_PKG]
        and dep_version == expected_dep
    )

    print_status()
    return in_sync


def find_version_base_ref(repo: Repo, version: str) -> str | None:
    """현재 버전의 기준 커밋(태그 또는 버전 범프 커밋)을 찾는다."""
    for tag in repo.tags:
        if tag.name in (version, f"v{version}"):
            return tag.commit.hexsha

    for commit in repo.iter_commits(max_count=200):
        first_line = commit.message.strip().split("\n")[0]
        if f"Update Version {version}" in first_line:
            return commit.hexsha

    return None


def format_commit_message(msg: str) -> str:
    """커밋 메시지에서 conventional commit 접두사를 제거한다."""
    match = re.match(
        r"^(?:feat|fix|chore|refactor|docs|test|perf|ci|fixed):\s*", msg
    )
    if match:
        return msg[match.end():]
    return msg


def classify_commits(
    repo: Repo, base_ref: str | None,
) -> dict[str, list[str]]:
    """기준 커밋 이후의 변경을 패키지별로 분류한다."""
    result: dict[str, list[str]] = {SOURCE_PKG: [], GEN_PKG: []}

    if base_ref:
        commits = list(repo.iter_commits(f"{base_ref}..HEAD"))
    else:
        commits = list(repo.iter_commits(max_count=50))

    for commit in commits:
        msg = commit.message.strip().split("\n")[0]

        if any(pattern in msg for pattern in SKIP_PATTERNS):
            continue

        if commit.parents:
            diffs = commit.parents[0].diff(commit)
            paths = [d.a_path or d.b_path for d in diffs]
        else:
            paths = []

        touches_source = any(
            p.startswith(f"{SOURCE_PKG}/")
            and not p.startswith(f"{GEN_PKG}/")
            for p in paths
        )
        touches_gen = any(p.startswith(f"{GEN_PKG}/") for p in paths)

        clean_msg = format_commit_message(msg)

        if touches_source:
            result[SOURCE_PKG].append(clean_msg)
        if touches_gen:
            result[GEN_PKG].append(clean_msg)
        if not touches_source and not touches_gen and paths:
            result[SOURCE_PKG].append(clean_msg)
            result[GEN_PKG].append(clean_msg)

    return result


def deduplicate(entries: list[str]) -> list[str]:
    """순서를 유지하면서 중복을 제거한다."""
    seen: set[str] = set()
    unique: list[str] = []
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            unique.append(entry)
    return unique


def update_changelog(pkg_name: str, new_version: str, entries: list[str]) -> None:
    """CHANGELOG.md 상단에 새 버전 섹션을 추가한다."""
    changelog_path = CHANGELOG_PATHS[pkg_name]

    entries = deduplicate(entries)
    if not entries:
        entries = ["Update packages."]

    new_lines = [f"## [{new_version}]", ""]
    for entry in entries:
        new_lines.append(f"- {entry}")
    new_lines.append("")
    new_section = "\n".join(new_lines) + "\n"

    existing = changelog_path.read_text() if changelog_path.exists() else ""

    if f"## [{new_version}]" in existing:
        print(f"  {pkg_name} CHANGELOG.md already has [{new_version}], skipped.")
        return

    changelog_path.write_text(new_section + existing)
    print(f"  {pkg_name} CHANGELOG.md updated ({len(entries)} entries)")


def generate_changelogs(new_version: str) -> None:
    """git log에서 패키지별 변경사항을 추출하여 CHANGELOG를 업데이트한다."""
    print("\nGenerating changelogs ...")

    repo = Repo(ROOT)
    current_version = str(get_versions()[SOURCE_PKG])

    base_ref = find_version_base_ref(repo, current_version)
    if base_ref:
        print(f"  Base ref for {current_version}: {base_ref[:8]}")
    else:
        print(f"  No base ref found for {current_version}, using recent commits.")

    classified = classify_commits(repo, base_ref)

    for pkg_name in (SOURCE_PKG, GEN_PKG):
        entries = classified[pkg_name]
        print(f"\n  {pkg_name}: {len(entries)} commit(s) found")
        for entry in entries:
            print(f"    - {entry}")
        update_changelog(pkg_name, new_version, entries)


def sync_to(new_version: str) -> None:
    print(f"Syncing all packages to version {new_version} ...")

    generate_changelogs(new_version)

    print("\nUpdating pubspec versions ...")

    for name, path in PACKAGES.items():
        data, yaml = load_yaml(path)
        old_version = str(data["version"])
        data["version"] = new_version
        save_yaml(path, data, yaml)
        print(f"  {name}: {old_version} -> {new_version}")

    gen_path = PACKAGES[GEN_PKG]
    data, yaml = load_yaml(gen_path)
    deps = data.get("dependencies", {})
    if SOURCE_PKG in deps:
        old_dep = str(deps[SOURCE_PKG])
        new_dep = f"^{new_version}"
        deps[SOURCE_PKG] = new_dep
        save_yaml(gen_path, data, yaml)
        print(f"\n  {GEN_PKG} dependency {SOURCE_PKG}: {old_dep} -> {new_dep}")

    print("\nDone.")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print_status()
        return

    if args[0] == "--check":
        in_sync = check_sync()
        sys.exit(0 if in_sync else 1)

    new_version = args[0]

    parts = new_version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        print(f"Error: Invalid version format '{new_version}'. Expected: X.Y.Z")
        sys.exit(1)

    sync_to(new_version)


if __name__ == "__main__":
    main()
