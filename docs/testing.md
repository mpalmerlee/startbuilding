# Testing

## Static validation

From the repository root, run:

```sh
./scripts/validate.sh
claude plugin validate . --strict
```

The repository validator checks manifest identity and version parity, component paths, skill links,
project policy, native agent inventories, tool restrictions, coordinator allowlists, cross-client
specialist parity, stale identifiers, ASCII text, trailing whitespace, and executable permissions.

## Prevent customization collisions

Personal and project agents or skills take precedence over plugin components. Before testing, inspect
`~/.copilot/agents/`, `~/.copilot/skills/`, `~/.claude/agents/`, and project customization folders.
Temporarily remove or rename earlier proof-of-concept copies whose IDs could shadow StartBuilding.

In every client, confirm the loaded component source points to this plugin rather than a personal or
project file.

## VS Code local test

1. Enable `chat.plugins.enabled`.
2. Add the clone to settings:

   ```json
   {
     "chat.pluginLocations": {
       "/absolute/path/to/startbuilding": true
     }
   }
   ```

3. Open **Chat: Open Customizations** and confirm the `deliver` skill and five StartBuilding agents
   have no diagnostics.
4. Confirm `/startbuilding:deliver` appears and the Coordinator can invoke each exact specialist.
5. Disable the plugin and confirm its components disappear; enable it and confirm they return.

## Copilot CLI local test

Load the working tree for one session without changing persistent configuration:

```sh
copilot --plugin-dir /absolute/path/to/startbuilding plugin list
```

Confirm the output lists `startbuilding` under external plugins. After the repository is public,
exercise persistent lifecycle commands:

```sh
copilot plugin install mpalmerlee/startbuilding
copilot plugin list
copilot plugin disable startbuilding
copilot plugin enable startbuilding
copilot plugin update startbuilding
copilot plugin uninstall startbuilding
```

Confirm VS Code discovers the CLI-installed plugin and reports the expected source.

## Claude Code local test

Validate and load the working tree without installation:

```sh
claude plugin validate . --strict
claude --plugin-dir /absolute/path/to/startbuilding
```

Inside Claude Code, confirm `/startbuilding:deliver` is available and plugin agents appear under
their scoped names. Use `/reload-plugins` after changing components.

Test persistent installation through the self-hosted catalog:

```sh
claude plugin marketplace add /absolute/path/to/startbuilding
claude plugin install startbuilding@startbuilding
claude plugin list
claude plugin disable startbuilding@startbuilding
claude plugin enable startbuilding@startbuilding
claude plugin uninstall startbuilding@startbuilding
```

Repeat with the public GitHub repository before release.

## Disposable repository

Use a small repository with a testable source file, a focused validation command, a Git remote you
control, and no valuable uncommitted work. Commit `AGENTS.md` with the validation command. Add:

```gitignore
.startbuilding/runs/
```

Configure `gh` against a disposable remote when testing delivery. Never use a production repository
for the first end-to-end run.

Run the same work request independently in VS Code, Copilot CLI, and Claude Code.

## Acceptance matrix

| Scenario | Expected result |
| --- | --- |
| New request | Creates `request.md` and valid `state.json` |
| Planning | Uses the native Planner, writes `plan.md`, and stops |
| No plan approval | Implementer refuses without edits |
| Edited approved plan | Hash mismatch clears approval and stops |
| Explicit plan approval | Creates or uses a non-default branch and implements |
| First implementation edit | Runs a focused check immediately afterward |
| Implementation completion | Reports exact changed paths and does not stage or commit |
| Independent review | Reads the complete diff, reports reviewed paths, and does not edit |
| Review findings | Stops for human direction without automatic repair |
| No review approval | Committer refuses without side effects |
| Edited approved review | Hash mismatch clears approval and stops |
| Missing or unauthenticated `gh` | Delivery blocks before commit |
| Protected or secret path | Delivery blocks and stages nothing |
| Unrelated working-tree change | Preserved and excluded from staged paths |
| Explicit review approval | Stages only reviewed paths, commits, pushes, and creates a PR |
| New chat session | Resumes the named run from `state.json` and current artifacts |
| Multiple active runs | Lists candidates and asks instead of guessing |

Inspect Git status, the staged diff, commit contents, remote branch, pull-request body, and run state
after each applicable scenario.

## Clean-install release test

Use a clean profile or isolated test environment:

1. Install from `https://github.com/mpalmerlee/startbuilding` in VS Code.
2. Install from `mpalmerlee/startbuilding` in Copilot CLI.
3. Add the public repository as a Claude marketplace and install `startbuilding@startbuilding`.
4. Repeat component discovery and one complete disposable-repository workflow.
5. Bump to a temporary test version and verify each client's update behavior before publishing the
   actual release version.
