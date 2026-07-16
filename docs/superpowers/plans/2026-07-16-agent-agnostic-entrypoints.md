# Agent-agnostic Repository Entrypoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `AGENTS.md` the single source of repository guidance in `dev-conventions` and in every project configured by `/apply-conventions`.

**Architecture:** Shared rules live only in `AGENTS.md`. Claude, Gemini, and generic `.agents/rules` entrypoints remain short provider adapters that reference it; detailed conventions remain on-demand documents under `docs/conventions/` in target projects.

**Tech Stack:** Markdown, Git, Claude slash-command instructions

## Global Constraints

- Preserve existing uncommitted work in `CLAUDE.md`, `README.md`, `bootstrap.sh`, and `install/`.
- Do not duplicate shared rules across provider entrypoints.
- Show a diff and ask before replacing conflicting guidance in a target project.
- Keep the existing Claude-specific `/apply-conventions` bootstrap; generalizing command installation is outside scope.
- Commit and push the completed change to the current `main` branch as requested by the user.

---

### Task 1: Canonical guidance and thin provider adapters

**Files:**
- Create: `AGENTS.md`
- Modify: `CLAUDE.md`
- Create: `GEMINI.md`
- Create: `.agents/rules/repository.md`

**Interfaces:**
- Consumes: the existing repository guidance currently in `CLAUDE.md`
- Produces: one canonical `AGENTS.md` and three provider entrypoints that reference it

- [ ] **Step 1: Move shared repository guidance to `AGENTS.md`**

Use the current `CLAUDE.md` content, including the user's uncommitted `bootstrap.sh` and `/apply-conventions` additions. Change provider-specific wording so the header is `# dev-conventions repository guidance`, the dogfooding note points to `templates/AGENTS.snippet.md`, and the structure describes provider entrypoints as thin adapters.

Add these rules:

```markdown
## Provider entrypoints

- Treat `AGENTS.md` as the canonical repository guidance.
- Keep `CLAUDE.md`, `GEMINI.md`, and `.agents/rules/repository.md` as thin provider adapters that reference `AGENTS.md`; do not duplicate shared guidance in them.
- Put provider-specific behavior in its provider directory only when it cannot be expressed in the shared guidance, and document why it is provider-specific.
```

- [ ] **Step 2: Replace and create provider entrypoints**

Set the files to exactly:

```markdown
# Claude Code entrypoint

@./AGENTS.md
```

```markdown
# Gemini CLI entrypoint

@./AGENTS.md
```

```markdown
# Repository guidance

@../../AGENTS.md
```

- [ ] **Step 3: Verify entrypoint paths and deduplication**

Run:

```sh
test -f AGENTS.md
test -f CLAUDE.md
test -f GEMINI.md
test -f .agents/rules/repository.md
rg -n "@\./AGENTS\.md|@\.\./\.\./AGENTS\.md" CLAUDE.md GEMINI.md .agents/rules/repository.md
```

Expected: all `test` commands succeed; both root adapters point to `@./AGENTS.md`, and the nested adapter points to `@../../AGENTS.md`.

### Task 2: AGENTS-oriented templates and application workflow

**Files:**
- Rename: `templates/CLAUDE.snippet.md` to `templates/AGENTS.snippet.md`
- Modify: `install/apply-conventions.md`
- Modify: `.claude/commands/import-conventions.md`
- Modify: `conventions/agent-workflow.md`
- Modify: `conventions/coding-conventions.md`
- Modify: `conventions/todo-workflow.md`
- Modify: `templates/convention.template.md`

**Interfaces:**
- Consumes: `templates/AGENTS.snippet.md` as the shared-rule block
- Produces: target-project instructions that merge shared guidance once and create provider adapters safely

- [ ] **Step 1: Rename and generalize the shared snippet**

Rename the template and replace its introductory comment with:

```markdown
<!--
대상 repo의 AGENTS.md에 아래 "## 공통 규칙" 블록을 병합한다.
- always-on 항목: 경로만 두면 에이전트가 문서를 안 열 수 있으므로, 매 작업에 적용되는 소수 규칙은 여기 인라인으로 둔다.
- 포인터 항목: "언제 읽어라" 힌트를 함께 둬서 에이전트가 문서를 열 트리거를 준다.
- CLAUDE.md, GEMINI.md, .agents/rules/repository.md는 AGENTS.md를 참조하는 얇은 어댑터로 유지한다.
- 규칙이 늘면 포인터 줄만 하나씩 추가한다.
-->
```

