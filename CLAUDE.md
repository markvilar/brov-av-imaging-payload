# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository stores notes and configurations for learning and using Claude Code. The notes are based on the [Net Ninja Claude Code Course](https://www.youtube.com/playlist?list=PL4cUxeGkcC9g4YJeBqChhFJwKQ9TRiivY) and the [Claude Code Masterclass](https://netninja.dev/p/claude-code-masterclass).

## MCP Servers

**context7** is configured as a project MCP server in `.mcp.json`. Use it to fetch up-to-date documentation when implementing features that involve libraries or frameworks. Always resolve the library ID first with `resolve-library-id`, then query with `query-docs`.

## Key Claude Code Concepts Covered in Notes

- **CLAUDE.md** (`02_claude.md`): project memory, local project memory, user memory, `/memory` command
- **Context management** (`03_context.md`): `@file` references, `/clear`, `/compact`, `/resume`, context window (~200K tokens)
- **Permissions** (`04_tools_and_permissions.md`): `.claude/settings.json` vs `.claude/settings.local.json`, deny/ask/allow tiers
- **Planning & Thinking** (`05_planning_and_thinking.md`): `/plan` for multi-step work; `think`/`think harder`/`ultrathink` keywords for extended reasoning
- **Custom slash commands** (`06_slash_commands.md`): defined in `.claude/commands/<name>.md`, support `$ARGUMENTS` via frontmatter
- **MCP servers** (`07_mcp_servers.md`): `claude mcp add` syntax, context7 for library docs
- **Spec-driven workflow** (`99_extras.md`): `/spec` → plan mode → implement with extended thinking + Opus

## Behavioral guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

Tradeoff: These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Git conventions

Never reference Claude in git commit messages, pull requests, or issues. This includes `Co-Authored-By` trailers, body text, or any other attribution to Claude or Anthropic.

Use `` ` `` (backtick) for inline code and code blocks in GitHub issues and pull requests, not `\`` (escaped backtick).

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `markvilar/claude-code` (uses the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
