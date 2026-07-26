## Plan: Build the StartBuilding agent plugin

Extract the proven RelayStep delivery methodology into the empty `startbuilding` repository as a
versioned, no-runtime agent plugin. Keep one shared workflow skill and artifact contract, but provide
client-specific agent frontmatter and manifests so VS Code/Copilot and Claude Code each enforce
their native tool restrictions. Release v0.1.0 for public Git-based installation across VS Code,
Copilot CLI, and Claude Code; defer submission to third-party community marketplaces.

## Steps

### Phase 1: Establish the portable plugin skeleton

1. Initialize the empty destination repository with `README.md`, `CHANGELOG.md`, `LICENSE` (MIT),
   `.gitignore`, contributor/architecture documentation, and `AGENTS.md`. Record Node-free,
   plugin-only scope, supported clients, prerequisites (`git`, authenticated `gh` for delivery),
   security boundaries, and the v0.1.0 release policy.
2. Add the Copilot/VS Code root `plugin.json` and Claude `.claude-plugin/plugin.json`, both with
   stable ID `startbuilding`, display metadata, version `0.1.0`, MIT license, repository URL
   `https://github.com/mpalmerlee/startbuilding`, and their native agent-directory path. Keep
   `skills/deliver/` shared so both expose `/startbuilding:deliver`.
3. Add `.claude-plugin/marketplace.json` as a self-hosted one-plugin catalog whose source is the
   repository root. This enables persistent Claude Code installation from the public Git repository
   without submitting to Anthropic's community marketplace. Do not add an external marketplace
   repository or submit to `awesome-copilot`, `copilot-plugins`, or `claude-community` in v0.1.
4. Add `scripts/validate.sh` early and make each later phase extend it. It should fail on malformed
   manifests, mismatched name/version/license/repository metadata, missing component paths,
   non-kebab IDs, and divergence between the two manifests where values are intended to match.
   This establishes the cheap validation loop for all subsequent work.

### Phase 2: Port and strengthen the workflow contract

5. Migrate `relaystep/agent-delivery-kit/skills/software-delivery/SKILL.md` to
   `skills/deliver/SKILL.md`; rename the skill to `deliver`, all product terminology to
   StartBuilding, and all repository metadata paths from `.relaystep/` to `.startbuilding/`. Keep
   repository instructions authoritative and preserve the two explicit human gates.
6. Split the large workflow instructions into progressively loaded references:
   `artifact-contract.md` for state/artifact schemas, `project-configuration.md` for optional
   repository policy, and `workflow-stages.md` for transitions and recovery behavior. Ensure every
   reference and asset is linked from `SKILL.md`, because unreferenced skill resources are not
   progressively loaded.
7. Define `.startbuilding/project.json` as optional versioned policy with default branch prefix
   `startbuilding/`, validation commands, protected paths, approval requirements, and optional
   overrides. Put the distributable example at `skills/deliver/assets/project.json`; do not
   auto-create project configuration or modify a target repository's `.gitignore` in v0.1.
8. Retain `.startbuilding/runs/<work-id>/` with `request.md`, versioned
   plan/implementation/review artifacts, `delivery.md`, and `state.json`. Strengthen approval
   records with the exact artifact path, explicit user approval text, UTC timestamp, and a content
   identity from `git hash-object --no-filters`; invalidate approval whenever the current artifact
   or hash changes. Preserve unknown state fields for forward compatibility and never persist
   secrets or unrelated chat text.
9. Specify deterministic resume behavior: use an explicitly named work ID/run path; if omitted,
   resume only when exactly one nonterminal run exists, otherwise list candidates and ask the user
   to choose. Repeated stages create suffixed artifacts and update current pointers rather than
   overwriting evidence.
10. Define delivery safety: create or use a non-default `startbuilding/<work-id>` branch without
    discarding existing changes; implementation reports changed paths; review covers the complete
    working-tree diff and identifies unrelated changes; commit stages only reviewed implementation
    paths and blocks on unreviewed content, protected paths, secrets, stale approvals, missing `gh`
    authentication, or a non-ready verdict. Verify the staged diff before commit and never stage
    `.startbuilding/runs/`.

### Phase 3: Port the five roles with native enforcement

