# Contributing

## Prerequisites

- Git
- Python 3 for static validation
- VS Code with GitHub Copilot, GitHub Copilot CLI, and Claude Code for full acceptance testing
- GitHub CLI for the end-to-end delivery test

The plugin itself has no Python or Node.js runtime dependency.

## Make a change

1. Read `AGENTS.md` and the relevant contract under `skills/deliver/`.
2. Keep the shared skill host-neutral.
3. When changing a specialist, update both native agent files and preserve equivalent behavior.
4. Keep frontmatter restricted to fields supported by that client.
5. Update the README and changelog when released behavior changes.
6. Run focused validation after the first edit and the complete checks before requesting review.

## Validate

Run the repository validator:

```sh
./scripts/validate.sh
```

When Claude Code is installed, also run its native schema validator:

```sh
claude plugin validate . --strict
```

Follow `docs/testing.md` for changes to workflow transitions, permissions, approval behavior,
installation, or delivery safety.

## Release changes

For every release:

1. Choose the semantic version.
2. Update `plugin.json`, `.plugin/plugin.json`, `.claude-plugin/plugin.json`, and
   `.claude-plugin/marketplace.json` together.
3. Add a dated changelog entry.
4. Run static and cross-client acceptance checks from a clean worktree.
5. Test installation from the public Git repository with a clean client profile.
6. Tag the exact accepted commit with `v<version>`.

Do not publish a version that bypasses plan approval, delivery confirmation, or delivery safety, or
advertises a client whose native role restrictions were not verified.
