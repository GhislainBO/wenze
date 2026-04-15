# CLAUDE.md

## Project: WENZE

- **Concept:** Digital neighborhood marketplace (Kinshasa 🇨🇩 & Brazzaville 🇨🇬)
- **Stack:** Kivy (mobile), FastAPI (backend), SQLite (database)
- **Python max version:** 3.10
- **No KivyMD in Phase 1**
- **No heavy dependencies**
- **UI text:** All in French
- **Code (variables, functions, comments):** In English
- **Full product requirements:** See [PRD.md](PRD.md)

## Deferred features

- Image upload: postponed - requires persistent storage
  solution (Cloudinary or Supabase Storage) before implementation

## GitHub

- GitHub account: GhislainBO
- Authentication: configured (gh CLI, SSH protocol)
- Token scopes: `repo`, `workflow`, `read:org`
- Use `gh` CLI for all GitHub operations (create repo, push, pull requests, issues)
- Never use the browser for GitHub operations
- Remote repo will be created when Phase 1 is validated

## gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp claude-in-chrome_*` tools.

### Available skills

- `/office-hours` — YC-style office hours
- `/plan-code-review` — Code review plan
- `/plan-eng-review` — Engineering review plan
- `/plan-design-review` — Design review plan
- `/design-consultation` — Design system consultation
- `/review` — Pre-landing PR review
- `/ship` — Ship workflow (test, commit, push, PR)
- `/land-deploy` — Land and deploy workflow
- `/canary` — Post-deploy canary monitoring
- `/benchmark` — Performance regression detection
- `/browse` — Headless browser for QA and browsing
- `/qa` — QA test and fix bugs
- `/qa-only` — QA report only (no fixes)
- `/design-review` — Visual QA and fixes
- `/setup-browser-cookies` — Import browser cookies
- `/setup-deploy` — Configure deployment settings
- `/retro` — Weekly engineering retrospective
- `/investigate` — Systematic debugging
- `/document-release` — Post-ship docs update
- `/codex` — OpenAI Codex CLI wrapper
- `/cso` — Security audit
- `/autoplan` — Auto-review pipeline
- `/careful` — Safety guardrails for destructive commands
- `/freeze` — Restrict edits to a directory
- `/guard` — Full safety mode (careful + freeze)
- `/unfreeze` — Clear freeze boundary
- `/gstack-upgrade` — Upgrade gstack
