# Anthropic Skill-Creator Patterns

Source: [Anthropic skills repository](https://github.com/anthropics/skills/tree/main/skill-creator)

---

## Core Principles

### 1. Concise is Key

> "The context window is a public good."

Skills share context with: system prompt, conversation history, other Skills' metadata, and user requests.

**Default assumption:** Claude is already very smart. Only add context Claude doesn't already have.

**Challenge each piece of information:**
- "Does Claude really need this explanation?"
- "Does this paragraph justify its token cost?"

**Prefer:** Concise examples over verbose explanations.

### 2. Set Appropriate Degrees of Freedom

Match specificity to task fragility and variability:

| Level | When to Use | Example |
|-------|-------------|---------|
| **High freedom** (text instructions) | Multiple valid approaches, context-dependent decisions | "Choose appropriate styling" |
| **Medium freedom** (pseudocode/scripts with params) | Preferred pattern exists, some variation OK | "Use this template, adjust X" |
| **Low freedom** (specific scripts, few params) | Fragile/error-prone operations, consistency critical | "Run this exact script" |

> "Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom)."

## Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/      - Executable code
    ├── references/   - Documentation for context
    └── assets/       - Files used in output
```

## Bundled Resources

### scripts/

Executable code for tasks requiring deterministic reliability or repeatedly rewritten.

**When to include:**
- Same code rewritten repeatedly
- Deterministic reliability needed

**Benefits:**
- Token efficient
- Deterministic
- Can execute without loading into context

**Note:** Scripts may still need to be read for patching or environment adjustments.

### references/

Documentation loaded as needed into context.

**When to include:**
- Database schemas
- API documentation
- Domain knowledge
- Company policies
- Detailed workflow guides

**Best practices:**
- If >10k words, include grep patterns in SKILL.md
- Keep only essential info in SKILL.md
- Avoid duplication between SKILL.md and references

### assets/

Files NOT loaded into context, used in output.

**When to include:**
- Templates
- Images, icons
- Boilerplate code
- Fonts
- Sample documents

## What NOT to Include

Do NOT create auxiliary documentation:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- User-facing documentation
- Setup/testing procedures

> "The skill should only contain information needed for an AI agent to do the job. It should not contain auxiliary context about the creation process."

## Progressive Disclosure Patterns

Keep SKILL.md under 500 lines. Split when approaching this limit.

### Pattern 1: High-level Guide with References

```markdown
## Quick start
[Basic example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

### Pattern 2: Domain-specific Organization

```
bigquery-skill/
├── SKILL.md (overview + navigation)
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

When user asks about sales, Claude only reads sales.md.

### Pattern 3: Conditional Details

```markdown
## Creating documents
Use docx-js. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

### Guidelines

- Avoid deeply nested references (one level from SKILL.md)
- Structure files >100 lines with table of contents
- Reference files should link directly from SKILL.md

## Description Best Practices

The description is the **primary triggering mechanism**.

**Include:**
1. What the Skill does
2. Specific triggers/contexts for when to use it

**Critical:** All "when to use" information goes in the description, NOT in the body. The body only loads AFTER triggering.

**Example (docx skill):**
```yaml
description: Comprehensive document creation, editing, and analysis with support
  for tracked changes, comments, formatting preservation, and text extraction.
  Use when Claude needs to work with professional documents (.docx files) for:
  (1) Creating new documents, (2) Modifying or editing content, (3) Working with
  tracked changes, (4) Adding comments, or any other document tasks
```

## Writing Guidelines

Always use imperative/infinitive form:
- "Create X" not "You should create X"
- "Run the script" not "You need to run the script"

## Output Patterns

### Template Pattern (Strict)

```markdown
ALWAYS use this exact template:

# [Title]
## Executive summary
[One-paragraph overview]
## Key findings
- Finding 1
- Finding 2
```

### Template Pattern (Flexible)

```markdown
Sensible default format, use your best judgment:

# [Title]
## Executive summary
[Overview]
## Key findings
[Adapt based on what you discover]
```

### Examples Pattern

For quality-dependent output, provide input/output pairs:

```markdown
**Example 1:**
Input: Added user authentication with JWT tokens
Output:
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

## Workflow Patterns

### Sequential Workflows

```markdown
Filling a PDF form involves:
1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
```

### Conditional Workflows

```markdown
1. Determine modification type:
   **Creating new?** → Follow "Creation workflow"
   **Editing existing?** → Follow "Editing workflow"

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## 6-Step Creation Process

1. **Understand** with concrete examples
2. **Plan** reusable contents (scripts, references, assets)
3. **Initialize** the skill (run init script)
4. **Edit** the skill (implement resources, write SKILL.md)
5. **Package** the skill (run package script)
6. **Iterate** based on real usage
