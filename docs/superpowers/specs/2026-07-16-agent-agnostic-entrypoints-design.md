# Agent-agnostic repository entrypoints

- Status: approved
- Scope: `dev-conventions` repository guidance and `/apply-conventions` output
- Last updated: 2026-07-16

## Goal

Keep shared repository guidance independent of the agent or provider in use. A project must have one canonical instruction file, while provider-specific files remain thin entrypoints that only reference the canonical guidance.

## Design

`AGENTS.md` is the canonical repository guidance. It contains the shared rules that currently live in `CLAUDE.md`, including the `dev-conventions` repository structure and rule-authoring workflow.

Provider entrypoints contain no duplicated shared rules:

- `CLAUDE.md` references `@./AGENTS.md`.
- `GEMINI.md` references `@./AGENTS.md`.
- `.agents/rules/repository.md` references `@../../AGENTS.md`.

Provider-specific instructions may remain in a provider directory only when they depend on provider-only behavior. The reason must be documented beside the instruction.

## Template and installation behavior

The shared rules snippet becomes AGENTS-oriented. `/apply-conventions` performs these steps:

1. Merge shared rules into the target project's `AGENTS.md` only.
2. Create or reconcile the thin provider entrypoints listed above.
3. Preserve unrelated content in existing entrypoint files.
4. Before replacing conflicting shared guidance or a non-thin existing entrypoint, show the difference and ask for confirmation.

The existing Claude slash-command installer remains provider-specific infrastructure. This change generalizes the repository guidance produced by the command; it does not add equivalent command installers for every agent provider.

## Documentation changes

Update `README.md`, `install/apply-conventions.md`, and rule-authoring pointers so they describe `AGENTS.md` as the single source of truth and the remaining files as provider adapters. Remove wording that instructs users to duplicate the common block into both `CLAUDE.md` and `AGENTS.md`.

## Compatibility and verification

Existing user changes in `CLAUDE.md`, `README.md`, `bootstrap.sh`, and `install/` must be preserved. Verification is documentation-focused:

- confirm all referenced template and entrypoint paths exist;
- search for stale instructions that still treat `CLAUDE.md` as the shared source;
- inspect the final diff for duplicated guidance and unrelated changes.

This repository has no build, lint, or test suite, so no package-manager verification is required.
