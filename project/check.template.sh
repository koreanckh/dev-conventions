#!/usr/bin/env bash
set -euo pipefail

# 프로젝트 단일 검증 진입점 — `scripts/check`로 복사하고 `chmod +x` 한 뒤, AGENTS.md의 `verify` 파라미터가 이 경로를 가리키게 한다.
#
# 계약 (dev-conventions 설계 §6.3):
#   - 인자 없이 실행한다. 종료 코드 0 = 통과.
#   - 내부 구성은 스택마다 자유다. 이름이 아니라 **진입점이 하나**인 게 목적이다.
#   - 이미 쓰는 스크립트가 있으면(`verify-all.sh`, `./gradlew check`) 새로 만들지 말고 여기서 그걸 부르거나 `verify`가 직접 가리키게 한다.
#   - 실패 메시지는 에이전트가 읽고 고칠 수 있게 구체적으로. 어느 단계가 왜 깨졌는지 남긴다.
#
# 아래는 node 프로젝트 예시다. 쓰는 스택에 맞게 단계를 갈아끼운다.

cd "$(dirname "${BASH_SOURCE[0]}")/.."

PM="${PM:-pnpm}"   # package-manager 파라미터의 값

step() {
  echo "▶ $*"
  if ! "$@"; then
    echo "✗ 실패: $*" >&2
    exit 1
  fi
}

step "$PM" lint
step "$PM" typecheck
step "$PM" test

echo "✓ check 통과"
