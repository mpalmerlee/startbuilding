# StartBuilding contributor instructions

StartBuilding is a no-runtime agent plugin distributed to VS Code, GitHub Copilot CLI, and Claude
Code. Keep changes portable across all three clients.

## Source contracts

- `skills/deliver/` is the shared workflow and artifact contract.
- `skills/research/`, `skills/pr-review/`, and `skills/pr-resolve/` are independent, isolated
  workflow and artifact contracts. Never let one graph's Coordinator delegate to another graph's
  agents.
- `agents/` contains the shared `.agent.md` definitions used by every supported client.
- Shared agent tool allowlists include both Copilot aliases and Claude-native names. Preserve each
  role's effective least-privilege boundary in both clients.
- `plugin.json`, `.plugin/plugin.json`, `.claude-plugin/plugin.json`, and
  `.claude-plugin/marketplace.json` must keep the same stable identity and release version.
- The README describes released behavior. Do not document planned behavior as available.

## Constraints

- Preserve explicit approval of the current plan before implementation and an explicit delivery
  request after review.
- Keep planner and reviewer roles read-only through native tool restrictions.
- Keep implementation separate from commit, push, and pull-request delivery.
- Keep `pr-review` findings approval and `pr-resolve` plan approval separate turns from any
  mutating `gh` call. Never let a mutating role submit a review `APPROVE`/`REQUEST_CHANGES` event,
  merge, close, or edit a pull request's title, description, or labels.
- Do not add hooks, MCP/LSP servers, compiled extension code, or runtime services without an
  approved architecture change and cross-client security review.
- Use ASCII text, repository-relative paths, and concise comments.
- Never commit `.startbuilding/runs/`, credentials, environment files, or generated secrets.

## Validation

After the first edit, run the narrowest relevant check. Before completion, run:

```sh
./scripts/validate.sh
claude plugin validate . --strict
```

When client behavior changes, also follow `docs/testing.md`. A release is blocked if a claimed
client does not enforce the documented role boundaries, plan gate, and delivery safeguards.
