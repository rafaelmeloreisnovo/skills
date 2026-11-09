> [!IMPORTANT]
> **Independent fork / upstream notice.** This repository preserves third-party Agent Skills from [openai/skills](https://github.com/openai/skills). The upstream repository is marked deprecated; current Codex examples have moved to [openai/plugins](https://github.com/openai/plugins). This fork is not an official OpenAI distribution. Imported content and independently authored additions have distinct provenance and rights.

# Agent Skills — fork and authorial extensions

Agent Skills are folders containing instructions, scripts and resources that agents may use for specific tasks. The contents of `skills/.curated/` and `skills/.system/` were inherited from upstream. Their existing instructions, attribution and individual licenses are not replaced by this fork.

## Authorial extension

- [`rafaelia-skill-audit`](skills/rafaelia-skill-audit/SKILL.md): read-only catalog audit, structural checks, license/provenance warnings and deterministic SHA-256 inventory. Standard-library Python; regression tests and an opt-in scoped CI gate. Its own rights notice is in [`LICENSE.txt`](skills/rafaelia-skill-audit/LICENSE.txt).

From the repository root, run:

~~~sh
python3 -m unittest discover -s skills/rafaelia-skill-audit/tests -v
python3 skills/rafaelia-skill-audit/scripts/audit_skills.py --root . --policy report --output-json skill-catalog.json
~~~

The report-only mode does not fail on findings. The CI workflow gates errors in the new authorial skill while reporting existing upstream findings. **A missing per-folder license is a review signal, not a legal conclusion.** Catalog output is a generated report and should not be presented as a test of the runtime behavior or safety of third-party scripts.

To install this authorial skill in a compatible Codex environment, use the skill installer with its directory URL after the branch is merged:

~~~text
https://github.com/rafaelmeloreisnovo/skills/tree/main/skills/rafaelia-skill-audit
~~~

No installation is implied by being present in this fork. The upstream `.system` auto-install behavior applies to supported official Codex distributions, not automatically to a fork.

## Upstream reference and licensing

- [Codex skills documentation](https://developers.openai.com/codex/skills)
- [Create a custom skill](https://developers.openai.com/codex/skills/create-skill)
- [Agent Skills specification](https://agentskills.io)
- [OpenAI Plugins repository](https://github.com/openai/plugins)

Read the license in each imported skill's directory before reuse. The absence of a license file does not authorize redistribution, and this fork does not grant new rights to imported materials. Contributions should document source, exact commit, rights, tests and rollback instructions. See [contributing.md](contributing.md).
