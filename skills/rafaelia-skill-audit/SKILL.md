---
name: rafaelia-skill-audit
description: Audit Agent Skills repositories for metadata, local references, provenance and license gaps; produce deterministic inventories and evidence-first, reversible remediation plans. Use for skill catalog improvements, review, ingestion, or migration, not to silently install or rewrite third-party skills.
---

# RAFAELIA Skill Audit

Audit first; change only what the repository owner authorized. Treat SOURCE, ARTIFACT, EXECUTION, EVIDENCE and CLAIM as distinct states.

## Procedure

1. Resolve repository, exact branch/commit, ownership and target; read only `SKILL.md` and relevant navigation files before expanding.
2. Run the read-only auditor from the repository root: `python3 skills/rafaelia-skill-audit/scripts/audit_skills.py --root . --policy report --output-json /tmp/skill-catalog.json`.
3. Classify findings: **ERROR** (structural issue), **WARNING** (requires human verification), **TOKEN_VAZIO** (unobserved). Missing local license is a warning, never proof of infringement.
4. Preserve upstream content, copyrights and per-skill licenses. Put genuinely new, independently authored skills in their own folders; do not relabel imported code as original.
5. Propose minimal, reversible patches on a separate branch. Do not delete files, execute untrusted bundled scripts, install packages or publish results without authorization.
6. Run unit tests with `python3 -m unittest discover -s skills/rafaelia-skill-audit/tests -v`; run auditor with `--policy authorial` to gate only this new skill or `--policy all` after reviewing historic findings.
7. Record repository/commit, exact commands, output, failures, remaining gaps and rollback path in the PR. Passing tests establish only the tested scope, not runtime safety of every skill.

## Controls

- The auditor uses Python standard library, reads `skills/` and hashes each `SKILL.md`. It never loads, imports or executes candidate skills.
- JSON catalog is deterministic for unchanged paths and bytes; the report is not a cryptographic attestation of the whole repository.
- A missing item is not zero. Treat unknown author, upstream, runtime or license as **TOKEN_VAZIO** until verified.
- Avoid making all legacy warnings merge blockers during first adoption. Escalate severity after evidence and review.

Finish substantial work with `R3 = <F_ok, F_gap, F_next>`.
