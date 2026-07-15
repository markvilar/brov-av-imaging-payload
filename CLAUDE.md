# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository covers the **camera selection, design, and documentation** for a
custom **imaging payload for an underwater robot** — an Allied Vision camera on a
MIPI/Jetson host, LED strobes, and the triggering electronics (capacitor
carriers, sync circuitry) that fire the strobes while the shutter is open, for
low-light photogrammetry stills at ~1 fps and 100–300 m depth.

`CONTEXT.md` at the repo root is the source of truth for *what* the payload is
and *why* — read it first for the system overview, operating envelope, and open
trade studies.

## Repository layout

- `CONTEXT.md` — domain context: purpose, subsystems, constraints, open questions.
- `requirements/` — payload requirements, interface specs, operating envelope.
- `trade-studies/` — option comparisons and selection rationale.
- `decisions/` — design-decision records (ADRs).
- `vendors/` — third-party vendor documentation (datasheets, manuals), by vendor.
- `tests/` — bench, pressure, sync-timing, and image-quality reports.

The record is organized primarily by document *type*; the subsystem axis is
carried by `area:` issue labels rather than directories, since the hardware
decomposition is still fluid. Out of scope: the Jetson-side capture/control
firmware and software (developed elsewhere).

## MCP Servers

**context7** is configured as a project MCP server in `.mcp.json`. Use it to fetch up-to-date documentation when implementing features that involve libraries or frameworks. Always resolve the library ID first with `resolve-library-id`, then query with `query-docs`.

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

Work is orchestrated via GitHub Projects and GitHub Issues on `markvilar/brov-av-imaging-payload` (uses the `gh` CLI). Issues hold the workflow and discussion; durable outcomes are distilled into the repo (`decisions/`, `trade-studies/`, `tests/`). Cross-link both ways: cite the issue number in the resulting artifact, and close the issue with a link to the committed artifact.

### Issue labels

Label vocabulary (prefix-grouped):

- `type:` — kind of work: `trade-study`, `decision`, `design`, `procurement`, `test`, `docs`, `question`.
- `area:` — subsystem: `camera`, `lighting`, `electronics`, `mechanical`, `sync`, `power`. Preferred over directories for the subsystem axis, since the decomposition is still fluid.
- `priority:` — `high`, `medium`, `low`.
- Status flags: `blocked`, `needs-info`. Day-to-day status lives in the Project board columns; these labels flag states that matter outside that flow.

### Domain docs

Single-context layout: one `CONTEXT.md` at the repo root, with design-decision records (ADRs) under `decisions/`.
