# Custom Claude Code Repository

**Version:** 1.0.0 | **Last Updated:** 2026-01-21 | **Scope:** Skills, Plugins, Agents, Commands for Claude Code

## Repository Purpose

This repository maintains a production-ready collection of 190+ Claude Code extensions including:
- **Skills** - Model-invoked capabilities that auto-trigger based on context
- **Plugins** - Extended functionality packages with commands, skills, agents, hooks, MCP
- **Agents** - Specialized autonomous agents for complex tasks
- **Commands** - Custom CLI commands

## Critical Principles

### 1. Progressive Disclosure
All skills and plugins MUST follow three-level disclosure:
1. **Metadata** (YAML frontmatter) - Concise description with strong triggers (always loaded)
2. **Core Content** (SKILL.md/README.md) - Essential reference (~1,500-2,000 words)
3. **Resources** (references/, examples/, scripts/) - Deep guides loaded as needed

### 2. Strong Triggers
Skills must have **specific trigger phrases** that reliably invoke them:
- ✅ GOOD: "create a hook", "add a PreToolUse hook", "validate tool use"
- ❌ BAD: "help with hooks", "hook stuff", "work on hooks"

### 3. Quality Standards
Before marking any skill/plugin/agent complete:
- [ ] Tested in real Claude Code session
- [ ] Examples are working and verified
- [ ] Documentation is clear and complete
- [ ] YAML frontmatter is valid
- [ ] References/examples organized properly
- [ ] README updated if new skill/plugin added

### 4. Fail-Fast Philosophy
- No silent failures or degraded functionality
- No placeholder stubs or "best effort" code
- Explicit errors over implicit fallbacks
- If something can't be done, document why and what's needed

## Repository Structure

```
custom-claude/
├── skills/              # 190+ skill definitions
│   └── {skill-name}/
│       ├── SKILL.md            # Core skill definition (required)
│       ├── examples/           # Working examples (optional)
│       ├── references/         # Deep reference docs (optional)
│       └── scripts/            # Utility scripts (optional)
├── plugins/             # 13 plugin packages
│   └── {plugin-name}/
│       ├── .claude-plugin/
│       │   └── plugin.json     # Plugin manifest (required)
│       ├── README.md           # Plugin documentation (required)
│       ├── commands/           # Slash commands (optional)
│       ├── agents/             # Plugin-specific agents (optional)
│       ├── skills/             # Plugin-bundled skills (optional)
│       ├── hooks/              # Hook definitions (optional)
│       └── .mcp.json           # MCP server config (optional)
├── agents/              # 13 custom agents
│   └── {agent-name}.md         # Agent definition with frontmatter
├── commands/            # Custom commands
│   └── {command-name}.md       # Command definition with frontmatter
└── README.md            # Comprehensive catalog (keep updated!)
```

## Working with Skills

### Creating a New Skill

1. **Create directory structure:**
   ```bash
   mkdir -p skills/{skill-name}/{examples,references,scripts}
   ```

2. **Create SKILL.md with frontmatter:**
   ```markdown
   ---
   name: skill-name
   description: |
     Concise description with trigger phrases like "create X", "implement Y", "validate Z".

     Use when asked to "specific phrase", "another trigger", or "exact use case".
   version: 1.0.0
   tags: [category, domain, technology]
   ---

   # Skill Name

   Core content here (~1,500-2,000 words max)...
   ```

3. **Add examples (if applicable):**
   - Create working, tested examples in `examples/`
   - Use descriptive filenames: `basic-usage.md`, `advanced-pattern.md`

4. **Add references (if needed):**
   - Deep dives, API docs, patterns in `references/`
   - Keep core SKILL.md lean, move details here

5. **Add utility scripts (if applicable):**
   - Validation, testing, or helper scripts in `scripts/`
   - Make executable: `chmod +x scripts/*.sh`

6. **Update README.md:**
   - Add skill to appropriate category
   - Include one-line description
   - Keep catalog organized and alphabetized

### Skill Standards

