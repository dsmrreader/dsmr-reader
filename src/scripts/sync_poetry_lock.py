#!/usr/bin/env python3
"""Regenerate poetry.lock from uv.lock without invoking Poetry's resolver, which can OOM on constrained hosts."""

from __future__ import annotations

import hashlib
import json
import sys
import tomllib
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import tomlkit
from packaging.requirements import Requirement
from packaging.utils import NormalizedName, canonicalize_name
from tomlkit import array, comment, document, inline_table, table

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT / "pyproject.toml"
UV_LOCK_PATH = ROOT / "uv.lock"
POETRY_LOCK_PATH = ROOT / "poetry.lock"

GENERATED_COMMENT = (
    "This file is automatically @generated from uv.lock by scripts/sync_poetry_lock.py "
    "and should not be changed by hand."
)
LOCK_VERSION = "2.1"
PYPI_JSON_URL = "https://pypi.org/pypi/{name}/{version}/json"


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def requirement_names(specs: list[str]) -> set[NormalizedName]:
    return {canonicalize_name(Requirement(spec).name) for spec in specs}


def content_hash(pyproject_data: dict[str, Any]) -> str:
    """Replicates Locker._get_content_hash() from poetry/packages/locker.py exactly."""
    project_content = pyproject_data.get("project", {})
    group_content = pyproject_data.get("dependency-groups", {})
    tool_poetry_content = pyproject_data.get("tool", {}).get("poetry", {})

    relevant_project_keys = ["requires-python", "dependencies", "optional-dependencies"]
    legacy_keys = ["dependencies", "source", "extras", "dev-dependencies"]
    relevant_keys = [*legacy_keys, "group"]

    relevant_project_content = {}
    for key in relevant_project_keys:
        data = project_content.get(key)
        if data is not None:
            relevant_project_content[key] = data

    relevant_poetry_content = {}
    for key in relevant_keys:
        data = tool_poetry_content.get(key)
        if data is None and (key not in legacy_keys or relevant_project_content or group_content):
            continue
        relevant_poetry_content[key] = data

    relevant_content: dict[str, Any] = {}
    if relevant_project_content:
        relevant_content["project"] = relevant_project_content
    if group_content:
        relevant_content["dependency-groups"] = group_content

    if relevant_content:
        relevant_content["tool"] = {"poetry": relevant_poetry_content}
    else:
        relevant_content = relevant_poetry_content

    return hashlib.sha256(json.dumps(relevant_content, sort_keys=True).encode()).hexdigest()


def group_sort_key(group: str) -> tuple[bool, str]:
    return group != "main", group


def reachable(roots: set[NormalizedName], graph: dict[NormalizedName, set[NormalizedName]]) -> set[NormalizedName]:
    seen: set[NormalizedName] = set()
    stack = list(roots)
    while stack:
        name = stack.pop()
        if name in seen or name not in graph:
            continue
        seen.add(name)
        stack.extend(graph[name])
    return seen


