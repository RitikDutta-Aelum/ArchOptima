# Architecture Advisor

Contents: [Codex installation](#install-in-codex-from-github) · [Downloaded package](#install-a-downloaded-package-in-codex) · [Capabilities](#what-the-skill-delivers) · [Alternative installers](#alternative-install-editable-skill-files) · [Use](#use-the-skill) · [Helpers](#local-helper-setup) · [Validate](#validate-and-contribute) · [Publish](#publish-this-repository)

A portable Agent Skill for professional architecture reviews, design comparisons, resource planning, and cost analysis. It accepts the user's question together with architecture diagrams, screenshots, PDFs, and other supported documents, then guides the host agent to produce an evidence-based report for architects.

The review workflow applies to general application and cloud architecture, with a ServiceNow-specific reference for platform boundaries, integration choices, entitlements, MID Servers, and external infrastructure. It keeps observed facts, assumptions, estimates, and recommendations separate.

**Distribution/plugin release: 1.1.0. Bundled core skill: 1.0.0.** This release adds native Codex marketplace packaging. The core skill files remain byte-identical to the original 1.0.0 release, and the installed skill identifier remains `architecture-advisor`.

## Install in Codex from GitHub

After publishing this repository, replace `OWNER/REPO` with its GitHub owner and repository name. Run these commands in a terminal or PowerShell session where the Codex CLI is available:

```powershell
codex plugin marketplace add OWNER/REPO
codex plugin add architecture-advisor@architecture-tools
codex plugin list
```

The first command registers the repository's marketplace. The second installs its `architecture-advisor` plugin from the marketplace named `architecture-tools`. The third lists the actual installed plugins so you can check the result. These are terminal commands, rather than text to paste as an ordinary architecture question. If your Codex version does not recognize the plugin commands, check `codex plugin --help` and update your Codex installation using its documented method.

The repository contains the complete marketplace and plugin metadata; no separate public-directory submission is needed for this repository installation route. Keep `.agents/plugins/marketplace.json`, `plugin.json`, `.codex-plugin/plugin.json`, and `skills/architecture-advisor/` together at the repository root.

Choose **one installation route** for this skill in a given Codex environment. Installing both the plugin and a copied skill can expose duplicate copies. Plugin installation supplies the skill and its bundled scripts; the optional Python dependencies are configured separately in [Local helper setup](#local-helper-setup).

Official references: [Codex developer commands](https://learn.chatgpt.com/docs/developer-commands) and [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), checked 31 October 2026.

### Refresh a registered Git marketplace

After the publisher releases a new version:

```powershell
codex plugin marketplace upgrade architecture-tools
codex plugin list
```

The upgrade command refreshes the configured Git marketplace. Inspect the installed version and the CLI's reported result; this guide does not promise a particular automatic-update schedule.

## Install a downloaded package in Codex

Extract the release and open a terminal in the extracted package root, where `plugin.json` and `skills/` are visible. For example, in Windows PowerShell, replace the example path with your actual extracted folder:

```powershell
Set-Location "C:\Downloads\architecture-advisor-codex-v1.1.0"
codex plugin marketplace add .
codex plugin add architecture-advisor@architecture-tools
codex plugin list
```

On macOS or Linux, change into the extracted folder with `cd` and run the same three `codex` commands. A local-directory marketplace uses the supplied local package; it is not a subscription to a future GitHub repository. Use the GitHub route above when that is your intended source.

## What the skill delivers

- An executive decision and concise assessment of the proposed or existing architecture.
- A documented current-state model with source references and uncertainty.
- Findings tied to consequences, priority, and recommended action.
- Feasible alternatives with explicit requirements and trade-offs.
- Cost and resource analysis when usable inputs are supplied.
- A proposed target architecture, implementation sequence, and validation criteria where relevant.

The skill does not promise a universally best architecture, guaranteed savings, or a practical implementation of a new complexity-theory result. Its calculations and solver results apply to the supplied model and assumptions.

## Alternative: install editable skill files

The optional third-party Skills CLI provides a separate installation route for Codex and other supported harnesses. For a user-level Codex installation after GitHub publication:

```powershell
npx skills add OWNER/REPO --agent codex --skill architecture-advisor --global --copy
```

Omit `--global` to install into the current project. To choose the target agent interactively:

    npx skills add OWNER/REPO --skill architecture-advisor

For Claude Code use `--agent claude-code`. Replace `OWNER/REPO` with your published GitHub identity. This optional CLI currently requires Node.js 22.20+. It installs skill files, not Python dependencies. See the [official CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) and [requirements](https://github.com/vercel-labs/skills/blob/main/README.md). The standard `skills/architecture-advisor` layout is discoverable by this workflow; remote installation can only be exercised after publication. Choose this route or the native Codex plugin route, rather than installing both copies into one environment.

For installation without Node.js, use the bundled Python installer below.

## Python installer for local skill files

The repository layout is `skills/architecture-advisor/`. Install the complete folder, including its scripts and references.

Clone your published repository:

```bash
git clone https://github.com/OWNER/REPO.git architecture-advisor-skill
cd architecture-advisor-skill
```

Replace `OWNER/REPO` with your GitHub repository. Review a release tag or commit before installing it.

### macOS and Linux

Preview the destination, then install into an existing project:

```bash
python3 skills/architecture-advisor/scripts/install.py --harness codex --scope project --project /absolute/path/to/your-project --dry-run
python3 skills/architecture-advisor/scripts/install.py --harness codex --scope project --project /absolute/path/to/your-project --apply
```

### Windows PowerShell

```powershell
py -3 skills/architecture-advisor/scripts/install.py --harness claude --scope project --project "C:\Projects\My Application" --dry-run
py -3 skills/architecture-advisor/scripts/install.py --harness claude --scope project --project "C:\Projects\My Application" --apply
```

Python 3.10+ is required for bundled scripts. File installation uses the standard library only; it does not install runtime dependencies.

### Choose your harness

| `--harness` | Project install | User install with `--scope user` |
|---|---|---|
| `codex` | `.agents/skills/architecture-advisor/` | `~/.agents/skills/architecture-advisor/` |
| `claude` | `.claude/skills/architecture-advisor/` | `~/.claude/skills/architecture-advisor/` |
| `cursor` | `.cursor/skills/architecture-advisor/` | `~/.cursor/skills/architecture-advisor/` |
| `copilot` | `.github/skills/architecture-advisor/` | `~/.copilot/skills/architecture-advisor/` |
| `gemini` | `.gemini/skills/architecture-advisor/` | `~/.gemini/skills/architecture-advisor/` |

Example user install:

```bash
python3 skills/architecture-advisor/scripts/install.py --harness cursor --scope user --apply
```

For another compatible host:

```bash
python3 skills/architecture-advisor/scripts/install.py --target /path/to/host/skills --apply
```

`--target` is the parent directory for skills; the installer creates an `architecture-advisor` child. It does not configure an unknown host to discover that directory.

See [installation and compatibility](skills/architecture-advisor/references/installation.md) for official sources, custom targets, updates, and hosted-session limitations. Local discovery paths were checked on 31 October 2026. The Python installer was tested as described in the release validation; this does not imply end-to-end testing inside every named harness.

## Use the skill

In Codex, open `/skills`, find Architecture Advisor, and select the installed skill, or explicitly ask Codex to use Architecture Advisor. In Claude Code, use `/architecture-advisor`. In Cursor, select it from the `/` menu. For other hosts, use their skill discovery controls or explicitly ask the agent to use `architecture-advisor`.

Example requests:

```text
Use architecture-advisor to review the attached architecture diagram and requirements PDF.
Identify the main reliability and cost risks, compare feasible alternatives, and produce
a structured report for our architecture review board. Cite the supplied evidence.
```

```text
Use architecture-advisor to compare these ServiceNow integration designs.
Keep the stated data-location and recovery requirements mandatory. Separate current
entitlements from new purchases, and explain the conditions that would change your recommendation.
```

```text
Use architecture-advisor to allocate the external processing workloads using the supplied
capacity and cost data. State the solver status, model assumptions, and remaining unknowns.
```

## Attachments and capabilities

The host must make uploaded files available to the agent. Vision is needed to interpret diagram layout and arrows; OCR alone cannot reconstruct architecture semantics. The bundled intake helper extracts supported content and reports limitations so the agent can inspect the original source. For unsupported formats or missing tools, the agent should explain the coverage gap and continue with the accessible evidence.

The language model performs the architectural reasoning. The scripts support intake, deterministic calculations, validation, and structured output; they do not create expert judgments without the host model. Missing cost or capacity data should be reported as unknown rather than fabricated.

The skill and scripts do not deploy infrastructure or connect to ServiceNow. Live integrations and any changes remain separate, explicitly authorized work.

## Publish this repository

1. Upload the extracted package contents to the repository root, including the `.agents/` and `.codex-plugin/` directories. A ZIP uploaded by itself is not the repository layout used by these commands.
2. Keep `skills/architecture-advisor/SKILL.md` and all supporting files together.
3. Replace the `OWNER/REPO` placeholder in this README with your repository identity.
4. Review the synthetic examples and publish a versioned distribution release, such as `v1.1.0`. Keep the root `VERSION` and both plugin manifests aligned when publishing future wrapper releases.
5. Share the repository URL and the native Codex commands above. The bundled core skill's separate version is recorded in `skills/architecture-advisor/VERSION` and `package_manifest.json`.

There is no required API key, marketplace account, or company-specific connector for the core review workflow. Document extraction and optimization helpers may require optional Python packages; use the dependency instructions supplied with this release.

## Local helper setup

The core workflow, installer, exact bounded enumeration, shared-cost allocation, DOCX/PPTX XML extraction, and text/CSV intake use Python 3.10+ and the standard library. The language-model host remains responsible for reasoning, browsing and visual inspection.

Create an isolated environment from the repository root (macOS/Linux):

    python3 -m venv .venv
    .venv/bin/python -m pip install -r skills/architecture-advisor/requirements-documents.txt
    .venv/bin/python -m pip install -r skills/architecture-advisor/requirements-optimization.txt
    .venv/bin/python skills/architecture-advisor/scripts/doctor.py

On Windows PowerShell:

    py -3 -m venv .venv
    .venv\Scripts\python.exe -m pip install -r skills/architecture-advisor/requirements-documents.txt
    .venv\Scripts\python.exe -m pip install -r skills/architecture-advisor/requirements-optimization.txt
    .venv\Scripts\python.exe skills/architecture-advisor/scripts/doctor.py

Install only the dependency groups you need. Document extras add PDF text extraction, image metadata, and XLSX reading. The optimization extra adds CP-SAT. No script installs a package automatically. Point the host's shell/tool runtime at this environment or use its Python path in commands. A skill-file installation alone does not configure a Python environment.

## Run a complete synthetic calculation

From the repository root, substitute your environment's Python executable where needed. The output paths below must not already exist; use a new output directory for another run.

    python3 skills/architecture-advisor/scripts/optimize.py skills/architecture-advisor/examples/model.json --output outputs/demo/run.json --backend enumerate
    python3 skills/architecture-advisor/scripts/render_report.py outputs/demo/run.json --output outputs/demo/calculation.md
    python3 skills/architecture-advisor/scripts/allocate_costs.py skills/architecture-advisor/examples/allocation.json --output outputs/demo/allocation.json

Expected optimization result: OPTIMAL for the encoded synthetic model, with INR 3,130,000 over 24 months. Raising the example capacity constraint from 100 to 150 changes the best listed option to INR 3,770,000. These are illustrative inputs, not real vendor quotes or measured savings.

Use --backend cp-sat with the optional dependency installed for the same model. The default enumeration backend is exact if it finishes, but grows exponentially; its time/state limits produce FEASIBLE or UNKNOWN when appropriate. No backend implements the ETH paper. Read [the model reference](skills/architecture-advisor/references/optimization-model.md) before translating real requirements.

## Review uploaded documents

    python3 skills/architecture-advisor/scripts/ingest.py architecture.pdf diagram.png costs.xlsx --out-dir outputs/evidence

The intake folder contains a manifest, source hashes, evidence IDs, locators and coverage warnings. PDF text does not verify a diagram. Images require the host's visual capability. Scanned PDFs need separate host/local OCR; the intake helper performs no OCR. DOCX uses paragraph/table locations, PPTX uses slide locations, and XLSX preserves formulas without recalculation. Unsupported legacy/macro-enabled files are reported explicitly.

For long documents, increase documented limits deliberately; for example --max-text-chars 400000. These controls are not a replacement for process-level resource isolation when parsing untrusted files.

Use the [full report template](skills/architecture-advisor/assets/architecture-report.md) and [ADR template](skills/architecture-advisor/assets/decision-record.md). The model should produce the architectural reasoning; render_report.py only creates a calculation appendix. See [the synthetic full review](skills/architecture-advisor/examples/architecture-review.md) for the expected professional style.

## Validate and contribute

For the complete optional-dependency and JSON Schema test set:

    python3 -m pip install -r skills/architecture-advisor/requirements-dev.txt

    python3 skills/architecture-advisor/scripts/validate_bundle.py
    python3 -m unittest discover -s skills/architecture-advisor/tests -v

Optional-format, CP-SAT and JSON Schema tests skip when their dependencies are absent. The development dependency file includes all three groups. The GitHub Actions workflow runs the suite on configured Linux/Windows jobs after publication; including the workflow does not mean it has already run on GitHub.

### Distribution 1.1.0 validation scope

The distribution wrapper is checked for JSON syntax, portable-manifest JSON Schema conformance, matching names and versions, local source/skill paths, and unchanged bundled skill file hashes. The Codex CLI is unavailable in the build environment, so these checks do **not** constitute an actual native CLI installation. The unpublished GitHub source and native marketplace fetch have not been exercised. Run the installation and `codex plugin list` commands in your Codex environment to verify that route.

The root `plugin.json` is the canonical portable manifest. It discovers the root `skills/` directory. The `.codex-plugin/plugin.json` compatibility overlay supplies OpenAI display metadata when root `extensions.com.openai` is absent. The marketplace's `source.path` is relative to the repository/marketplace root, so `./` selects this package root.

### Bundled core skill 1.0.0 validation

The original core 1.0.0 release passed all 65 automated tests on Linux with Python 3.12.14, including real OR-Tools 9.15.6755 execution, document fixtures and JSON Schema validation. This is retained evidence for the unchanged core, not a new native-plugin installation test. The suite covers solver status handling, cost arithmetic, shared capacity, allocation reconciliation, source locators, unsupported inputs, Python installer destinations and overwrite refusal. The original package and skill metadata checks also passed.

A fresh agent additionally reviewed the [synthetic document-and-diagram case](skills/architecture-advisor/examples/review-case/) using the skill. It correctly deferred production approval when pricing and engineering evidence were missing, preserved the hosted ServiceNow boundary, and produced a complete structured report. The report's structural check passed. See [the forward-use evaluation](skills/architecture-advisor/evals/forward-use.md) for the reproducible scenario and acceptance criteria.

This establishes local functionality for these cases. Native sessions in every named harness, native Windows execution, a future GitHub repository, and its CI jobs have not been exercised here. Architecture findings still require suitable source evidence and human decision ownership.

Use synthetic fixtures and never commit customer architecture files, secrets, invoices, or generated intake folders. Add evidence-backed domain references instead of hard-coding unsupported prices or claims. Preserve explicit unknowns and solver statuses when extending the package.

## Package contents

| Location | Purpose |
| --- | --- |
| plugin.json | Portable plugin identity and distribution version |
| .codex-plugin/plugin.json | Codex compatibility overlay and display metadata |
| .agents/plugins/marketplace.json | Native marketplace named architecture-tools |
| CHANGELOG.md | Distribution changes and bundled core version |
| skills/architecture-advisor/SKILL.md | Portable agent instructions and routing |
| scripts/ingest.py | Local document intake and source coverage |
| scripts/optimize.py | Bounded enumeration and optional CP-SAT |
| scripts/render_report.py | Verified arithmetic appendix from a run |
| scripts/allocate_costs.py | Exact integer-unit shared-cost allocation |
| scripts/install.py | Preview/apply installation into a chosen host |
| scripts/doctor.py | Local capability diagnostics |
| scripts/check_report.py | Full-report structural check only |
| scripts/validate_bundle.py | Metadata, resource and syntax checks |
| references/ | Review method, ServiceNow, costs, research, installation |
| assets/ | Report/ADR templates and optimization JSON Schema |
| examples/ | Synthetic models, allocation and full review |
| evals/ | Reproducible agent-level review scenario and acceptance criteria |
| tests/ | Generated-fixture correctness and failure-mode tests |

All script/reference/asset paths in the table are within skills/architecture-advisor. The package includes a versioned manifest and SHA256SUMS for distribution verification. Checksums describe the supplied release; editing files, including replacing the repository placeholder, changes their checksums. Regenerate them for your own versioned release.

## License

The original skill instructions and scripts are provided under the MIT License in LICENSE. Third-party Python packages and the optional external Skills CLI retain their own licenses. No research paper or customer file is redistributed.