11. Create Copilot/VS Code agents under `copilot-agents/`:
    `startbuilding-coordinator.agent.md`, planner, implementer, reviewer, and committer. Port the POC
    bodies, use StartBuilding display names, retain `user-invocable: false` and `agents: []` for
    specialists, grant only native `read/search/edit/execute/agent` tools required by each role,
    and allow the coordinator to invoke exactly the four specialists.
12. Create behaviorally equivalent Claude agents under `agents/` using Claude's lowercase
    `name`, `Read/Glob/Grep/Edit/Write/Bash/Agent(...)` vocabulary, and native
    allowlists/omissions. Specialists must omit `Agent`; planner and reviewer omit write tools;
    implementer cannot perform delivery; committer has no edit/write tools. The coordinator may
    spawn only the four StartBuilding specialist IDs.
13. Make `deliver` the canonical user entry point on every client. Its instructions resolve the
    host's available agent names (`StartBuilding Planner` in Copilot, scoped
    `startbuilding:startbuilding-planner` in Claude), while the coordinator agents remain alternate
    explicit entry points. Keep workflow writes in the parent coordinator context; specialist
    outputs are returned and persisted exactly.
14. Extend validation to compare the two agent sets by role and required contract markers, verify
    coordinator allowlists against actual IDs/display names, verify least-privilege tool
    declarations, and reject stale `.relaystep`, `.startdev`, `software-delivery`,
    `Delivery Planner`, absolute RelayStep paths, or unprefixed agent IDs. Also validate relative
    Markdown links and executable script permissions.

### Phase 4: Documentation and automated checks

15. Replace the POC copy-installer documentation with client-specific development and public-install
    instructions: VS Code `chat.pluginLocations` and "Install Plugin From Source"; Copilot CLI
    local/Git install and lifecycle commands; Claude `--plugin-dir` for development plus adding this
    repository as a marketplace and installing `startbuilding@startbuilding` for persistence.
    Include collision cleanup for stale personal POC agents/skills before testing.
16. Document the architecture, state machine, trust model, artifact lifecycle, role/tool matrix,
    configuration schema, limitations, and recovery paths. Clearly state that v0.1 has no hooks,
    MCP/LSP servers, background scheduler, database, queue, UI, multi-user approval, or
    crash-recovery service.
17. Add a GitHub Actions validation workflow that runs the repository validator on pull requests and
    pushes, checks JSON/YAML/frontmatter/link conventions, scans for stale identifiers and obvious
    secret files, and runs `claude plugin validate . --strict` when the CLI can be installed
    non-interactively. Keep vendor-CLI validation as a documented local requirement if CI cannot
    install it without credentials.
18. Add a versioned manual smoke-test document and disposable fixture repository recipe covering
    component discovery, enable/disable behavior, both approval stops, stale-artifact rejection,
    branch creation, implementation/review separation, blocked unsafe delivery, commit/push/PR
    success, and cross-session resume.

### Phase 5: Cross-client acceptance and public direct release

19. Validate the local plugin in VS Code after removing or renaming stale `~/.copilot/agents/` and
    `~/.copilot/skills/software-delivery/` entries. Confirm the namespaced skill, coordinator,
    hidden specialists, exact delegated agent identities, diagnostics, and plugin disable/enable
    lifecycle.
20. Validate Copilot CLI session-locally with `--plugin-dir`, then install from
   `mpalmerlee/startbuilding`; confirm
    list/update/disable/enable/uninstall behavior and that VS Code discovers the CLI-installed
    plugin. Run the complete disposable-repository workflow through both approval gates.
21. Validate Claude Code with `claude plugin validate . --strict` and `claude --plugin-dir`, then
    through the repository's self-hosted catalog. Confirm `/startbuilding:deliver`, scoped agent
    discovery, native tool restrictions, explicit approval behavior, update/uninstall, and the same
    end-to-end workflow. Any client whose native restrictions are not actually enforced blocks
    v0.1 rather than being documented as supported.
22. Run a clean-install acceptance test from the public Git URL on a fresh profile/test environment,
    finalize `CHANGELOG.md`, tag `v0.1.0`, and publish installation commands in the README. Verify
    update behavior with an explicit version bump before announcing the release.
23. After direct-install telemetry and user feedback, open a separate release plan for external
    catalog submissions (`awesome-copilot`/Copilot marketplace and Anthropic `claude-community`),
    naming/trademark checks, submission forms, review requirements, and marketplace-specific
    metadata. This is deliberately not part of v0.1 delivery.

## Relevant files

