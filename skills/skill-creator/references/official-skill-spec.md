# Official Agent Skills Specification

Source: [Anthropic skills repository](https://github.com/anthropics/skills) - agent_skills_spec.md

---

## Overview

A skill is a folder of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks. In order for the folder to be recognized as a skill, it must contain a `SKILL.md` file.

## Skill Folder Layout

### Minimum Structure

```
my-skill/
  - SKILL.md
```

More complex skills can add additional directories and files as needed.

## The SKILL.md File

The skill's "entrypoint" is the `SKILL.md` file. It is the only file required to exist. The file must start with a YAML frontmatter followed by regular Markdown.

## YAML Frontmatter

### Required Properties

| Property | Description | Constraints |
|----------|-------------|-------------|
| `name` | The name of the skill in hyphen-case | Lowercase Unicode alphanumeric + hyphen. Must match directory name. |
| `description` | Description of what the skill does and when Claude should use it | Non-empty, max 1024 characters |

### Optional Properties

| Property | Description | Notes |
|----------|-------------|-------|
| `license` | License applied to the skill | Keep short (license name or bundled file reference) |
| `allowed-tools` | List of tools pre-approved to run | Currently only supported in Claude Code |
| `metadata` | Map of string keys to string values | For client-specific properties |

## Name Field Restrictions

- Lowercase letters only
- Numbers allowed
- Hyphens allowed
- No XML tags
- No reserved words: "anthropic", "claude"
- Maximum 64 characters

## Markdown Body

The Markdown body has no restrictions on it.

## Version History

- 1.0 (2025-10-16) Public Launch
