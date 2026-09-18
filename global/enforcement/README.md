# enforcement — 하네스가 집행하는 층

모델이 우회할 수 없는 **강제 계층**(권한 규칙 + hook)의 실파일. 규칙 문서는 `global/skills/harness-engineering/SKILL.md`이고, 거기엔 "왜"만 있고 값은 전부 여기 있다.

```
claude/
  settings.fragment.json           # 공통 deny/ask/allow + PreToolUse guard 배선 → ~/.claude/settings.json에 키 단위 병합
  hooks/
    pre-tool-use-bash-guard.sh     # 인자 위치가 자유로운 위험 패턴 차단(exit 2) — rm -rf /, force push, --no-verify, pipe-to-shell
    post-tool-use-audit.sh         # 선택. 툴 호출을 날짜별 JSONL로 append(관측용). 기본 미배선
codex/
  config.fragment.toml             # approval_policy / sandbox_mode 두 키만 → ~/.codex/config.toml에 병합
```

## 설치 계약

- **전역에 설치하고, 병합만 한다.** `bootstrap.sh`가 `permissions.deny/ask/allow` 배열에 없는 항목만 추가하고, 추가한 항목을 `.dev-conventions.lock`의 `managed`에 기록한다. 기존 항목·다른 도구가 넣은 hook은 건드리지 않는다(→ 설계 §7.3).
- 전역 `settings.json`의 hook 배열에는 **외부 도구가 관리하는 래퍼**가 이미 들어 있다. 배열을 교체하지 말고 항목만 append한다.
- `{{DEV_CONVENTIONS_DIR}}`는 설치 시점에 repo 절대경로로 치환된다(`bootstrap.sh`가 자기 위치로 감지). hook 스크립트는 복사하지 않고 repo 경로를 직접 참조한다 — repo를 `git pull`하면 곧 갱신이다.
- 프로젝트 고유 allow(그 프로젝트의 스크립트명, `rm -rf dist` 같은 exact 규칙)는 여기 넣지 않는다. 프로젝트 `.claude/settings.json`으로 간다(→ 설계 §6.4).

## 이 값들의 출처 (2026-09-18 역수집)

`settings.fragment.json`은 두 곳을 합쳐 만들었다.

1. **이 PC의 `~/.claude/settings.json`** — 실제로 쓰이고 있던 deny 10 / ask 20 / allow 96. 이게 사실상의 원본이었고, 저장소로 끌어온 게 이번 역수집이다.
2. **기존 프로젝트용 템플릿**(`templates/harness/claude/settings.json`, 권한 패턴 B) — 전역에 없던 항목(`rm -rf /*`, `rm -rf ~*`, 의존성 변경 ask, `.env` 세분화)을 더했다.

**버린 것**(머신 고유 값 — 설계 §7.7):

- 세션 중 누적된 일회성 allow 60여 개 — 절대경로(`/Users/kwanghun/...`), 특정 프로젝트 이름, 특정 파일 조회, `echo "…complete"` 류. 이식되지 않는다.
  - 그중 하나에는 로컬 개발용 DB 비밀번호가 문자열로 박혀 있었다. 저장소로 가져오지 않았다.
- `model`·`theme`·`statusLine`·`tui`·`effortLevel`·플러그인 목록 — 취향·UI.
- `permissions.additionalDirectories` — 머신마다 다른 절대경로.
- `permissions.defaultMode` — 이 PC는 `auto`, 템플릿은 `default`였다. 환경마다 고르는 값으로 보고 **설치 대상에서 뺐다**. bootstrap은 이 키를 읽지도 쓰지도 않는다.

**판단이 갈린 것**(설치 전에 알고 있어야 하는 차이):

| 항목 | 이 PC 현재 | 이 파일 | 왜 |
|---|---|---|---|
| `.env` 읽기 | `Read(**/.env.*)` 한 줄로 광범위 deny | `.env.local`·`.env.*.local`·`.env.production`을 열거 | deny는 allow 예외를 못 가져서 광범위 deny면 커밋되는 `.env.example`도 못 읽는다. 단 설치는 병합만 하므로 이 PC의 기존 광범위 deny는 그대로 남는다 — 좁히려면 직접 지워야 한다 |
| 의존성 변경 | ask 없음(`Bash(pnpm:*)` allow) | `pnpm add`/`pnpm remove` ask | 설계 §5.1이 요구. **설치하면 이 PC에 없던 승인 프롬프트가 생긴다.** 실제로 귀찮으면 빼고 그 사실을 기록한다 |
| `curl`/`wget` | `Bash(curl:*)` allow | 어느 쪽에도 넣지 않음 | 이 PC는 allow, 프로젝트 템플릿은 ask였다. 어느 쪽이 모든 프로젝트에 공통이라고 볼 근거가 없어 전역에서 판정하지 않는다 |