**Frontmatter Requirements:**
- `name` - kebab-case, matches directory name
- `description` - Include specific trigger phrases
- `version` - Semantic versioning (1.0.0)
- `tags` - Relevant categories for searchability

**Content Guidelines:**
- Write in **imperative/infinitive form** ("Use this skill to...", "This skill provides...")
- Third-person perspective ("This skill should be used when...")
- Core SKILL.md: 1,500-2,000 words maximum
- Move lengthy content to references/
- Include "When to Use" and "When NOT to Use" sections

**Testing Requirements:**
- Test skill invocation with trigger phrases
- Verify examples actually work
- Test in clean Claude Code session
- Validate YAML frontmatter parses correctly

## Working with Plugins

### Creating a New Plugin

Use the plugin-dev toolkit when available:
```bash
/plugin-dev:create-plugin [optional description]
```

Or manually:

1. **Create plugin structure:**
   ```bash
   mkdir -p plugins/{plugin-name}/{.claude-plugin,commands,agents,skills,hooks}
   ```

2. **Create plugin.json manifest:**
   ```json
   {
     "name": "plugin-name",
     "version": "1.0.0",
     "description": "Brief plugin description",
     "author": "Your Name",
     "commands": {
       "command-name": "${CLAUDE_PLUGIN_ROOT}/commands/command-name.md"
     },
     "agents": {
       "agent-name": "${CLAUDE_PLUGIN_ROOT}/agents/agent-name.md"
     },
     "skills": [
       "${CLAUDE_PLUGIN_ROOT}/skills/skill-name"
     ],
     "hooks": "${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json"
   }
   ```

3. **Create comprehensive README.md:**
   - Overview and features
   - Installation instructions
   - Usage examples
   - Component descriptions
   - Troubleshooting section

4. **Add components:**
   - Commands: Slash commands with YAML frontmatter
   - Agents: Autonomous agents for complex tasks
   - Skills: Bundled skills (follow skill standards above)
   - Hooks: Event-driven automation (PreToolUse, PostToolUse, Stop, etc.)

5. **Test thoroughly:**
   ```bash
   cc --plugin-dir /path/to/custom-claude/plugins/{plugin-name}
   ```

### Plugin Standards

**Always use ${CLAUDE_PLUGIN_ROOT}** for portable paths in:
- plugin.json references
- Hook script paths
- Command file references
- Agent file references

**Documentation Requirements:**
- Comprehensive README.md (200+ lines for complex plugins)
- Usage examples for all commands
- Troubleshooting section
- Component descriptions

**Quality Checklist:**
- [ ] plugin.json is valid JSON
- [ ] All paths use ${CLAUDE_PLUGIN_ROOT}
- [ ] README includes installation and usage
- [ ] Commands have proper frontmatter
- [ ] Hooks validated with scripts (if applicable)
- [ ] Tested in clean Claude Code environment

## Working with Agents

### Creating a New Agent

1. **Create agent file in agents/ directory:**
   ```markdown
   ---
   name: agent-name
   description: |
     Describe when to use this agent with specific triggers.

     Use for "specific task", "complex workflow", or "specialized operation".
   model: sonnet  # or opus, haiku
   color: blue    # for UI (optional)
   tools: [Read, Write, Edit, Bash, Grep, Glob]  # Available tools
   ---

   # System Prompt for Agent

   You are a specialized agent for [purpose].

   ## Your Role
   [Describe agent's specific expertise and responsibilities]

   ## Approach
   [Describe methodology and workflow]

   ## Standards
   [Quality requirements and constraints]

   ## Output Format
   [How agent should structure deliverables]
   ```

2. **Test agent invocation:**
   - Verify trigger phrases work
   - Test with real tasks
   - Validate tool restrictions are appropriate

3. **Update README.md:**
   - Add to agents section if not plugin-specific

### Agent Standards

**Frontmatter Requirements:**
- `name` - kebab-case identifier
- `description` - Clear triggers with specific phrases
- `model` - Appropriate model for task complexity
- `tools` - Only tools agent actually needs (principle of least privilege)

