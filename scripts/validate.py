#!/usr/bin/env python3

import json
import os
import re
import sys
from pathlib import Path


class Validation:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def require_file(self, relative_path: str) -> Path:
        path = self.root / relative_path
        if not path.is_file():
            self.fail(f"Missing required file: {relative_path}")
        return path

    def read_json(self, relative_path: str) -> dict:
        path = self.require_file(relative_path)
        if not path.is_file():
            return {}
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.fail(f"Invalid JSON in {relative_path}: {error}")
            return {}
        if not isinstance(value, dict):
            self.fail(f"Expected a JSON object in {relative_path}")
            return {}
        return value

    def read_frontmatter(self, relative_path: str) -> tuple[dict[str, str], str]:
        path = self.require_file(relative_path)
        if not path.is_file():
            return {}, ""
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
        if not match:
            self.fail(f"Missing or malformed frontmatter: {relative_path}")
            return {}, text

        fields: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if line.startswith((" ", "-")) or ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
        return fields, match.group(2)

    def validate_manifests(self) -> None:
        copilot = self.read_json("plugin.json")
        vscode = self.read_json(".plugin/plugin.json")
        claude = self.read_json(".claude-plugin/plugin.json")
        marketplace = self.read_json(".claude-plugin/marketplace.json")

        for key in ("name", "description", "version", "repository", "license"):
            if copilot.get(key) != vscode.get(key):
                self.fail(f"Manifest field differs between Copilot and VS Code: {key}")
            if copilot.get(key) != claude.get(key):
                self.fail(f"Manifest field differs between clients: {key}")

        name = copilot.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            self.fail("Plugin name must be lowercase kebab-case")
        if not isinstance(copilot.get("version"), str) or not re.fullmatch(
            r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)",
            copilot.get("version", ""),
        ):
            self.fail("Plugin version must be semantic MAJOR.MINOR.PATCH")

        if copilot.get("agents") != "copilot-agents/":
            self.fail("Copilot manifest must use copilot-agents/")
        if copilot.get("skills") != "skills/":
            self.fail("Copilot manifest must use skills/")
        if vscode.get("agents") != "copilot-agents/":
            self.fail("VS Code precedence manifest must use copilot-agents/")
        if vscode.get("skills") != "skills/":
            self.fail("VS Code precedence manifest must use skills/")

        if "agents" in claude:
            self.fail("Claude manifest must use default agents/ discovery")
        if not (self.root / "agents").is_dir():
            self.fail("Missing Claude default agent directory")

        plugins = marketplace.get("plugins")
        if marketplace.get("name") != name or not isinstance(plugins, list) or len(plugins) != 1:
            self.fail("Marketplace must contain the single StartBuilding plugin")
        elif plugins[0].get("name") != name or plugins[0].get("source") != "./":
            self.fail("Marketplace plugin identity or source is invalid")
        if marketplace.get("metadata", {}).get("version") != copilot.get("version"):
            self.fail("Marketplace and plugin versions differ")

    def validate_skill(self) -> None:
        fields, body = self.read_frontmatter("skills/deliver/SKILL.md")
        if fields.get("name") != "deliver":
            self.fail("Skill name must be deliver")
        if not fields.get("description"):
            self.fail("Skill description is required")
        for marker in (
            "./references/workflow-stages.md",
            "./references/artifact-contract.md",
            "./references/project-configuration.md",
            "./assets/project.json",
            "StartBuilding Planner",
            "startbuilding:startbuilding-planner",
        ):
            if marker not in body:
                self.fail(f"Skill is missing contract marker: {marker}")

        config = self.read_json("skills/deliver/assets/project.json")
        if config.get("version") != 1:
            self.fail("Project configuration version must be 1")
        if config.get("branchPrefix") != "startbuilding/":
            self.fail("Default branch prefix must be startbuilding/")
        if config.get("requirePlanApproval") is not True:
            self.fail("Plan approval must be required")
        if config.get("requireReviewApproval") is not True:
            self.fail("Review approval must be required")
        protected = config.get("protectedPaths")
        if not isinstance(protected, list) or ".startbuilding/runs/" not in protected:
            self.fail("Run artifacts must be protected")

    def validate_agents(self) -> None:
        roles = ("coordinator", "planner", "implementer", "reviewer", "committer")
        copilot_dir = self.root / "copilot-agents"
        claude_dir = self.root / "agents"
        copilot_files = sorted(copilot_dir.glob("*.agent.md")) if copilot_dir.is_dir() else []
        claude_files = sorted(claude_dir.glob("*.md")) if claude_dir.is_dir() else []
        if len(copilot_files) != 5:
            self.fail("Expected exactly five Copilot agents")
        if len(claude_files) != 5:
            self.fail("Expected exactly five Claude agents")

        expected_copilot_tools = {
            "coordinator": "[read, search, edit, execute, agent]",
            "planner": "[read, search]",
            "implementer": "[read, search, edit, execute]",
            "reviewer": "[read, search, execute]",
            "committer": "[read, execute]",
        }
        expected_claude_tools = {
            "planner": "Read, Glob, Grep",
            "implementer": "Read, Glob, Grep, Edit, Write, Bash",
            "reviewer": "Read, Glob, Grep, Bash",
            "committer": "Read, Glob, Grep, Bash",
        }
        display_names = {role: f"StartBuilding {role.title()}" for role in roles}

        for role in roles:
            copilot_path = f"copilot-agents/startbuilding-{role}.agent.md"
            claude_path = f"agents/startbuilding-{role}.md"
            copilot_fields, copilot_body = self.read_frontmatter(copilot_path)
            claude_fields, claude_body = self.read_frontmatter(claude_path)

            if copilot_fields.get("name") != display_names[role]:
                self.fail(f"Invalid Copilot display name for {role}")
            if copilot_fields.get("tools") != expected_copilot_tools[role]:
                self.fail(f"Invalid Copilot tools for {role}")
            if claude_fields.get("name") != f"startbuilding-{role}":
                self.fail(f"Invalid Claude name for {role}")
            if role != "coordinator" and claude_fields.get("tools") != expected_claude_tools[role]:
                self.fail(f"Invalid Claude tools for {role}")

            if role != "coordinator":
                if copilot_fields.get("agents") != "[]":
                    self.fail(f"Copilot {role} must prevent subagent use")
                if copilot_fields.get("user-invocable") != "false":
                    self.fail(f"Copilot {role} must be hidden from the normal picker")
                if "Agent" in claude_fields.get("tools", ""):
                    self.fail(f"Claude {role} must not spawn subagents")
                if copilot_body != claude_body:
                    self.fail(f"Agent behavior differs between clients for {role}")

        coordinator = self.require_file(
            "copilot-agents/startbuilding-coordinator.agent.md"
        ).read_text(encoding="utf-8")
        for role in roles[1:]:
            if display_names[role] not in coordinator:
                self.fail(f"Copilot coordinator is missing {display_names[role]}")

        claude_coordinator = self.require_file(
            "agents/startbuilding-coordinator.md"
        ).read_text(encoding="utf-8")
        for role in roles[1:]:
            scoped_name = f"startbuilding:startbuilding-{role}"
            if scoped_name not in claude_coordinator:
                self.fail(f"Claude coordinator is missing {scoped_name}")

        contract_markers = {
            "planner": ("Status: awaiting approval",),
            "implementer": ("git hash-object --no-filters", "Status: ready for review"),
            "reviewer": ("Verdict: changes requested", "Verdict: ready for human approval"),
            "committer": ("gh auth status", "git add -A", "Status: delivered"),
        }
        for role, markers in contract_markers.items():
            text = self.require_file(
                f"copilot-agents/startbuilding-{role}.agent.md"
            ).read_text(encoding="utf-8")
            for marker in markers:
                if marker not in text:
                    self.fail(f"{role} is missing contract marker: {marker}")

    def validate_markdown_links(self) -> None:
        pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
        for path in self.root.rglob("*.md"):
            if ".git" in path.parts:
                continue
            for target in pattern.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                relative_target = target.split("#", 1)[0]
                if relative_target and not (path.parent / relative_target).resolve().exists():
                    self.fail(f"Broken Markdown link in {path.relative_to(self.root)}: {target}")

    def validate_repository_files(self) -> None:
        required_files = (
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "AGENTS.md",
            "docs/architecture.md",
            "docs/contributing.md",
            "docs/testing.md",
            ".github/workflows/validate.yml",
        )
        for relative_path in required_files:
            self.require_file(relative_path)

        readme = self.require_file("README.md")
        if readme.is_file():
            readme_text = readme.read_text(encoding="utf-8")
            for marker in (
                "/startbuilding:deliver",
                "copilot plugin install mpalmerlee/startbuilding",
                "claude plugin marketplace add mpalmerlee/startbuilding",
                "Chat: Install Plugin From Source",
            ):
                if marker not in readme_text:
                    self.fail(f"README is missing release marker: {marker}")

        license_path = self.require_file("LICENSE")
        if license_path.is_file() and not license_path.read_text(encoding="utf-8").startswith(
            "MIT License"
        ):
            self.fail("LICENSE must contain the MIT license")

        gitignore = self.require_file(".gitignore")
        if gitignore.is_file() and ".startbuilding/runs/" not in gitignore.read_text(
            encoding="utf-8"
        ).splitlines():
            self.fail(".gitignore must exclude .startbuilding/runs/")

        workflow = self.require_file(".github/workflows/validate.yml")
        if workflow.is_file():
            workflow_text = workflow.read_text(encoding="utf-8")
            for marker in ("./scripts/validate.sh", "claude plugin validate . --strict"):
                if marker not in workflow_text:
                    self.fail(f"CI workflow is missing validation marker: {marker}")

    def validate_text_files(self) -> None:
        stale_exclusions = {"plan.md", "scripts/validate.py"}
        stale_patterns = (".relay" + "step", ".start" + "dev", "software-" + "delivery")
        text_suffixes = {".md", ".json", ".py", ".sh", ".yml", ".yaml"}
        for path in self.root.rglob("*"):
            is_extensionless_text = path.name in {"LICENSE", ".gitignore"}
            if (
                not path.is_file()
                or ".git" in path.parts
                or (path.suffix not in text_suffixes and not is_extensionless_text)
            ):
                continue
            relative = path.relative_to(self.root).as_posix()
            data = path.read_bytes()
            if any(byte > 127 for byte in data):
                self.fail(f"Non-ASCII content: {relative}")
            if data and not data.endswith(b"\n"):
                self.fail(f"Missing final newline: {relative}")
            text = data.decode("ascii", errors="replace")
            for line_number, line in enumerate(text.splitlines(), start=1):
                if line.endswith((" ", "\t")):
                    self.fail(f"Trailing whitespace: {relative}:{line_number}")
            if relative not in stale_exclusions:
                for stale in stale_patterns:
                    if stale in text:
                        self.fail(f"Stale identifier {stale} in {relative}")
                if "/Users/" in text or "C:\\Users\\" in text:
                    self.fail(f"User-specific absolute path in {relative}")

    def run(self) -> int:
        self.validate_manifests()
        self.validate_skill()
        self.validate_agents()
        self.validate_markdown_links()
        self.validate_repository_files()
        self.validate_text_files()

        validate_script = self.root / "scripts/validate.sh"
        if validate_script.is_file() and not os.access(validate_script, os.X_OK):
            self.fail("scripts/validate.sh must be executable")

        if self.errors:
            for error in self.errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print(f"StartBuilding validation failed with {len(self.errors)} error(s).", file=sys.stderr)
            return 1
        print("StartBuilding plugin is valid.")
        return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate.py <plugin-root>", file=sys.stderr)
        return 2
    return Validation(Path(sys.argv[1]).resolve()).run()


if __name__ == "__main__":
    raise SystemExit(main())
