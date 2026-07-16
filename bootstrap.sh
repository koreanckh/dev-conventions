#!/usr/bin/env bash
set -euo pipefail

# dev-conventions bootstrap
# 이 PC에 전역 /apply-conventions 커맨드를 설치한다.
# 이 레포를 어디에 clone했든, 스크립트가 자기 위치로 레포 경로를 감지해 커맨드에 주입한다.
# → 새 PC에서 clone 후 이 스크립트만 한 번 실행하면 경로 설정이 끝난다.

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO/install/apply-conventions.md"
DEST_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/commands"
DEST="$DEST_DIR/apply-conventions.md"

if [[ ! -f "$SRC" ]]; then
  echo "error: $SRC 가 없다. dev-conventions 레포 루트에서 실행했는지 확인." >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# 감지한 레포 절대경로를 커맨드 기본값에 주입해 설치 (PC마다 경로 달라도 자동 반영)
sed "s|{{DEV_CONVENTIONS_DIR}}|$REPO|g" "$SRC" > "$DEST"

echo "설치 완료: $DEST"
echo "소스 레포:  $REPO"
echo
echo "이제 아무 프로젝트에서나 /apply-conventions 를 쓸 수 있다."
echo "(경로 오버라이드: /apply-conventions <다른-경로>  또는  DEV_CONVENTIONS_DIR 환경변수)"