**System Prompt Guidelines:**
- Clear role definition
- Specific methodology
- Quality standards
- Output format expectations
- Constraints and boundaries

## Working with Commands

### Creating a New Command

1. **Create command file:**
   ```markdown
   ---
   description: Brief description for /help
   argument-hint: <required-arg> [optional-arg]
   allowed-tools: [Read, Glob, Grep, Bash]
   ---

   # Command Implementation

   Instructions for Claude on what to do when command is invoked.

   ## Steps
   1. First step
   2. Second step
   3. Final step

   ## Examples
   Show usage examples
   ```

2. **Register in plugin.json (if plugin command):**
   ```json
   "commands": {
     "command-name": "${CLAUDE_PLUGIN_ROOT}/commands/command-name.md"
   }
   ```

3. **Test command:**
   ```bash
   /command-name arg1 arg2
   ```

## File Naming Conventions

### Skills
- Directory: `kebab-case-name/`
- Main file: `SKILL.md`
- Examples: `examples/descriptive-name.md`
- References: `references/topic-name.md`
- Scripts: `scripts/action-name.sh`

### Plugins
- Directory: `kebab-case-name/`
- Manifest: `.claude-plugin/plugin.json`
- README: `README.md`
- Components follow same pattern as standalone

### Agents
- File: `kebab-case-name.md`
- Located in `agents/` (global) or `plugins/{plugin}/agents/` (plugin-specific)

### Commands
- File: `kebab-case-name.md`
- Located in `commands/` (global) or `plugins/{plugin}/commands/` (plugin-specific)

## Domain Coverage

When creating new skills/plugins/agents, consider these covered domains:
- Architecture & Design
- Quality Gates & Code Review
- Testing (pytest, Playwright, snapshot)
- Implementation Patterns (CQRS, Repository, DI, Value Objects)
- Home Assistant (dashboards, MQTT, custom cards)
- Browser Automation (Chrome, Playwright)
- Svelte/SvelteKit
- Textual TUI Framework
- Data Engineering (ClickHouse, Kafka)
- Infrastructure & Cloud (GCP, Cloudflare, Caddy, Terraform)
- Python Tools & Testing
- Java Development & Gradle
- JIRA & Atlassian
- Lotus Notes Migration
- Observability (OpenTelemetry, Micrometer)
- OpenSCAD & CAD
- Utilities & Workflow

**Gap Analysis:** Before creating new content, check if similar functionality exists in related domains.

## README.md Maintenance

The main README.md is the **source of truth** catalog. When adding new content:

1. **Add to appropriate section:**
   - Skills: Add to domain category with one-line description
   - Plugins: Add to plugins list with overview
   - Agents: Add to agents section
   - Commands: Add to commands section

2. **Update statistics:**
   - Skill count
   - Plugin count
   - Agent count
   - Last updated date

3. **Keep organized:**
   - Alphabetize within categories
   - Use consistent formatting
   - Include trigger keywords in descriptions

4. **Update structure diagram if needed:**
   - Add new categories if domains expand

## Testing & Validation

### Before Committing

**For Skills:**
```bash
# Test skill invocation
cc  # Start new session
# Use trigger phrases, verify skill loads

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('skills/{name}/SKILL.md').read().split('---')[1])"

# Test examples if included
# Run any scripts/utilities
```

**For Plugins:**
```bash
# Test plugin loading
cc --plugin-dir plugins/{plugin-name}

# Test all commands
/plugin-command

# Validate plugin.json
python3 -c "import json; json.load(open('plugins/{name}/.claude-plugin/plugin.json'))"

# Test hooks if included (use plugin-dev utilities)
```

**For Agents:**
```bash
# Test agent invocation
# Use trigger phrases in Claude Code

# Validate YAML frontmatter
python3 -c "import yaml; yaml.safe_load(open('agents/{name}.md').read().split('---')[1])"
```

### Quality Gates

