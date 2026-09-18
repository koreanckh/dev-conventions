#!/usr/bin/env bash
set -euo pipefail

# dev-conventions bootstrap — 이 PC(환경)에 규칙을 설치한다.
#
#   ./bootstrap.sh              설치/갱신 (멱등)
#   ./bootstrap.sh --dry-run    바뀔 내용만 출력. 아무것도 쓰지 않는다
#   ./bootstrap.sh --check      낡음 검사만. 0=최신, 1=낡음
#   ./bootstrap.sh --copy       심링크 대신 복사 (심링크를 못 쓰는 환경)
#   ./bootstrap.sh --uninstall  lock에 기록된 자기 설치분만 제거
#   ./bootstrap.sh --agent claude   한 에이전트만
#
# 이 레포를 어디에 clone했든 스크립트가 자기 위치로 레포 경로를 감지한다.
# 설치 대상 매핑은 install/targets, 실제 동작은 install/lib/dc_install.py.
# 의존성: bash · git · python3. GNU 전용 플래그를 쓰지 않는다.

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$REPO/install/lib/dc_install.py"

COMMAND=install
MODE=link
DRY=()
AGENT=()

usage() { sed -n '4,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)     COMMAND=check ;;
    --uninstall) COMMAND=uninstall ;;
    --dry-run)   DRY=(--dry-run) ;;
    --copy)      MODE=copy ;;
    --agent)     shift; AGENT=(--agent "${1:?--agent 뒤에 이름이 필요하다}") ;;
    -h|--help)   usage; exit 0 ;;
    *)           echo "error: 모르는 옵션 '$1'" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

command -v python3 >/dev/null || { echo "error: python3가 필요하다." >&2; exit 1; }
[[ -f "$HELPER" ]] || { echo "error: $HELPER 가 없다. dev-conventions 레포 루트에서 실행했는지 확인." >&2; exit 1; }

exec python3 "$HELPER" --repo "$REPO" --command "$COMMAND" --mode "$MODE" "${DRY[@]+"${DRY[@]}"}" "${AGENT[@]+"${AGENT[@]}"}"