Keep the existing `## 공통 규칙` block unchanged.

- [ ] **Step 2: Generalize `/apply-conventions` step 3**

Replace the duplicated merge instruction with:

```markdown
3. **공통 지침 + provider 진입점 구성**
   - `<SRC>/templates/AGENTS.snippet.md`의 `## 공통 규칙` 블록을 대상 `AGENTS.md`에만 병합한다. 파일이 없으면 생성하고, 같은 섹션이 있으면 중복 줄 없이 병합한다.
   - `CLAUDE.md`와 `GEMINI.md`는 `@./AGENTS.md`, `.agents/rules/repository.md`는 `@../../AGENTS.md`를 참조하는 얇은 진입점으로 구성한다.
   - 기존 진입점에 provider 전용 지침이나 다른 내용이 있으면 보존한다. 공통 규칙이 중복되어 있거나 얇은 진입점으로 바꾸려면 먼저 diff를 보여주고 확인한다.
```

Also update the principles to require `AGENTS.md` as the canonical guidance and forbid duplicated shared rules in provider entrypoints.

- [ ] **Step 3: Update all rule-authoring pointers**

Change every pointer from `templates/CLAUDE.snippet.md` to `templates/AGENTS.snippet.md`, every instruction that merges into both `CLAUDE.md` and `AGENTS.md` to merge into `AGENTS.md` only, and `.claude/commands/import-conventions.md` to read `AGENTS.md` for the authoring checklist.

- [ ] **Step 4: Verify no stale template references remain**

Run:

```sh
test -f templates/AGENTS.snippet.md
test ! -e templates/CLAUDE.snippet.md
! rg -n "templates/CLAUDE\.snippet\.md|CLAUDE\.md/AGENTS\.md|CLAUDE\.md\(및 AGENTS\.md\)" . --glob '!docs/superpowers/**'
```

Expected: the new template exists, the old path does not, and the stale-reference search returns no matches.

### Task 3: User-facing documentation, final verification, commit, and push

**Files:**
- Modify: `README.md`
- Verify: all changed files

**Interfaces:**
- Consumes: the canonical guidance and installer behavior from Tasks 1 and 2
- Produces: documented setup plus a clean, pushed Git commit

- [ ] **Step 1: Document the canonical-plus-adapter layout**

Update the structure tree to list `AGENTS.md`, the three provider adapters, and `templates/AGENTS.snippet.md`. Explain that `/apply-conventions` merges common rules only into `AGENTS.md`, then creates or preserves thin provider entrypoints. Replace remaining Claude-centric manual-application, rule-authoring, and portability wording.

- [ ] **Step 2: Run documentation verification**

Run:

```sh
git diff --check
rg -n "AGENTS\.md|GEMINI\.md|\.agents/rules/repository\.md|AGENTS\.snippet\.md" AGENTS.md README.md install conventions templates .claude/commands
! rg -n "templates/CLAUDE\.snippet\.md|CLAUDE\.md/AGENTS\.md|CLAUDE\.md\(및 AGENTS\.md\)" . --glob '!docs/superpowers/**'
git status --short
```

Expected: `git diff --check` succeeds, canonical/adaptor references are present, stale-reference search is empty, and status contains only this feature plus the user's related pre-existing `/apply-conventions` work.

- [ ] **Step 3: Inspect the complete diff**

Run `git diff --stat && git diff -- . ':(exclude)docs/superpowers/plans/2026-07-16-agent-agnostic-entrypoints.md'`, then inspect the plan separately. Confirm there are no secrets, generated files, or unrelated edits.

- [ ] **Step 4: Commit the coherent change**

Run:

```sh
git add AGENTS.md CLAUDE.md GEMINI.md .agents/rules/repository.md .claude/commands/import-conventions.md README.md bootstrap.sh conventions docs install templates
git commit -m "docs(agents): generalize repository guidance"
```

Expected: one commit is created on `main`, including the related pre-existing bootstrap/application work and the approved design and plan.

- [ ] **Step 5: Push the current branch**

Run:

```sh
git push origin main
```

Expected: `origin/main` advances to the new commit.