Run before committing:
- [ ] All YAML frontmatter is valid
- [ ] All JSON files are valid
- [ ] Examples are tested and working
- [ ] Documentation is complete and accurate
- [ ] README.md is updated
- [ ] No placeholder or stub content
- [ ] Scripts are executable (`chmod +x`)

## Common Patterns

### Skill with References Pattern
```
skill-name/
├── SKILL.md                    # Core content (1,500 words)
├── examples/
│   ├── basic-usage.md         # Simple example
│   └── advanced-usage.md      # Complex example
├── references/
│   ├── api-reference.md       # Deep API docs
│   ├── patterns.md            # Design patterns
│   └── troubleshooting.md     # Common issues
└── scripts/
    ├── validate.sh            # Validation script
    └── test.sh                # Testing script
```

### Plugin with All Components Pattern
```
plugin-name/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── commands/
│   ├── main-command.md
│   └── helper-command.md
├── agents/
│   └── specialized-agent.md
├── skills/
│   └── plugin-skill/
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       └── validation-hook.sh
└── .mcp.json
```

## Anti-Patterns to Avoid

❌ **Vague Triggers**
```yaml
description: This skill helps with testing stuff
```
✅ **Specific Triggers**
```yaml
description: |
  Use when asked to "create pytest fixtures", "set up test factories",
  or "implement fixture patterns for integration tests".
```

❌ **Monolithic Skills**
```markdown
# Testing Skill (10,000 words)
Everything about testing in one file...
```
✅ **Progressive Disclosure**
```markdown
# Testing Skill (1,500 words)
Core concepts...
See references/pytest-patterns.md for deep dive...
```

❌ **Placeholder Content**
```markdown
## Examples
Coming soon...
```
✅ **Working Examples**
```markdown
## Examples
See examples/basic-fixture.py for working pytest fixture example.
```

❌ **Hardcoded Paths**
```json
"commands": {
  "test": "/Users/dawid/.claude/plugins/test/commands/test.md"
}
```
✅ **Portable Paths**
```json
"commands": {
  "test": "${CLAUDE_PLUGIN_ROOT}/commands/test.md"
}
```

## Contribution Workflow

1. **Create new content** following standards above
2. **Test thoroughly** in clean Claude Code session
3. **Update README.md** with new content
4. **Validate all YAML/JSON** files
5. **Commit with descriptive message:**
   ```bash
   git add .
   git commit -m "Add {skill/plugin/agent name} for {purpose}"
   ```

## Key Resources

- **Plugin-Dev Toolkit:** Use `/plugin-dev:create-plugin` for structured plugin creation
- **Hookify Plugin:** Use `/hookify` for easy hook creation without JSON editing
- **Skill Creator Agent:** Invoke for AI-assisted skill creation following standards
- **Agent Creator:** Available in plugin-dev for AI-assisted agent generation

## Questions to Ask Before Creating New Content

1. **Does similar functionality exist?** Search existing skills/plugins first
2. **Is this a skill, plugin, agent, or command?**
   - Skill: Model-invoked capability, auto-triggered
   - Plugin: Package of multiple components
   - Agent: Autonomous specialist for complex tasks
   - Command: User-invoked slash command
3. **What are the specific trigger phrases?** List 3-5 concrete examples
4. **What domain does this cover?** Fit into existing categories or new domain?
5. **What's the core content size?** Should be ~1,500-2,000 words max for skills
6. **What examples are needed?** Working, tested examples that prove functionality
7. **What references would help?** Deep dives that don't fit in core content

## Success Criteria

New content is complete when:
- ✅ Tested in real Claude Code session
- ✅ Trigger phrases reliably invoke it
- ✅ Examples work as documented
- ✅ Documentation is clear and complete
- ✅ README.md is updated
- ✅ YAML/JSON validates correctly
- ✅ Scripts are executable (if applicable)
- ✅ Follows progressive disclosure principle
- ✅ No placeholders or "coming soon" content

---

**Remember:** This repository serves real development needs. Every skill, plugin, agent, and command should be production-ready, tested, and valuable.
