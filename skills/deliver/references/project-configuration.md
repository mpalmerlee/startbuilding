# Project configuration

StartBuilding works without setup by reading repository instructions. A target repository may
commit `.startbuilding/project.json` to define validation commands, protected paths, and its branch
prefix.

## Schema

```json
{
  "version": 1,
  "validationCommands": ["pnpm test"],
  "protectedPaths": [".env", ".env.*", ".startbuilding/runs/"],
  "branchPrefix": "startbuilding/"
}
```

- `version` must be `1`.
- `validationCommands` is an ordered list of repository-root commands to run after focused checks.
- `protectedPaths` contains repository-relative paths or gitignore-style patterns that must never
  be staged by StartBuilding.
- `branchPrefix` must be a nonempty Git-safe prefix ending in `/`.

Unknown fields must be preserved and ignored for forward compatibility. Invalid JSON or an invalid
known field blocks mutation until the repository owner fixes the configuration.

## Defaults

When configuration is absent, use:

- validation commands explicitly required by applicable repository instructions;
- protected paths `.env`, `.env.*`, and `.startbuilding/runs/`;
- branch prefix `startbuilding/`.

Configuration never overrides repository security policy, Git hooks, host permissions, the plan
approval gate, or delivery safety checks.
