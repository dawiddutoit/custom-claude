# Claude Code Skills Collection

A comprehensive collection of 105+ production-ready skills for Claude Code, organized by domain and use case.

## 📦 What's Inside

- **105+ Skills** - Reusable workflows for architecture, testing, quality gates, Home Assistant, web development, and more
- **Agents** - Specialized autonomous agents for complex tasks
- **Plugins** - Extended functionality via Claude Code plugins
- **Commands** - Custom command-line tools

## 🚀 Quick Start

### Installation

Copy skills to your Claude config directory:

```bash
# Clone the repository
git clone https://github.com/dawiddutoit/custom-claude.git
cd custom-claude

# Install all skills
cp -r skills/* ~/.claude/skills/

# Install agents (optional)
cp -r agents/* ~/.claude/agents/
```

### Usage

Skills are invoked automatically by Claude Code when relevant, or you can explicitly trigger them:

```bash
# Run a specific skill
/skill quality-run-quality-gates

# List available skills
/skills
```

## 📚 Skills Catalog

### Architecture & Design (5 skills)
- `architecture-single-responsibility-principle` - SRP validation using multi-dimensional detection
- `architecture-validate-architecture` - Clean Architecture, Hexagonal, Layered, MVC validation
- `architecture-validate-layer-boundaries` - Domain layer boundary enforcement
- `architecture-validate-srp` - AST-based SRP violation detection
- `create-adr-spike` - Architecture Decision Records and research spikes

### Quality Gates & Code Review (13 skills)
- `quality-capture-baseline` - Capture quality metrics baseline
- `quality-code-review` - Automated code review with best practices
- `quality-detect-orphaned-code` - Find unused code and dead imports
- `quality-detect-refactor-markers` - Identify TODO, FIXME, HACK markers
- `quality-detect-regressions` - Compare against baseline to detect regressions
- `quality-reflective-questions` - Code quality self-assessment
- `quality-run-linting-formatting` - Run linters and formatters
- `quality-run-quality-gates` - Comprehensive quality gate execution
- `quality-run-type-checking` - Type checking with mypy/pyright
- `quality-verify-implementation-complete` - Verify feature completeness
- `quality-verify-integration` - CCV (Creation+Connection+Verification) validation
- `editing-claude` - Validate and optimize CLAUDE.md files
- `artifacts-creating-and-managing` - Manage project artifacts (ADRs, spikes, analysis)

### Testing (11 skills)
- `test-debug-failures` - Systematic test failure debugging
- `test-first-thinking` - Test-first development workflow
- `test-implement-constructor-validation` - Constructor validation tests
- `test-implement-factory-fixtures` - Factory pattern fixtures
- `test-organize-layers` - Organize tests by architectural layer
- `test-property-based` - Property-based testing with Hypothesis
- `test-setup-async` - Async test setup and patterns
- `setup-pytest-fixtures` - pytest fixture configuration
- `textual-snapshot-testing` - Snapshot testing for Textual TUIs
- `textual-test-fixtures` - Textual test fixtures
- `textual-test-patterns` - Textual testing patterns

### Implementation Patterns (6 skills)
- `implement-cqrs-handler` - CQRS command/query handlers
- `implement-dependency-injection` - dependency-injector patterns
- `implement-feature-complete` - 10-stage feature implementation lifecycle
- `implement-repository-pattern` - Repository pattern (Protocol + Implementation)
- `implement-retry-logic` - Retry with exponential backoff
- `implement-value-object` - Immutable domain value objects

### Python Best Practices (3 skills)
- `python-best-practices-async-context-manager` - Async context manager patterns
- `python-best-practices-fail-fast-imports` - Fail-fast import validation
- `python-best-practices-type-safety` - Type safety best practices

### Observability (3 skills)
- `observability-analyze-logs` - Log analysis and debugging
- `observability-analyze-session-logs` - Session-specific log analysis
- `observability-instrument-with-otel` - OpenTelemetry instrumentation

### Home Assistant (14 skills)
- `ha-button-cards` - Button card configuration with actions
- `ha-conditional-cards` - Conditional card visibility
- `ha-custom-cards` - HACS custom cards (ApexCharts, gauges, bubbles)
- `ha-dashboard-cards` - Dashboard card creation with static titles
- `ha-dashboard-create` - Programmatic dashboard creation via WebSocket
- `ha-dashboard-layouts` - Layout patterns (grid, stack, panel)
- `ha-error-checking` - Dashboard debugging and validation
- `ha-graphs-visualization` - History graphs and time-series charts
- `ha-mqtt-autodiscovery` - MQTT auto-discovery for IoT devices
- `ha-mushroom-cards` - Minimalist Mushroom card ecosystem
- `ha-rest-api` - REST API integration
- `ha-sunsynk-integration` - Sunsynk/Deye solar inverter integration
- `ha-validate-dashboards` - 3-tier dashboard validation

