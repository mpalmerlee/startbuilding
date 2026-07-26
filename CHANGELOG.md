# Changelog

All notable changes to StartBuilding are documented in this file.

## 0.2.0 - 2026-07-26

### Changed

- Replaced Git-hash-bound plan approval with a lightweight current-plan artifact pointer.
- Replaced formal review approval records with a simple delivery confirmation after independent
  review.
- Limited default implementation validation to focused checks plus explicitly configured or
  repository-required commands, and directed reviewers to reuse existing results.
- Consolidated branch, secret, reviewed-path, staging, and GitHub checks at the Committer boundary.
- Preserved compatibility with v0.1 run state and project configuration fields as ignored unknown
  data.

## 0.1.2 - 2026-07-26

### Fixed

- Unified Copilot, VS Code, and Claude Code on one shared `agents/*.agent.md` inventory.
- Added dual-vocabulary tool allowlists so each host preserves native role boundaries while ignoring
  unsupported tool names.
- Made Copilot CLI installation the tested path for VS Code Agent Host discovery, eliminating the
  duplicate Claude-format agent set.

## 0.1.1 - 2026-07-26

### Fixed

- Added a higher-precedence VS Code manifest so direct source installations use the Copilot-native
  agents instead of treating the colocated Claude marketplace as the plugin format.
- Added delegated Planner and Implementer tool-availability checks to VS Code acceptance testing.

## 0.1.0 - 2026-07-26

### Added

- Shared `/startbuilding:deliver` workflow for planning, implementation, independent review, and
  pull-request delivery.
- Explicit plan and review approval gates bound to artifact content hashes.
- Durable, resumable local run artifacts under `.startbuilding/runs/`.
- Native least-privilege agent sets for VS Code, GitHub Copilot CLI, and Claude Code.
- Direct Git installation metadata and a self-hosted Claude plugin catalog.
- Static repository validation and cross-client acceptance guidance.
