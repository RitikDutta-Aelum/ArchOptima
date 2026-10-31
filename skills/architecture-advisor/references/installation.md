# Installation and harness compatibility

Contents: [Compatibility](#compatibility) · [GitHub installation](#install-from-a-downloaded-github-repository) · [Custom directories](#use-a-custom-skills-directory) · [Verification](#verify-the-installation) · [Manual hosts](#hosts-without-native-skill-support) · [Updates](#updating-and-removing)

This package follows the [Agent Skills format](https://agentskills.io/specification): one `architecture-advisor` folder containing `SKILL.md` and its supporting files. Install the **whole folder** so references and scripts remain available. The skill does not supply a model, a terminal, vision, document rendering, or API access; those capabilities come from the host.

## Compatibility

These local discovery paths were checked against official documentation on **31 October 2026**. Availability in a hosted or remote session depends on that host's configuration and policies; installing on your laptop does not automatically install into a cloud runner.

| Installer preset | Project skills parent | User skills parent | Invocation or discovery |
|---|---|---|---|
| `codex` | `.agents/skills/` | `~/.agents/skills/` | `/skills` or `$architecture-advisor` |
| `claude` | `.claude/skills/` | `~/.claude/skills/` | `/architecture-advisor` |
| `cursor` | `.cursor/skills/` | `~/.cursor/skills/` | Search for the skill in the `/` menu |
| `copilot` | `.github/skills/` | `~/.copilot/skills/` | Ask Copilot to use the skill; discovery depends on the Copilot surface |
| `gemini` | `.gemini/skills/` | `~/.gemini/skills/` | `/skills list`, then request the skill by name |
| `agents` | `.agents/skills/` | `~/.agents/skills/` | For a host whose documentation confirms this shared path |

Every destination above receives a child directory named `architecture-advisor`. Avoid installing duplicate copies into several discovery roots of the same host. Follow your organization's workspace trust and script execution policies.

Official sources:

- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Cursor: Agent Skills](https://cursor.com/docs/skills)
- [GitHub Copilot: Add skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [Gemini CLI: Agent Skills](https://geminicli.com/docs/cli/skills/)

## Direct installation after GitHub publication

With the optional third-party Skills CLI and Node.js 22.20 or later, run from the target project:

    npx skills add OWNER/REPO --skill architecture-advisor

Choose the target agent in the CLI. To select Codex explicitly and copy files:

    npx skills add OWNER/REPO --skill architecture-advisor --agent codex --copy

For Claude Code use --agent claude-code. Add --global for a user-level installation. Use --list to inspect repository discovery before installing. The Skills CLI is an optional external installer with its own behavior; it is not part of this package. It does not install the Python helper dependencies. Its supported agents and requirements may change; verify its current documentation. The local Python installer below provides a separately tested alternative without Node.js.

Primary documentation: https://github.com/vercel-labs/skills/blob/main/README.md and https://github.com/vercel-labs/skills/blob/main/docs/commands.md (checked 31 October 2026).

## Install from a downloaded GitHub repository

Use Python 3.10 or later. Installing the skill files needs no Python packages and does not install dependencies. The examples assume the repository contains `skills/architecture-advisor/`.

Clone the repository, replacing the placeholder owner and repository:

```bash
git clone https://github.com/OWNER/REPO.git architecture-advisor-skill
cd architecture-advisor-skill
```

Preview a project install on macOS or Linux:

```bash
python3 skills/architecture-advisor/scripts/install.py --harness codex --scope project --project /absolute/path/to/your-project --dry-run
```

Apply that install:

```bash
python3 skills/architecture-advisor/scripts/install.py --harness codex --scope project --project /absolute/path/to/your-project --apply
```

On Windows PowerShell, use the Python launcher and quote paths containing spaces:

```powershell
py -3 skills/architecture-advisor/scripts/install.py --harness claude --scope project --project "C:\Projects\My Application" --dry-run
py -3 skills/architecture-advisor/scripts/install.py --harness claude --scope project --project "C:\Projects\My Application" --apply
```

Change `--harness` to the preset in the table. Project scope requires an existing, explicit `--project` directory, avoiding an accidental install into the downloaded skill repository.

For a local user install shared across projects:

```bash
python3 skills/architecture-advisor/scripts/install.py --harness cursor --scope user --apply
```

The default mode is preview. `--dry-run` makes that intent explicit; `--apply` performs the copy. The output prints the exact resolved source and destination. The installer refuses an existing destination and never downloads or executes remote content. It excludes Git metadata, virtual environments, and Python caches from the copy.

## Use a custom skills directory

For another compatible host, supply the **parent directory that holds individual skills**:

```bash
python3 skills/architecture-advisor/scripts/install.py --target /path/to/custom/skills --apply
```

This creates `/path/to/custom/skills/architecture-advisor/SKILL.md`. Do not include the final `architecture-advisor` directory in `--target`. The custom target cannot be combined with a harness preset or project location. A custom directory is not automatically discoverable: configure your host according to its own documentation.

## Verify the installation

1. Confirm `SKILL.md`, `references/`, `assets/`, and `scripts/` exist under the destination shown by the installer.
2. Use the host's skill list or selection menu where available. Gemini CLI provides `/skills reload` to refresh discovery. For other hosts, refresh the skill selector or open a new session if needed.
3. Ask: `Use architecture-advisor to review the attached architecture and give a decision-oriented report with evidence, assumptions, alternatives, cost implications, and next actions.`
4. Ensure the host can access the attachments and the scripts. Scripts are optional when the task only needs an evidence-based narrative review.

Install Python dependencies separately in a virtual environment only if you will use the document or optimization helpers. Consult the repository README and dependency files for the exact optional capabilities; the installer does not install packages or grant permissions.

## Hosts without native skill support

The same material can serve as an instruction package if the host lets you attach instructions and files. Load `SKILL.md`, make its referenced files available, and tell the model to use the workflow. This is **manual use**, not automatic skill discovery. If the host cannot read attachments or run scripts, use its available document tools or provide extracted text and state the limitation. Uploading the skill alone does not add those capabilities.

## Updating and removing

The installer intentionally does not replace an existing installation. To update, compare the new package with the installed copy, move the old copy to a backup **outside all skill discovery roots**, then install the reviewed replacement. This preserves local modifications and avoids duplicate activation. Remove only the installed `architecture-advisor` folder to uninstall; do not delete the parent skills directory or other skills.

The installation performs local file copying only. It does not publish a GitHub repository, configure a marketplace, connect accounts, execute cloud changes, or make the skill available in unrelated hosted sessions.