## 기준·대조 기록

- 기준 날짜: 2026-09-09. Claude Code 권한 규칙·hook 문법은 공식 문서(`code.claude.com/docs/en/permissions`, `/hooks`)와 대조했다.
  - 규칙 평가 순서 deny → ask → allow, 첫 매치. deny는 allow 예외를 못 가진다.
  - Bash 규칙은 `Bash(git push *)`(= `Bash(git push:*)`) 형태의 **prefix 매칭**. 복합 명령(`&&`, `;`, `|`)은 서브커맨드별로 매칭되며 deny/ask는 서브셸·치환 안까지 본다.
  - `Read(.env)`처럼 bare 파일명은 어느 깊이든 매칭. `Write(...)` 경로 규칙은 무시되므로 `Edit(...)`을 쓴다.
  - hook: `matcher`는 툴 이름(`"Bash"`, `"Edit|Write"`, 정규식). **exit 2 + stderr**가 차단 사유. exit 0은 판단 없음.
- 권한 3패턴(A/B/C)과 deny 기본 목록은 hidekazu-konishi "Claude Code Harness and Environment Engineering" 패턴 B를 기반으로 조정.
- Codex 키(`approval_policy`, `sandbox_mode`, 프로필, trust 모델, 우선순위)는 OpenAI Codex 설정 문서 기준. `hooks.json`·`rules/`는 스키마를 검증하지 못해 **제외**했다.

## 설계 메모

- **`--no-verify` 금지는 hook에 있다, deny 규칙이 아니다.** prefix 규칙 `Bash(git commit --no-verify *)`는 `git commit -m x --no-verify`를 못 잡는다. 인자 위치가 자유로운 플래그는 hook의 정규식으로 강제한다. 이게 "산문 규칙을 강제 계층으로 내리는" 예시다.
- guard는 커밋 메시지 안의 `-n` 같은 오탐을 막기 위해 git 플래그 패턴만 **따옴표 내용을 비운 문자열**에 매칭한다.
- guard는 `jq` → `python3` 순으로 payload를 파싱하고, 둘 다 없으면 **fail-closed(전부 차단)**. 안전장치가 조용히 무력화되는 것보다 낫다고 봤다. 이 동작이 싫으면 해당 분기에서 `exit 0`으로 바꾼다.
- allow의 패키지 매니저 스크립트명은 `Bash(pnpm:*)`처럼 도구 단위로 넓게 잡았다. 프로젝트별 스크립트명까지 전역에 박지 않는다 — 그건 프로젝트 `.claude/settings.json`의 일이다.
- `Bash(rm:*)`는 ask다. `rm -rf dist` 같은 프로젝트 안 삭제가 잦으면 그 프로젝트의 `.claude/settings.json`에 `Bash(rm -rf dist)`처럼 **경로를 박은 exact 규칙**을 allow에 추가한다. deny `Bash(rm -rf /*)`·`Bash(rm -rf ~*)`가 먼저 평가되므로 안전.

## audit hook 배선 (선택)

전역 `settings.json`의 `hooks`에 추가. 매 툴 호출마다 실행되므로 필요할 때만.

```json
"PostToolUse": [
  {
    "matcher": "*",
    "hooks": [
      { "type": "command", "command": "<repo>/global/enforcement/claude/hooks/post-tool-use-audit.sh", "timeout": 5 }
    ]
  }
]
```

기본 경로 `~/.claude/audit/YYYY-MM-DD.jsonl`, `CLAUDE_AUDIT_DIR`로 변경. 한 줄 = `{"ts": ..., "payload": <hook 입력 전체>}`.

## 검증 방법

```sh
python3 -m json.tool claude/settings.fragment.json >/dev/null
bash -n claude/hooks/*.sh
printf '{"tool_input":{"command":"rm -rf /"}}' | bash claude/hooks/pre-tool-use-bash-guard.sh; echo $?   # 2
printf '{"tool_input":{"command":"git commit -m x --no-verify"}}' | bash claude/hooks/pre-tool-use-bash-guard.sh; echo $?   # 2
printf '{"tool_input":{"command":"pnpm test"}}'  | bash claude/hooks/pre-tool-use-bash-guard.sh; echo $?   # 0
```
