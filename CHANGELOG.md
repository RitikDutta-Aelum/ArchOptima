# Changelog

## Distribution/plugin 1.1.0 — 31 October 2026

Adds a Codex distribution wrapper around the unchanged Architecture Advisor core skill 1.0.0.

- Adds root `plugin.json`, using the Agent Plugins 1.0.0 schema and fixed `skills/` discovery.
- Adds `.codex-plugin/plugin.json` with the matching plugin identity/version and OpenAI display metadata.
- Adds `.agents/plugins/marketplace.json`, exposing `architecture-advisor` through the `architecture-tools` marketplace.
- Documents GitHub and local-directory native Codex installation, installed-plugin inspection, and Git-marketplace refresh.
- Retains the alternative Skills CLI and Python file-installation routes.

The installed skill identifier remains `architecture-advisor`. Every file under `skills/architecture-advisor/` is byte-identical to the core 1.0.0 release. The root distribution version and the bundled core version are intentionally separate.

Validation covers JSON syntax, portable-manifest JSON Schema, manifest names/versions, local paths, and core file hashes. No Codex CLI is available in the build environment, and no native CLI install or unpublished GitHub fetch was performed. The 65 passing core tests recorded in the README belong to the original core 1.0.0 release.

## Core skill 1.0.0 — 31 October 2026

Initial portable architecture review skill, including document intake, finite-model optimization, exact cost allocation, professional report templates, synthetic examples, installation helpers, and automated tests.
