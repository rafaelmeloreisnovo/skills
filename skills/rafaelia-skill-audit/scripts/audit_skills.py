#!/usr/bin/env python3
"""Read-only, dependency-free audit of a repository's Agent Skills catalog."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELD_RE = re.compile(r"^(name|description):\s*(.*)$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
AUTHORIAL_PREFIX = "skills/rafaelia-skill-audit/"


def audit(root):
    root = Path(root).resolve()
    target = root / "skills"
    if not target.is_dir():
        raise ValueError("Missing skills/ directory")
    entries = []
    issues = []
    seen = {}

    def issue(severity, code, path, detail):
        issues.append({"severity": severity, "code": code, "path": path, "detail": detail})

    for skill_file in sorted(target.rglob("SKILL.md")):
        relative = skill_file.relative_to(root).as_posix()
        directory = skill_file.parent
        data = skill_file.read_bytes()
        try:
            body = data.decode("utf-8")
        except UnicodeDecodeError:
            issue("error", "invalid_utf8", relative, "SKILL.md is not UTF-8")
            continue
        attrs = {}
        if not body.startswith("---\n"):
            issue("error", "frontmatter_missing", relative, "YAML frontmatter must start on line 1")
        else:
            match = re.search(r"\n---\s*(?:\n|$)", body[4:])
            if not match:
                issue("error", "frontmatter_unclosed", relative, "Closing --- delimiter missing")
            else:
                header = body[4:4 + match.start()]
                for line in header.splitlines():
                    found = FIELD_RE.match(line)
                    if found:
                        attrs[found.group(1)] = found.group(2).strip().strip('"\'')
        name = attrs.get("name", "")
        description = attrs.get("description", "")
        if not name:
            issue("error", "name_missing", relative, "Required name field missing")
        elif not NAME_RE.fullmatch(name):
            issue("error", "name_invalid", relative, "Name must be lowercase kebab-case")
        elif name != directory.name:
            issue("error", "name_mismatch", relative, "Frontmatter name must match folder")
        if not description:
            issue("error", "description_missing", relative, "Required description missing")
        if name in seen and name:
            issue("error", "name_duplicate", relative, "Duplicate skill name also at " + seen[name])
        if name:
            seen[name] = relative
        licensed = any((directory / n).is_file() for n in ("LICENSE.txt", "LICENSE", "LICENSE.md"))
        if not licensed:
            issue("warning", "license_not_local", relative, "No individual license file found; inspect provenance")
        for raw in LINK_RE.findall(body):
            dest = raw.split()[0].strip("<>")
            if not dest or dest.startswith(("#", "https://", "http://", "mailto:", "data:", "/")):
                continue
            if "$" in dest or "{" in dest:
                continue
            source_path = (directory / unquote(dest.split("#", 1)[0])).resolve()
            try:
                source_path.relative_to(root)
            except ValueError:
                issue("warning", "link_outside_repo", relative, dest)
                continue
            if not source_path.exists():
                issue("warning", "link_missing", relative, dest)
        entries.append({
            "path": directory.relative_to(root).as_posix(),
            "name": name or None,
            "description": description or None,
            "skill_sha256": hashlib.sha256(data).hexdigest(),
            "license_local": licensed,
        })
    if not entries:
        issue("error", "no_skills", "skills/", "No SKILL.md found")
    return {"schema": "rafaelia.skill-audit.v1", "count": len(entries),
            "skills": entries, "issues": sorted(issues, key=lambda x: (x["path"], x["code"]))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy", choices=("report", "authorial", "all"), default="report")
    parser.add_argument("--output-json", help="Optional output path for deterministic JSON catalog")
    args = parser.parse_args(argv)
    try:
        report = audit(args.root)
    except (OSError, ValueError) as exc:
        print("AUDIT_BLOCKED:", exc, file=sys.stderr)
        return 2
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = {s: sum(i["severity"] == s for i in report["issues"]) for s in ("error", "warning")}
    print("skills={count} errors={error} warnings={warning} policy={policy}".format(
        count=report["count"], policy=args.policy, **counts))
    for item in report["issues"]:
        print("{severity}: {code}: {path}: {detail}".format(**item))
    failures = [i for i in report["issues"] if i["severity"] == "error"]
    if args.policy == "authorial":
        failures = [i for i in failures if i["path"].startswith(AUTHORIAL_PREFIX) or i["code"] == "no_skills"]
    if args.policy == "report":
        failures = []
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
