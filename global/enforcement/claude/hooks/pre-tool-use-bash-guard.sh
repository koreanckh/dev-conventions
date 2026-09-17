#!/usr/bin/env bash
# PreToolUse(Bash) guard — 권한 prefix 규칙으로 못 잡는 "인자 위치가 자유로운" 위험 패턴을 차단한다.
# 계약: stdin으로 hook payload(JSON)를 받고, 차단하려면 stderr에 사유를 쓰고 exit 2. exit 0은 판단 없음(정상 진행).
# 원본: dev-conventions/global/enforcement/claude/hooks (→ global/skills/harness-engineering/SKILL.md)
set -euo pipefail

payload="$(cat)"

# jq → python3 순으로 파싱. 둘 다 없으면 fail-closed(차단): 안전장치가 조용히 무력화되는 것보다 낫다.
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
elif command -v python3 >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')"
else
  echo "pre-tool-use-bash-guard: jq 또는 python3가 필요합니다 (fail-closed)" >&2
  exit 2
fi

[ -z "$cmd" ] && exit 0

# 따옴표 안 내용을 비운 버전. 커밋 메시지 속 "-n" 같은 오탐을 막기 위해 git 플래그 패턴은 이쪽에 매칭한다.
cmd_unquoted="$(printf '%s' "$cmd" | sed -E "s/\"[^\"]*\"/\"\"/g; s/'[^']*'/''/g")"

# 패턴(ERE) / 사유 / 매칭 대상(raw|unquoted)은 같은 인덱스로 짝. 프로젝트 사정에 맞게 추가/삭제한다.
# 사유는 에이전트가 읽고 우회로를 찾을 수 있게 구체적으로 쓴다.
declare -a patterns=(
  # 루트/홈 재귀 삭제 (권한 규칙 Bash(rm -rf /*)의 백스톱 — 플래그 순서가 다른 변형까지)
  'rm[[:space:]]+-[[:alpha:]]*[rR][[:alpha:]]*[[:space:]]+(/|~|\$HOME|\$\{HOME\})/?\*?([[:space:]]|$)'
  # 디스크/파일시스템 파괴
  'mkfs(\.|[[:space:]])'
  'dd[[:space:]].*of=/dev/'
  '>[[:space:]]*/dev/(sd|nvme|disk)'
  # 원격 스크립트를 셸에 바로 파이프
  '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z|da)?sh([[:space:]]|$)'
  # force push (--force-with-lease는 허용)
  'git[[:space:]]+push[^|;&]*([[:space:]]--force([[:space:]]|$)|[[:space:]]-f([[:space:]]|$)|[[:space:]]\+[[:alnum:]])'
  # pre-commit/pre-push 훅 우회 — 규칙 "--no-verify 금지"의 강제 계층
  'git[[:space:]]+(commit|push|merge)[^|;&]*[[:space:]]--no-verify([[:space:]]|$)'
  'git[[:space:]]+commit[^|;&]*[[:space:]]-n([[:space:]]|$)'
)
declare -a reasons=(
  "루트/홈 디렉터리 재귀 삭제"
  "파일시스템 생성(mkfs)"
  "dd로 디바이스 덮어쓰기"
  "블록 디바이스로 리다이렉트"
  "원격 스크립트 pipe-to-shell. 먼저 내려받아 내용을 확인한다"
  "force push (필요하면 --force-with-lease)"
  "git --no-verify: 훅 우회 금지 (규칙 위반). 훅이 실패하면 원인을 고친다"
  "git commit -n(--no-verify): 훅 우회 금지 (규칙 위반)"
)
declare -a targets=(
  raw raw raw raw raw
  unquoted unquoted unquoted
)

for i in "${!patterns[@]}"; do
  subject="$cmd"
  [ "${targets[$i]}" = "unquoted" ] && subject="$cmd_unquoted"
  if printf '%s' "$subject" | grep -Eq "${patterns[$i]}"; then
    printf 'bash-guard 차단: %s\n  명령: %s\n' "${reasons[$i]}" "$cmd" >&2
    exit 2
  fi
done

exit 0