- `plugin.json` - Copilot/VS Code manifest and canonical v0.1 metadata.
- `.claude-plugin/plugin.json` - Claude manifest with the Claude-native agent path.
- `.claude-plugin/marketplace.json` - Self-hosted Claude catalog for persistent public Git
  distribution.
- `skills/deliver/SKILL.md` - Shared `/startbuilding:deliver` orchestration entry point.
- `skills/deliver/references/artifact-contract.md` - Durable state, hash-bound approvals, naming,
  and resume rules.
- `skills/deliver/references/project-configuration.md` - Optional `.startbuilding/project.json`
  contract and defaults.
- `skills/deliver/references/workflow-stages.md` - State transitions, gates, blocked states, and
  repair loops.
- `skills/deliver/assets/project.json` - Optional configuration template.
- `copilot-agents/` - Five Copilot/VS Code `.agent.md` definitions.
- `agents/` - Five Claude-native agent definitions with equivalent role bodies.
- `scripts/validate.sh` - Structural, parity, stale-name, link, and policy validation.
- `.github/workflows/validate.yml` - CI validation.
- `docs/architecture.md` - Client architecture, role matrix, and trust boundaries.
- `docs/testing.md` - Repeatable local and clean-install acceptance matrix.
- `../relaystep/agent-delivery-kit/custom_agent_and_skills_vision.md` - Product handoff and migration
  checklist to reconcile, with StartDev decisions superseded by StartBuilding choices.
- `../relaystep/agent-delivery-kit/skills/software-delivery/SKILL.md` - Source workflow behavior.
- `../relaystep/agent-delivery-kit/skills/software-delivery/references/artifacts.md` - Source
  artifact/state contract.
- `../relaystep/agent-delivery-kit/agents/` - Source role prompts and Copilot tool boundaries.
- `../relaystep/agent-delivery-kit/scripts/validate.sh` - Minimal validator to replace, not copy
  unchanged.

## Verification

1. Run `./scripts/validate.sh` after every structural or prompt change and in CI; require zero stale
   product identifiers, broken links, manifest drift, agent parity failures, or permission-boundary
   failures.
2. Run `claude plugin validate . --strict`, inspect `claude plugin details startbuilding`, and use
   `claude --debug` when component loading is ambiguous.
3. In VS Code, inspect Chat Customizations diagnostics and Agent Plugins views; verify source paths
   so personal/project precedence cannot mask the plugin.
4. In Copilot CLI, test session-local loading with `--plugin-dir`, then Git installation plus
   `list`, `update`, `disable`, `enable`, and `uninstall`; confirm VS Code sees the installation.
5. In Claude Code, test `--plugin-dir`, self-hosted marketplace add/install, `/reload-plugins`, scoped
   skill/agent invocation, update, disable, and uninstall.
6. Run the disposable-repository matrix independently on all three clients, including negative tests
   for missing/stale plan approval, missing/stale review approval, default-branch mutation,
   protected paths, unrelated changes, missing `gh`, and accidental run-artifact staging.
7. Perform a final clean-profile install from the public Git repository and verify `v0.1.0`
   version/update semantics before tagging the release.

## Decisions

- Product, repository, plugin ID, and metadata namespace are `StartBuilding`, `startbuilding`, and
  `.startbuilding/`; the handoff's StartDev naming is superseded.
- Primary command is `/startbuilding:deliver`.
- v0.1's tested support contract is VS Code, GitHub Copilot CLI, and Claude Code.
- License is MIT.
- v0.1 is a public direct-install release. A self-hosted Claude catalog is included only because
  persistent Claude installation requires a marketplace source; third-party marketplace
  submissions are deferred.
- Use client-specific manifests and agent frontmatter with a shared skill/reference contract. This
  preserves native least-privilege controls instead of relying on ambiguous cross-client field
  translation.
- `.startbuilding/project.json` remains optional; `.startbuilding/runs/` is ignored by default;
  branch prefix defaults to `startbuilding/`.
- Approval is explicit and bound to artifact content. Silence, a favorable automated review, or an
  agent message never constitutes approval.
- `git` is foundational; authenticated `gh` is required only for the final delivery stage. Missing
  delivery prerequisites block before commit/push/PR side effects.
- Hooks, MCP/LSP servers, compiled extension code, and runtime services are excluded from v0.1
  unless cross-client acceptance proves an instruction/tool restriction cannot otherwise enforce a
  critical safety boundary.
