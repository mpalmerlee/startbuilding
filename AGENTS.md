# StartBuilding contributor instructions

StartBuilding is a no-runtime agent plugin distributed to VS Code, GitHub Copilot CLI, and Claude
Code. Keep changes portable across all three clients.

## Source contracts

- `skills/deliver/` is the shared workflow and artifact contract.
- `copilot-agents/` contains VS Code and Copilot-native frontmatter.
- `agents/` contains Claude-native frontmatter and uses Claude's default plugin discovery path.
- Specialist agent bodies must remain behaviorally identical across clients. Change both versions
  together.
- `plugin.json`, `.plugin/plugin.json`, `.claude-plugin/plugin.json`, and
  `.claude-plugin/marketplace.json` must keep the same stable identity and release version.
- The README describes released behavior. Do not document planned behavior as available.

## Constraints

- Preserve both explicit, content-bound human approval gates.
- Keep planner and reviewer roles read-only through native tool restrictions.
- Keep implementation separate from commit, push, and pull-request delivery.
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
client does not enforce the documented role boundaries and approval gates.
