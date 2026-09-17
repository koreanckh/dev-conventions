#!/usr/bin/env bash
# PostToolUse audit — 모든 툴 호출 payload를 날짜별 JSONL로 append한다(관측/사후 디버깅용). 항상 exit 0.
# 배선은 global/enforcement/README.md의 hooks 조각 참고. 기본 경로 ~/.claude/audit, CLAUDE_AUDIT_DIR로 변경.
# 원본: dev-conventions/global/enforcement/claude/hooks (→ global/skills/harness-engineering/SKILL.md)
set -euo pipefail

log_dir="${CLAUDE_AUDIT_DIR:-$HOME/.claude/audit}"
mkdir -p "$log_dir"
log_file="$log_dir/$(date -u +%Y-%m-%d).jsonl"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
payload="$(cat)"
printf '{"ts":"%s","payload":%s}\n' "$ts" "$payload" >> "$log_file"
exit 0