def fetch_pypi_metadata(name: str, version: str) -> dict[str, Any]:
    # Fixed https://pypi.org template with no user input, safe despite the non-literal URL.
    url = urllib.request.Request(PYPI_JSON_URL.format(name=name, version=version))
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:  # noqa: S310
            data = json.load(resp)
        info = data.get("info", {})
        return {
            "description": info.get("summary") or "",
            "python-versions": info.get("requires_python") or "*",
            "requires_dist": info.get("requires_dist") or [],
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warning: PyPI metadata lookup failed for {name} {version}: {exc}", file=sys.stderr)
        return {"description": "", "python-versions": "*", "requires_dist": []}


def build_dependency_constraints(
    requires_dist: list[str], locked_names: set[NormalizedName]
) -> dict[str, list[dict[str, Any]]]:
    dependencies: dict[str, list[dict[str, Any]]] = {}
    for raw in requires_dist:
        try:
            req = Requirement(raw)
        except ValueError:
            continue

        marker_str = str(req.marker) if req.marker else ""
        if "extra ==" in marker_str or "extra ==" in marker_str.replace("'", '"'):
            continue  # optional extra we never request

        target = canonicalize_name(req.name)
        if target not in locked_names:
            continue

        constraint: dict[str, Any] = {"version": str(req.specifier) or "*"}
        if req.extras:
            constraint["extras"] = sorted(req.extras)
        if req.marker:
            constraint["markers"] = str(req.marker).replace("'", '"')

        dependencies.setdefault(req.name, []).append(constraint)

    return dependencies


def package_files(pkg: dict[str, Any]) -> list[dict[str, str]]:
    wheels = [{"file": Path(w["url"]).name, "hash": w["hash"]} for w in pkg.get("wheels", [])]
    sdist = [{"file": Path(pkg["sdist"]["url"]).name, "hash": pkg["sdist"]["hash"]}] if "sdist" in pkg else []
    return sorted(wheels + sdist, key=lambda f: f["file"])


def package_groups(
    canon: NormalizedName, main_reachable: set[NormalizedName], dev_reachable: set[NormalizedName]
) -> list[str]:
    groups = []
    if canon in main_reachable:
        groups.append("main")
    if canon in dev_reachable:
        groups.append("dev")
    groups.sort(key=group_sort_key)
    return groups


def build_package_specs(
    packages_by_name: dict[NormalizedName, dict[str, Any]],
    metadata_by_name: dict[NormalizedName, dict[str, Any]],
    main_reachable: set[NormalizedName],
    dev_reachable: set[NormalizedName],
    locked_names: set[NormalizedName],
) -> list[dict[str, Any]]:
    package_specs = []
    for canon in sorted(packages_by_name):
        pkg = packages_by_name[canon]
        meta = metadata_by_name[canon]

        groups = package_groups(canon, main_reachable, dev_reachable)
        if not groups:
            continue  # unreachable from either root set; shouldn't happen since uv only resolves what's needed

        spec: dict[str, Any] = {
            "name": pkg["name"],
            "version": pkg["version"],
            "description": meta["description"],
            "optional": False,
            "python-versions": meta["python-versions"],
            "groups": groups,
            "files": package_files(pkg),
        }

        dependencies = build_dependency_constraints(meta["requires_dist"], locked_names)
        if dependencies:
            spec["dependencies"] = dependencies

        package_specs.append(spec)

    return package_specs


def render_dependency_value(constraints: list[dict[str, Any]]) -> Any:
    if all(set(c) == {"version"} for c in constraints):
        versions = [c["version"] for c in constraints]
        if len(versions) == 1:
            return versions[0]
        value = array().multiline(True)
        for v in versions:
            value.append(v)
        return value

    entries = []
    for c in constraints:
        it = inline_table()
        for k in ("version", "extras", "markers"):
            if k in c:
                it[k] = c[k]
        entries.append(it)
    if len(entries) == 1:
        return entries[0]
    value = array().multiline(True)
    for e in entries:
        value.append(e)
    return value


def render_package_table(spec: dict[str, Any]) -> Any:
    pkg_table = table()
    pkg_table["name"] = spec["name"]
    pkg_table["version"] = spec["version"]
    pkg_table["description"] = spec["description"]
    pkg_table["optional"] = spec["optional"]
    pkg_table["python-versions"] = spec["python-versions"]
    pkg_table["groups"] = spec["groups"]

    files_array = array().multiline(True)
    for f in spec["files"]:
        file_entry = inline_table()
        file_entry["file"] = f["file"]
        file_entry["hash"] = f["hash"]
        files_array.append(file_entry)
    pkg_table["files"] = files_array

    if "dependencies" in spec:
        deps_table = table()
        for dep_name, constraints in sorted(spec["dependencies"].items()):
            deps_table[dep_name] = render_dependency_value(constraints)
        pkg_table["dependencies"] = deps_table

    return pkg_table


def main() -> None:
    pyproject_data = load_toml(PYPROJECT_PATH)
    uv_lock = load_toml(UV_LOCK_PATH)

    main_roots = requirement_names(pyproject_data["project"]["dependencies"])
    dev_roots = requirement_names(pyproject_data["dependency-groups"]["dev"])

    uv_packages = [p for p in uv_lock["package"] if p.get("source", {}).get("virtual") is None]

    packages_by_name: dict[NormalizedName, dict[str, Any]] = {}
    graph: dict[NormalizedName, set[NormalizedName]] = {}
    for pkg in uv_packages:
        canon = canonicalize_name(pkg["name"])
        packages_by_name[canon] = pkg
        graph[canon] = {canonicalize_name(dep["name"]) for dep in pkg.get("dependencies", [])}

    main_reachable = reachable(main_roots, graph)
    dev_reachable = reachable(dev_roots, graph)
    locked_names = set(packages_by_name)

    print(f"Fetching PyPI metadata for {len(uv_packages)} packages...", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=8) as pool:
        metadata_list = list(pool.map(lambda p: fetch_pypi_metadata(p["name"], p["version"]), uv_packages))
    metadata_by_name = {canonicalize_name(p["name"]): m for p, m in zip(uv_packages, metadata_list)}

    package_specs = build_package_specs(packages_by_name, metadata_by_name, main_reachable, dev_reachable, locked_names)

    lock = document()
    lock.add(comment(GENERATED_COMMENT))

    package_aot = tomlkit.aot()
    for spec in package_specs:
        package_aot.append(render_package_table(spec))
    lock["package"] = package_aot

    lock["metadata"] = {
        "lock-version": LOCK_VERSION,
        "python-versions": pyproject_data["project"]["requires-python"],
        "content-hash": content_hash(pyproject_data),
    }

    POETRY_LOCK_PATH.write_text(tomlkit.dumps(lock), encoding="utf-8")
    print(f"Wrote {POETRY_LOCK_PATH} ({len(package_specs)} packages)", file=sys.stderr)


if __name__ == "__main__":
    main()
