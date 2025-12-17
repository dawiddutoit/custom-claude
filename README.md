# Claude Skills & Plugins Collection

A collection of custom skills, agents, and plugins for Claude Code.

## Structure

```
├── custom-skills/      # Custom skill definitions
│   ├── bosl2-best-practices.md
│   ├── gridfinity-design-patterns.md
│   ├── openscad-code-organization.md
│   ├── openscad-library-reference.md
│   ├── openscad-mcp-workflow.md
│   └── solidpython2-integration.md
├── custom-agents/      # Custom agent definitions
│   └── skills-researcher.md
└── plugins/            # Claude plugins from marketplace
    ├── agent-sdk-dev/
    ├── code-review/
    ├── commit-commands/
    ├── feature-dev/
    ├── frontend-design/
    ├── hookify/
    ├── plugin-dev/
    ├── pr-review-toolkit/
    ├── ralph-wiggum/
    ├── security-guidance/
    └── ...
```

## Installation

Copy skills to your Claude config:
```bash
cp custom-skills/* ~/.claude/skills/
cp custom-agents/* ~/.claude/agents/
```

## Custom Skills

### OpenSCAD Skills
- **bosl2-best-practices.md** - BOSL2 library patterns and best practices
- **gridfinity-design-patterns.md** - Gridfinity system design patterns
- **openscad-code-organization.md** - Code organization for OpenSCAD projects
- **openscad-library-reference.md** - Quick reference for OpenSCAD libraries
- **openscad-mcp-workflow.md** - MCP server workflow for OpenSCAD
- **solidpython2-integration.md** - SolidPython2 integration guide

## License

MIT