### Browser Automation (10 skills)
- `browser-layout-editor` - 2D layout editors with FastAPI + SVG
- `chrome-auth-recorder` - Record authenticated workflows as GIFs
- `chrome-browser-automation` - Chrome automation via MCP
- `chrome-form-filler` - Safe form filling with verification
- `chrome-gif-recorder` - Record workflows as annotated GIFs
- `playwright-console-monitor` - Monitor browser console logs
- `playwright-e2e-testing` - End-to-end testing patterns
- `playwright-form-validation` - Form validation testing
- `playwright-network-analyzer` - Network request analysis
- `playwright-responsive-screenshots` - Responsive screenshot capture
- `playwright-tab-comparison` - Multi-tab comparison testing
- `playwright-web-scraper` - Web scraping patterns

### Svelte/SvelteKit (13 skills)
- `svelte-add-accessibility` - Accessibility best practices
- `svelte-add-component` - Component creation workflow
- `svelte-components` - Component patterns library
- `svelte-create-spa` - SPA creation from scratch
- `svelte-deployment` - Deployment strategies
- `svelte-extract-component` - Extract reusable components
- `svelte-migrate-html-to-spa` - Migrate HTML to Svelte SPA
- `svelte-runes` - Svelte 5 runes patterns
- `svelte-setup-state-store` - State management setup
- `svelte5-showcase-components` - Svelte 5 component showcase
- `sveltekit-data-flow` - Data loading and forms
- `sveltekit-remote-functions` - Remote function calling
- `sveltekit-structure` - Project structure patterns

### OpenSCAD & CAD (4 skills)
- `openscad-cutlist-woodworkers` - Woodworking cut list generation
- `openscad-labeling` - Part labeling and annotations
- `openscad-workshop-tools` - Workshop tool design patterns
- `scad-load` - OpenSCAD project loading

### Textual TUI Framework (10 skills)
- `textual-app-lifecycle` - App lifecycle management
- `textual-data-display` - Data tables and displays
- `textual-event-messages` - Event and message handling
- `textual-layout-styling` - Layout and CSS styling
- `textual-reactive-programming` - Reactive programming patterns
- `textual-testing` - Testing strategies
- `textual-widget-development` - Custom widget development
- `temet-run-tui-patterns` - Temet-specific TUI patterns

### Utilities & Workflow (6 skills)
- `util-manage-todo` - Todo list management
- `util-multi-file-refactor` - Multi-file refactoring
- `util-research-library` - Library research and evaluation
- `util-resolve-serviceresult-errors` - ServiceResult error resolution
- `write-atomic-tasks` - Atomic task decomposition
- `data-migration-versioning` - Data format migration and versioning

### Agent & SDK (3 skills)
- `claude-agent-sdk` - Claude Agent SDK patterns
- `manage-agents` - Agent lifecycle management
- `skill-creator` - Create and manage skills

### Domain-Specific (3 skills)
- `jira-builders` - JIRA integration builders
- `minimal-abstractions` - Minimal abstraction patterns
- `infra-manage-ssh-services` - SSH service management

## 🗂️ Repository Structure

```
.
├── skills/              # 105+ skill definitions
│   ├── architecture-*/  # Architecture & design skills
│   ├── quality-*/       # Quality gates & code review
│   ├── test-*/          # Testing skills
│   ├── implement-*/     # Implementation patterns
│   ├── ha-*/            # Home Assistant skills
│   ├── svelte-*/        # Svelte/SvelteKit skills
│   └── ...
├── agents/              # Custom agent definitions
├── plugins/             # Claude Code plugins
└── commands/            # Custom CLI commands
```

## 📖 Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md            # Skill definition and documentation
├── examples/           # Usage examples (optional)
└── tests/              # Validation tests (optional)
```

## 🤝 Contributing

Contributions welcome! To add a new skill:

1. Create a new directory in `skills/`
2. Add a `SKILL.md` file following the skill template
3. Test the skill thoroughly
4. Submit a PR with a clear description

## 📜 License

MIT

## 🔗 Related Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Claude Agent SDK](https://github.com/anthropics/claude-code-agent-sdk)
- [MCP Servers](https://modelcontextprotocol.io/)

## ✨ Highlights

### CCV Principle
Many skills enforce the **Creation + Connection + Verification** principle to ensure code isn't just written but actually integrated and working in production.

### Quality Gates
Comprehensive quality gate skills ensure code meets standards before merging:
- Type checking
- Linting and formatting
- Test coverage
- Regression detection
- Architecture validation

### Multi-Domain Support
Skills span multiple domains:
- Backend (Python, CQRS, repositories)
- Frontend (Svelte, SvelteKit)
- Home automation (Home Assistant)
- CAD/3D (OpenSCAD)
- TUI (Textual framework)
- Browser automation (Chrome, Playwright)

---

**Last Updated:** 2026-01-20
**Total Skills:** 105+
**Maintained by:** [@dawiddutoit](https://github.com/dawiddutoit)
