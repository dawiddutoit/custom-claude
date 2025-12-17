# Claude Code Skills Documentation

Source: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

---

## What Are Agent Skills?

Agent Skills are modular capabilities that extend Claude's functionality. They consist of a `SKILL.md` file with instructions that Claude reads when relevant, plus optional supporting files like scripts and templates.

Skills operate through **model invocation** - Claude autonomously decides when to use them based on your request and the Skill's description. This distinguishes them from user-invoked slash commands.

## Directory Locations

### Personal Skills
**Location:** `~/.claude/skills/my-skill-name/`
- Available across all projects
- For individual workflows and experimental Skills

### Project Skills
**Location:** `.claude/skills/my-skill-name/`
- Shared with teams via git
- For team conventions and project-specific expertise
- Automatically available when team members pull changes

### Plugin Skills
- Bundled with installed Claude Code plugins

## Typical Structure

```
my-skill/
├── SKILL.md (required)
├── reference.md (optional)
├── examples.md (optional)
├── scripts/ (optional utilities)
└── templates/ (optional)
```

## SKILL.md Format

```yaml
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
allowed-tools: Tool1, Tool2 (optional)
---

# Your Skill Name

## Instructions
[Step-by-step guidance]

## Examples
[Concrete usage examples]
```

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Lowercase letters, numbers, hyphens only (max 64 characters) |
| `description` | What the Skill does and when to use it (max 1024 characters) |

### Optional Fields

| Field | Description |
|-------|-------------|
| `allowed-tools` | Restricts which tools Claude can use (e.g., "Read, Grep, Glob" for read-only) |

## Description Best Practices

Write specific, discovery-focused descriptions including trigger terms.

**Effective:**
```
Analyze Excel spreadsheets, create pivot tables, and generate charts.
Use when working with Excel files, spreadsheets, or analyzing tabular
data in .xlsx format.
```

**Ineffective:**
```
Helps with documents
```

## Skill Design Best Practices

1. **Keep focused** - One capability per skill
2. **Clear instructions** - Step-by-step guidance
3. **Concrete examples** - Show how to use
4. **Version history** - Track changes (optional)

## Troubleshooting Discovery Issues

Claude may not use your Skill if:

| Issue | Solution |
|-------|----------|
| Vague description | Add trigger terms and specifics |
| Incorrect file path | Verify `SKILL.md` location |
| YAML syntax errors | Check indentation, missing `---` |
| Overlapping descriptions | Use distinct language from similar Skills |

## Sharing and Distribution

### Via Plugins (Recommended)
Create a plugin with Skills in the `skills/` directory.

### Via Git
```bash
mkdir -p .claude/skills/team-skill
# Create SKILL.md with content
git add .claude/skills/
git commit -m "Add team Skill"
```

Skills become immediately available to team members upon pulling changes.

## Key Advantages

1. Reduce repetitive prompting
2. Extend Claude's capabilities for specific workflows
3. Enable team expertise sharing through git
4. Compose multiple Skills for complex tasks
