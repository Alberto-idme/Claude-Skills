# Installed Skills

Snapshot of the Claude Code skills, plugins, agents, and commands installed locally on `alberto.carvajal@id.me`'s machine at the time of this commit.

## Layout

| Path | Source | Notes |
|---|---|---|
| `skills/` | `~/.claude/skills/` | User-level standalone skills. Symlinks resolved. |
| `plugins-cache/` | `~/.claude/plugins/cache/` | Plugin marketplaces (autoresearch, claude-plugins-official, context7, godmode, idme-config, openai-codex, superpowers-dev, superpowers-lab-local, ui-ux-pro-max-skill). |
| `agents/` | `~/.claude/agents/` | User-level subagent definitions. |
| `commands/` | `~/.claude/commands/` | User-level command definitions (autoresearch, gsd). |
| `installed_plugins.json` | `~/.claude/plugins/installed_plugins.json` | Plugin manifest — versions, install paths, install timestamps. |

## Exclusions

The following were intentionally excluded to keep the repo within GitHub limits:

- `node_modules/`
- `.venv/`
- `__pycache__/` and `*.pyc`
- `.git/` (nested git repos flattened)
- `.DS_Store`
- Compiled binaries: `*.metallib`, `*.dylib`, `*.so`
- Specific large compiled binaries inside `gstack/`:
  - `bin/gstack-global-discover`
  - `browse/dist/{browse,find-browse}`
  - `design/dist/design`
  - `make-pdf/dist/pdf`
  - `node_modules/@anthropic-ai/claude-agent-sdk-darwin-arm64/claude`

To rebuild any excluded artifacts, reinstall the corresponding plugin or run the skill's local install script.

## Symlink handling

`~/.claude/skills/` contains many symlinks pointing into `~/.agents/skills/` (Anthropic-bundled skills). Those were **resolved during copy** (`rsync -aL`) so the contents are real files in this repo, not broken links.
