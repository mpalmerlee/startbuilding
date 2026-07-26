# Project configuration

StartBuilding works without setup by reading repository instructions, package manifests, build
files, and CI configuration. A target repository may commit `.startbuilding/project.json` to
override discovered policy.

## Schema

```json
{
  "version": 1,
  "validationCommands": ["pnpm test"],
  "protectedPaths": [".env", ".env.*", ".startbuilding/runs/"],
  "branchPrefix": "startbuilding/",
  "requirePlanApproval": true,
  "requireReviewApproval": true
}
```

- `version` must be `1`.
- `validationCommands` is an ordered list of repository-root commands. Use repository instructions
  and focused checks before these broader commands.
- `protectedPaths` contains repository-relative paths or gitignore-style patterns that must never
  be staged by StartBuilding.
- `branchPrefix` must be a nonempty Git-safe prefix ending in `/`.
- `requirePlanApproval` and `requireReviewApproval` must remain `true` in v0.1. A configuration that
  sets either to `false` is invalid and blocks the workflow.

Unknown fields must be preserved and ignored for forward compatibility. Invalid JSON or an invalid
known field blocks mutation until the repository owner fixes the configuration.

## Defaults

When configuration is absent, use:

- validation commands discovered from repository instructions and CI;
- protected paths `.env`, `.env.*`, and `.startbuilding/runs/`;
- branch prefix `startbuilding/`;
- both approval requirements enabled.

Configuration never overrides repository security policy, Git hooks, host permissions, or the
plugin's non-negotiable approval boundaries.
