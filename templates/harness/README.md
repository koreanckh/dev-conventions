# harness 템플릿

에이전트를 감싸는 **강제 계층**(권한 규칙 + hook)의 실파일. 규칙 문서는 `conventions/harness-engineering.md`. 문서에는 "왜"만 있고 값은 전부 여기.

```
claude/
  settings.json                    # 패턴 B(curated allow-list) + PreToolUse guard 배선 → 대상 repo .claude/settings.json
  hooks/
    pre-tool-use-bash-guard.sh     # 인자 위치가 자유로운 위험 패턴 차단(exit 2) — rm -rf /, force push, --no-verify, pipe-to-shell
    post-tool-use-audit.sh         # 선택. 툴 호출을 날짜별 JSONL로 append(관측용). 기본 미배선
codex/
  config.toml                      # approval_policy / sandbox_mode 두 키만. 프로필은 주석 예시
```

## 출처·기준

- 기준 날짜: 2026-09-09. Claude Code 권한 규칙·hook 문법은 공식 문서(`code.claude.com/docs/en/permissions`, `/hooks`)와 대조했다.
  - 규칙 평가 순서 deny → ask → allow, 첫 매치. deny는 allow 예외를 못 가진다.
  - Bash 규칙은 `Bash(git push *)`(= `Bash(git push:*)`) 형태의 **prefix 매칭**. 복합 명령(`&&`, `;`, `|`)은 서브커맨드별로 매칭되며 deny/ask는 서브셸·치환 안까지 본다.
  - `Read(.env)`처럼 bare 파일명은 어느 깊이든 매칭. `Write(...)` 경로 규칙은 무시되므로 `Edit(...)`을 쓴다.
  - hook: `matcher`는 툴 이름(`"Bash"`, `"Edit|Write"`, 정규식). **exit 2 + stderr**가 차단 사유. exit 0은 판단 없음.
- 권한 3패턴(A/B/C)과 deny 기본 목록은 hidekazu-konishi "Claude Code Harness and Environment Engineering" 패턴 B를 기반으로 pnpm 스택에 맞춰 조정.
- Codex 키(`approval_policy`, `sandbox_mode`, 프로필, trust 모델, 우선순위)는 OpenAI Codex 설정 문서 기준. `hooks.json`·`rules/`는 스키마를 검증하지 못해 **템플릿에서 제외**했다.

## 설계 메모

- **`--no-verify` 금지는 hook에 있다, deny 규칙이 아니다.** prefix 규칙 `Bash(git commit --no-verify *)`는 `git commit -m x --no-verify`를 못 잡는다. 인자 위치가 자유로운 플래그는 hook의 정규식으로 강제한다. 이게 "산문 규칙을 강제 계층으로 내리는" 예시다.
- guard는 커밋 메시지 안의 `-n` 같은 오탐을 막기 위해 git 플래그 패턴만 **따옴표 내용을 비운 문자열**에 매칭한다.
- guard는 `jq` → `python3` 순으로 payload를 파싱하고, 둘 다 없으면 **fail-closed(전부 차단)**. 안전장치가 조용히 무력화되는 것보다 낫다고 봤다. 이 동작이 싫으면 해당 분기에서 `exit 0`으로 바꾼다.
- `.env` deny 목록은 "gitignore되는 env 파일"과 맞춘다는 원칙. `.env.example`처럼 커밋되는 파일은 읽을 수 있어야 하므로 `Read(.env.*)` 같은 광범위 deny는 피했다. 프로젝트 `.gitignore`와 대조해 조정.
- allow의 pnpm 스크립트명(`lint`/`test`/`build`/`typecheck`/`format`)은 대상 `package.json`에 맞춰 바꾼다. 없는 스크립트를 allow해도 해는 없지만 있는 스크립트를 빠뜨리면 매번 묻는다.
- `Bash(rm -rf *)`는 ask다. `rm -rf dist` 같은 프로젝트 안 삭제가 잦으면 `Bash(rm -rf dist)`처럼 **경로를 박은 exact 규칙**을 allow에 추가한다. deny `Bash(rm -rf /*)`·`Bash(rm -rf ~*)`가 먼저 평가되므로 안전.

## audit hook 배선 (선택)

`settings.json`의 `hooks`에 추가. 매 툴 호출마다 실행되므로 필요할 때만.

```json
"PostToolUse": [
  {
    "matcher": "*",
    "hooks": [
      { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/post-tool-use-audit.sh", "timeout": 5 }
    ]
  }
]
```

기본 경로 `~/.claude/audit/YYYY-MM-DD.jsonl`, `CLAUDE_AUDIT_DIR`로 변경. 한 줄 = `{"ts": ..., "payload": <hook 입력 전체>}`.

## 검증 방법

```sh
jq . claude/settings.json
bash -n claude/hooks/*.sh
printf '{"tool_input":{"command":"rm -rf /"}}' | bash claude/hooks/pre-tool-use-bash-guard.sh; echo $?   # 2
printf '{"tool_input":{"command":"pnpm test"}}'  | bash claude/hooks/pre-tool-use-bash-guard.sh; echo $?   # 0
```
