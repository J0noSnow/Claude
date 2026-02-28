# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working in this repository.

## Repository Overview

**Name:** Claude
**Description:** Test repository with claude
**Primary Branch:** `main`
**Development Branch Convention:** `claude/<description>-<session-id>`

This is currently a minimal repository. As the project grows, update this file to reflect new conventions, tooling, and structure.

## Repository Structure

```
/
├── README.md       # Project introduction
└── CLAUDE.md       # This file — AI assistant guidance
```

## Git Workflow

### Branching

- **Main branch:** `main` (protected; do not push directly)
- **Feature branches:** `claude/<short-description>-<session-id>`
- Always develop on the designated feature branch for the current session

### Commit Messages

Write clear, imperative commit messages:

```
Add CLAUDE.md with initial project documentation
Fix typo in README
Update workflow section with new conventions
```

- Use present tense ("Add" not "Added")
- Keep the subject line under 72 characters
- Reference issue numbers if applicable

### Push Procedure

```bash
git push -u origin <branch-name>
```

- Branch names must start with `claude/` for session branches
- Retry on network failure with exponential backoff: 2s, 4s, 8s, 16s

### Commit Signing

This repository uses GPG signing via SSH. Commits are automatically signed with the configured SSH key. Do not bypass signing (`--no-gpg-sign`) unless explicitly instructed.

## Development Conventions

### Adding New Code

When adding a technology stack or source files to this repo, update this CLAUDE.md with:

1. **Stack section** — languages, frameworks, key libraries
2. **Setup instructions** — how to install dependencies and run locally
3. **Testing section** — test commands and framework details
4. **Build section** — build commands and output locations
5. **Linting/formatting** — tools used and how to run them

### File Organization

Follow standard conventions for the language/framework being used. Document any project-specific deviations here.

## Working with This Repository

### Before Making Changes

1. Check the current branch: `git branch`
2. Confirm you are on the correct `claude/` feature branch
3. Pull latest changes: `git pull origin <branch-name>`

### After Making Changes

1. Stage relevant files: `git add <files>`
2. Commit with a descriptive message
3. Push: `git push -u origin <branch-name>`

### Things to Avoid

- Do not push to `main` or `master` directly
- Do not use `--no-verify` to skip hooks
- Do not force-push to shared branches without explicit permission
- Do not commit secrets, credentials, or `.env` files

## Updating This File

Keep this file current. When the repository gains:
- A tech stack → add a "Stack" and "Setup" section
- Tests → add a "Testing" section with commands
- CI/CD → add a "CI/CD" section describing pipelines
- Linters/formatters → add a "Code Quality" section
- Deployment → add a "Deployment" section

This file is the primary source of truth for AI assistants operating in this codebase.
