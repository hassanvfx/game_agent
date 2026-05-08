# ClineFlow Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses date-based versioning: `YYYY.MM.DD.patch`

## [2025.11.17.0] - 2025-11-17

### Added
- **Multi-Root Workspace Generation** - Complete fix for @ mention completion in Cline
  - `setup-refs.sh` now generates `.code-workspace` files automatically
  - Workspace files enable full VS Code indexing of all linked repositories
  - New `--workspace-only` flag to regenerate workspace without touching symlinks
  - Hybrid approach: symlinks for file browser + workspace for @ mentions
  
### Fixed
- **@ Mention Autocomplete** - Resolved issue where symlinked reference files didn't appear in Cline's @ mention suggestions
  - VS Code wasn't indexing symlinked directories
  - Multi-root workspace makes all repos first-class citizens
  - Full autocomplete now works for all linked repositories
  
### Changed
- Updated `template/.gitignore` to exclude `*.code-workspace` files (developer-specific paths)
- Enhanced reference system to be fully idempotent (safe to re-run anytime)
- Improved `setup-refs.sh` output with workspace file usage instructions

### Documentation
- Added "Troubleshooting: @ Mentions Not Working?" section to README.md
- Complete rewrite of `template/clineflow/README.md` usage section
- Documented dual access model (workspace vs symlinks)
- Added workspace vs folder comparison
- Clear upgrade path for existing users

---

## [2025.11.12.0] - 2025-11-12

### Added
- **SOP-008: Feature Branch Management** - New procedure ensuring all development happens on feature branches
  - Automatic branch checking before starting tasks
  - Standard Git Flow branch naming conventions (feature/, fix/, docs/, refactor/)
  - Integration with existing SOPs for complete workflow
  - Protects main branch from direct commits
  
- **Update System** - Complete update mechanism for existing installations
  - `update.sh` script for safe, selective updates
  - Preserves user customizations (.clinerules, .clineflow.local, journals)
  - `--dry-run` option to preview updates
  - `--yes` flag for automated updates
  - Smart file comparison to detect actual changes
  
- **Version Tracking** - Date-based semantic versioning
  - `VERSION` file tracks current installation
  - Format: YYYY.MM.DD.patch (e.g., 2025.11.12.0)
  - Displayed during updates for clear tracking

### Changed
- Updated "Before Starting Any Task" checklist to include branch verification
- Enhanced PROCEDURES.md with comprehensive branch management guidance
- All template files now include version-aware update system

### Documentation
- Added complete branch management workflows for solo developers and teams
- Documented integration between SOP-008 and existing procedures
- Created this CHANGELOG for tracking all future updates

---

## [Previous Releases]

### [2025.11.11.0] - 2025-11-11
- AI-assisted installation as primary method
- Agent-agnostic support (Cline, Cursor, Copilot, Windsurf)
- Updated README with prominent AI installation option

### [2025.11.10.0] - 2025-11-10
- Viral README enhancement with ASCII art and Mermaid diagrams
- Real dogfooding proof with development journal link
- "Senior VibeCoding" branding
- Complete visual storytelling

### [2025.11.09.0] - 2025-11-09
- Multi-line git commit safety (SOP-007)
- Heredoc pattern for reliable commits
- Document Driven Development (DDD) positioning
- Comprehensive uninstall system

### [2025.11.08.0] - 2025-11-08
- Initial ClineFlow release (rebranded from llm-refs)
- Intelligent commit workflow (SOP-005)
- Task journal management (SOP-006)
- Reference system with symlink safety
- Auto-configured .gitignore

---

## Update Instructions

### For Existing Users

To update your ClineFlow installation to the latest version:

```bash
# Download and run update script
curl -fsSL https://raw.githubusercontent.com/hassanvfx/clineflow/main/update.sh | bash

# Or if you already have it
./update.sh
```

**What gets updated:**
- Template documentation files (clineflow/*)
- Setup scripts (setup-refs.sh)
- Configuration examples (.clineflow.example)

**What stays protected:**
- Your custom rules (.clinerules)
- Your local config (.clineflow.local)
- All your journals (docs/journals/*)

### Preview Before Updating

```bash
# See what would change without modifying anything
curl -fsSL https://raw.githubusercontent.com/hassanvfx/clineflow/main/update.sh | bash -s -- --dry-run
```

### Version Check

```bash
# Check your current version
cat VERSION

# Latest version available
curl -fsSL https://raw.githubusercontent.com/hassanvfx/clineflow/main/VERSION
```

---

## Versioning Scheme

ClineFlow uses **date-based versioning** with semantic patches:

- `YYYY.MM.DD.patch`
- Example: `2025.11.12.0`
- Patch increments for same-day releases
- Major changes update date

**Benefits:**
- Clear chronological tracking
- Easy to see update frequency
- Semantic patch number for hotfixes

---

## Breaking Changes Policy

We strive to maintain backward compatibility. When breaking changes are necessary:

1. **Major version bump** - Date changes significantly (e.g., monthly release)
2. **Migration guide** - Detailed steps in changelog entry
3. **Deprecation warnings** - At least one release cycle notice
4. **Update script handles** - Automatic migration when possible

---

## Support

- **Issues**: [GitHub Issues](https://github.com/hassanvfx/clineflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hassanvfx/clineflow/discussions)
- **Updates**: Watch this repository for release notifications

---

## Contributing

Found a bug? Have a feature request? 

1. Check [existing issues](https://github.com/hassanvfx/clineflow/issues)
2. Open a new issue with details
3. Use ClineFlow to document your contribution!

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) principles.*
