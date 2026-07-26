# Changelog

All notable changes to StartBuilding are documented in this file.

## 0.1.0 - 2026-07-26

### Added

- Shared `/startbuilding:deliver` workflow for planning, implementation, independent review, and
  pull-request delivery.
- Explicit plan and review approval gates bound to artifact content hashes.
- Durable, resumable local run artifacts under `.startbuilding/runs/`.
- Native least-privilege agent sets for VS Code, GitHub Copilot CLI, and Claude Code.
- Direct Git installation metadata and a self-hosted Claude plugin catalog.
- Static repository validation and cross-client acceptance guidance.
