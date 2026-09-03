# Testing

## Static validation

From the repository root, run:

```sh
./scripts/validate.sh
claude plugin validate . --strict
```

The repository validator checks manifest identity and version parity, component paths, skill links,
project policy, the shared agent inventory, dual-vocabulary tool restrictions, coordinator
allowlists, stale identifiers, ASCII text, trailing whitespace, and executable permissions.

## Prevent customization collisions

Personal and project agents or skills take precedence over plugin components. Before testing, inspect
`~/.copilot/agents/`, `~/.copilot/skills/`, `~/.claude/agents/`, and project customization folders.
Temporarily remove or rename earlier proof-of-concept copies whose IDs could shadow StartBuilding.

In every client, confirm the loaded component source points to this plugin rather than a personal or
project file.

## VS Code Agent Host test

1. Enable `chat.plugins.enabled` and the Agent Host, then select the Copilot harness.
2. Install the working tree through Copilot CLI so VS Code discovers the same package:

   ```sh
   copilot plugin install /absolute/path/to/startbuilding
   ```

3. Reload the VS Code window. Open **Chat: Open Customizations** and confirm the `deliver` and
   `research` skills and exactly nine StartBuilding agents have no diagnostics or duplicate
   variants.
4. Confirm every agent source resolves through the shared `agents/` directory.
5. Invoke the Planner as a subagent and confirm it receives workspace read and file-search tools.
6. Invoke the Implementer as a subagent and confirm it receives filesystem, edit, and shell tools.
7. Confirm `/startbuilding:deliver` appears and the Coordinator can invoke each exact specialist.
8. Confirm `/startbuilding:research` appears and the Research Coordinator can invoke the
   Researcher, Skeptic, and Merger. Confirm the Merger receives only workspace read and
   file-search tools, and that the Researcher and Skeptic receive those plus web fetch, with no
   edit or shell tools for any of the three.
9. Disable the plugin and confirm its components disappear; enable it and confirm they return.

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

Inside Claude Code, confirm `/startbuilding:deliver` and `/startbuilding:research` are available and
plugin agents appear under their scoped names, such as `startbuilding:startbuilding-implementer`.
Confirm Planner gets only `Read`, `Glob`, and `Grep`; Implementer gets `Read`, `Glob`, `Grep`,
`Edit`, `Write`, and `Bash`; and Coordinator gets `Read`, `Write`, `Edit`, `Bash`, and the scoped
`Agent` allowlist. Confirm the Researcher, Skeptic, and Merger each get only `Read`, `Glob`, and
`Grep`, and that the Research Coordinator's `Agent` allowlist names only those three. Use
`/reload-plugins` after changing components.

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
| Revised plan | Writes a suffixed plan, changes `currentPlan`, clears approval, and stops |
| Explicit plan approval | Creates or uses a non-default branch and implements |
| First implementation edit | Runs a focused check immediately afterward |
| Configured validation | Runs explicitly configured or repository-required commands once |
| Implementation completion | Reports exact changed paths and does not stage or commit |
| Independent review | Reads the complete diff, reuses validation results, reports reviewed paths, and does not edit |
| Review findings | Stops for human direction without automatic repair |
| Clean review | Reports ready for delivery and stops for a later user request |
| No delivery request | Makes no commit, push, or pull-request side effects |
| Missing or unauthenticated `gh` | Delivery blocks before commit |
| Protected or secret path | Delivery blocks and stages nothing |
| Unrelated working-tree change | Preserved and excluded from staged paths |
| Explicit delivery request | Stages only reviewed paths, commits, pushes, and creates a PR |
| New chat session | Resumes the named run from `state.json` and current artifacts |
| Multiple active runs | Lists candidates and asks instead of guessing |
| New research request | Creates `request.md` and valid `state.json` at stage `intake` |
| Researching | Uses the native Researcher, writes `findings.md`, and advances to `critiquing` |
| Critiquing | Uses the native Skeptic, writes `critique.md`, and advances to `synthesizing` |
| Synthesizing | Uses the native Merger, writes `recommendation.md`, and stops at `recommendation_review` |
| No human response at recommendation review | Makes no further stage transition |
| Requested revision | Repeats the needed stage, writes a suffixed artifact, and stops again at `recommendation_review` |
| Accepted recommendation | Sets stage `completed` and stops |

Inspect Git status, the staged diff, commit contents, remote branch, pull-request body, and run state
after each applicable scenario.

## Clean-install release test

Use a clean profile or isolated test environment:

1. Install from `mpalmerlee/startbuilding` in Copilot CLI and confirm VS Code Agent Host discovers
   that installation.
2. Confirm VS Code exposes one agent set with the expected delegated tool boundaries.
3. Add the public repository as a Claude marketplace and install `startbuilding@startbuilding`.
4. Repeat component discovery and one complete disposable-repository workflow.
5. Bump to a temporary test version and verify each client's update behavior before publishing the
   actual release version.
