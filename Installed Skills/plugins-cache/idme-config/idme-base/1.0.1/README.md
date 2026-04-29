# idme-base

**Single-install AI development course materials**: 15 agents, 5 skills, 4 commands, and 3 MCP servers.

## Installation

```bash
# In Claude Code - that's it, one command!
/plugin marketplace add ./
/plugin install idme-base@baseline
```

Then restart Claude Code to activate MCP servers.

## What's Included

### MCP Servers (3)

| Server | Purpose |
|--------|---------|
| **allPepper-memory-bank** | Local document scratch pad at `~/.claude/memory-bank` |
| **sequential-thinking** | Structured reasoning for complex problem-solving |
| **chromadb** | Vector database at `~/.claude/chromadb` for semantic search |

### Agents (15)

**Java Development**
- `java-architect-planner` - Architecture design and phased execution planning
- `java-developer` - Test-first implementation with Maven expertise
- `java-debugger` - Systematic bug investigation and performance profiling

**React Development**
- `react-architect-planner` - React/Next.js architecture and component design
- `react-developer` - Test-first React with Vitest/RTL
- `react-debugger` - Hooks, hydration, and performance debugging

**Research & Analysis**
- `adr-researcher` - Gathers info for Architectural Decision Records
- `deep-research-synthesizer` - Multi-source research synthesis
- `deep-analyst` - Complex problem analysis and root cause investigation

**Code Quality**
- `code-review-expert` - Post-implementation code review
- `codebase-deep-analyzer` - Architecture patterns and technical debt analysis
- `plan-auditor` - Plan review and validation

**Knowledge Management**
- `knowledge-tidier` - ChromaDB and memory bank consolidation
- `pdf-chromadb-processor` - PDF processing and ChromaDB storage
- `project-management-setup` - Multi-week project infrastructure

### Skills (5)

| Skill | Purpose |
|-------|---------|
| `adr-writer` | ADR document writer (<900 words) |
| `api-council-writer` | API Council documentation |
| `arb-writer` | Architecture Review Board documentation |
| `design-document-writer` | Technical design documents |
| `writer` | RDR (Recommendation/Decisioning Record) writer |

### Commands (4)

| Command | Purpose |
|---------|---------|
| `/rdr:implement` | Spawn beads issues from locked RDR |
| `/rdr:init` | Initialize project with RDR workflow |
| `/rdr:status` | Show RDR project status |
| `/rdr:validate` | Validate RDR completeness |

## Verification

After installation and restart:

```bash
# Check MCP servers are running
/mcp

# Verify agents loaded
/agent list

# Test a skill
/adr-writer
```

## Beads Integration

For issue tracking, also install Beads:

```bash
/plugin marketplace add steveyegge/beads
/plugin install beads
```

Then run `/beads:workflow` to see the AI-supervised workflow guide.

## Customization

After installation, you can modify agents or create your own. See **[CUSTOMIZATION.md](../../CUSTOMIZATION.md)** for:

- How to safely modify installed agents
- Creating custom agents from scratch
- Model, color, and tool options
- Best practices and examples

**Quick tip**: Copy agents before editing to prevent losing changes on reinstall:
```bash
cp ~/.claude/agents/java-developer.md ~/.claude/agents/my-java-developer.md
```

## Troubleshooting

### MCP servers not showing

1. Restart Claude Code after installation
2. Check `~/.claude/mcp_servers.json` exists
3. Verify directories exist: `~/.claude/memory-bank`, `~/.claude/chromadb`

### Agents not loading

1. Verify installation: `/plugin list`
2. Check agent files: `ls ~/.claude/agents/`
3. Reinstall: `/plugin uninstall idme-base@baseline && /plugin install idme-base@baseline`

### ChromaDB issues

Requires Python 3.13 and uvx:
```bash
brew install uv
uvx --python 3.13 chroma-mcp --version
```

### Memory Bank issues

Requires Node.js >= 18:
```bash
node --version  # Should be 18+
npx @allpepper/memory-bank-mcp --version
```

## License

Apache-2.0
