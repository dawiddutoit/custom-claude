# Infrastructure Guide Reference

**This is a reference pointer to the comprehensive SSH infrastructure guide.**

The complete documentation is maintained at:
`/Users/dawiddutoit/.claude/artifacts/2026-01-01/infrastructure/SSH_INFRASTRUCTURE_GUIDE.md`

## Why This Structure?

The infrastructure guide is 683 lines and contains:
- Complete service inventory for all 5 hosts
- Detailed connection details and SSH configuration
- Environment variable mappings
- Common workflows and troubleshooting guides
- Security notes and credential locations

To avoid duplication, this references/ directory points to the canonical source.

## Quick Access

**Read the full guide:**
```bash
# In Claude Code
Read /Users/dawiddutoit/.claude/artifacts/2026-01-01/infrastructure/SSH_INFRASTRUCTURE_GUIDE.md
```

**Or open in editor:**
```bash
code /Users/dawiddutoit/.claude/artifacts/2026-01-01/infrastructure/SSH_INFRASTRUCTURE_GUIDE.md
```

## What's in the Guide

### Section 1: Quick Reference
- SSH commands via `connect` function
- Common workflows

### Section 2: Infrastructure Inventory (5 Hosts)
1. **infra.local** - Primary infrastructure (16+ services)
2. **deus** - Development machine
3. **homeassistant.local** - Home automation
4. **pi4-motor.local** - Raspberry Pi (offline)
5. **armitage.local** - WSL2 PC (offline)

### Section 3: Best Practices
- Service discovery patterns
- MongoDB usage for NomNom project
- Observability integration
- SSH key management
- File synchronization
- Docker remote management

### Section 4: Common Workflows
- Starting NomNom development
- Checking Claude Code telemetry
- Troubleshooting remote services
- Home Assistant integration

### Section 5: Environment Variables
- Infrastructure endpoints
- SSH aliases
- Service URLs

### Section 6: Troubleshooting
- Connection refused errors
- SSH authentication failures
- Service restart loops
- Port availability issues

## When to Read the Full Guide

**Read the comprehensive guide when:**
1. First-time infrastructure setup
2. Troubleshooting complex service issues
3. Understanding environment variable mappings
4. Learning Docker Compose management patterns
5. Setting up new hosts or services
6. Investigating security/credential locations

**Use the skill's SKILL.md when:**
1. Quick service discovery
2. Standard health checks
3. Common workflows (NomNom, observability)
4. Following established patterns

## Progressive Disclosure

The skill follows the 80/20 rule:
- **SKILL.md** handles 80% of use cases (discovery, health checks, common workflows)
- **infrastructure_guide.md** handles 20% of advanced use cases (detailed troubleshooting, environment setup, comprehensive reference)

This avoids loading 683 lines into context when only basic service checks are needed.
