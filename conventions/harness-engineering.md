# 하네스 설정

> 원본(SSOT): dev-conventions. 대상 repo로 복사할 땐 이 줄을 `> 출처: dev-conventions · 복사 YYYY-MM-DD`로 바꿔 남긴다(복사본이 낡았는지 판단용).

`Agent = Model + Harness`. 모델은 못 바꾸니까, 모델을 감싸는 것 — 지침 파일·권한·hook·skill·서브에이전트·검증 루프 — 을 어디에 어떻게 두는가가 결과를 결정한다. 이 문서는 그 **배치 규칙**이다. 에이전트가 *어떻게 일하는가*(절차)는 [에이전트 작업 규칙](agent-workflow.md), 상태를 세션 밖에 남기는 법은 [작업 인계](handoff.md)·[TODO 관리](todo-workflow.md)에 이미 있으므로 여기선 참조만 한다. 프로젝트마다 바꿀 값: allow-list의 스크립트명, 보호할 env 파일 경로 — 전부 `templates/harness/`.

## 원칙

### 규칙은 강제력이 가장 높은 계층에 둔다

```
지침       AGENTS.md / CLAUDE.md          권고. 모델이 잊거나 무시할 수 있다
프로세스 안 permissions · hook · lint · test  Claude Code/Codex가 강제. 모델이 우회할 수 없다
프로세스 밖 컨테이너 · OS 사용자 · 네트워크    환경이 강제. 프로세스가 뚫려도 막힌다
```

- **`AGENTS.md`엔 "그 줄이 있다는 걸 잊어도 지킬 문장"만.** 잊으면 안 지킬 규칙이면 아래 계층으로 내린다.
- **"매번 X하면 Y해라" / "절대 하지 마"는 지침이 아니다.** hook(`PreToolUse` exit 2)이나 `permissions.deny`로. 프롬프트 규칙은 압박 상황에서 깨진다.
- 같은 규칙을 여러 계층에 두는 건 모순이 아니라 **백스톱**이다. `.env`를 지침(만지지 마) + deny(`Read(.env)`) + hook + 컨테이너 미마운트로 겹쳐 두는 게 정석.
- 권한 규칙과 hook은 **모델이 아니라 하네스가** 집행한다. `CLAUDE.md`에 뭘 쓰든 허용 범위는 바뀌지 않는다.

### 지침 파일은 목차다

- `AGENTS.md`는 **~100줄 목차, 200줄 상한.** 백과사전이 아니다. 오너를 두고 코드처럼 리뷰한다.
- 30줄 넘는 절차(배포·리뷰 체크리스트)는 skill로, 특정 경로에만 해당하는 제약은 `rules/`에 `paths:`로, 세부 설명은 `docs/`로. 지침 파일엔 포인터 + "언제 읽어라" 힌트만 → 이 repo의 [`templates/AGENTS.snippet.md`](../templates/AGENTS.snippet.md)가 그 형태.
- 항상 로드되는 것은 컨텍스트 비용이 높다. **매 작업에 적용되는 소수 규칙만 인라인**, 나머지는 on-demand.

### 무엇을 어디에 (레이어 선택표)

| 넣을 것 | 위치 | 왜 |
|---|---|---|
| 빌드/테스트 명령, 디렉터리 구조, 코딩 컨벤션 요약 | 루트 지침 파일 | 매 작업에 필요. 압축 후에도 다시 로드됨 |
| 특정 디렉터리에서만 유효한 컨벤션 | 하위 디렉터리 지침 파일 | 그 경로에 들어갈 때만 로드 |
| 경로에 묶인 하드 제약(예: `migrations/` 수정 규칙) | `.claude/rules/*.md` + `paths:` | 관련 파일을 만질 때만 비용 지불 |
| 절차·체크리스트(배포, 릴리스, 리뷰) | `.claude/skills/<name>/SKILL.md` | 호출 시에만 본문 로드. 이름·설명만 상시 |
| 격리가 필요한 탐색·분석(코드베이스 검색, 로그 분석) | `.claude/agents/*.md` 서브에이전트 | 별도 컨텍스트. 요약만 돌아옴 |
| "매번/절대" 류 결정론적 규칙, lint·포맷 자동 실행 | `hooks` (settings.json) | 코드가 집행. 모델 판단 불개입 |
| 위험 명령·보호 경로·승인 필요 작업 | `permissions.deny/ask/allow` | 하네스가 집행. 가장 싸고 확실 |
| 외부 시스템 접근(이슈 트래커, 브라우저, DB) | `.mcp.json` + 툴별 allow/deny | 툴 단위 스코프 제어 |
| 아키텍처 경계·의존 방향 | **커스텀 lint / 구조 테스트** | 문서 대신 기계 강제. 에러 메시지에 수정법을 담아 에이전트 교육 자료로 |

### 생성자와 평가자를 분리한다

- 에이전트의 가장 흔한 실패: **코드 쓰고 → 자기 코드 다시 읽고 → "괜찮아 보임" → 종료. 실제 테스트 없음.** 자기평가는 항상 낙관적이다.
- 검증은 자기 코드 재독이 아니라 **스펙·테스트·실행 결과**에 대해 한다. 가능하면 사용자처럼(E2E, 브라우저 자동화).
- 테스트는 **지우거나 약화시켜 통과시키지 않는다**(test ratchet). 실패하면 원인을 고친다.
- 리뷰가 중요한 변경은 생성한 세션이 아닌 **별도 평가자**(리뷰 서브에이전트, 다른 모델)에 맡긴다. 리뷰 강도는 위험에 비례 → [에이전트 작업 규칙](agent-workflow.md).

### 상태는 컨텍스트 밖에 둔다

- 에이전트는 기억이 없다. 진행 상태·결정·실패한 접근은 **파일**에 → [작업 인계](handoff.md). 완료 조건은 **미리 적어둔 목록**에 → [TODO 관리](todo-workflow.md).
- 긴 작업은 compaction보다 **구조화된 handoff + 깨끗한 리셋**이 낫다. 컨텍스트 한계가 가까워지면 조급하게 마무리하는 경향(context anxiety)이 있다.
- 세션 시작 의식: handoff 읽기 → 미완 항목 1개 선택 → **새 작업 전에 현재 상태 검증** → 작업. 한 번에 하나씩.

### 최소로 시작, 실패한 뒤에 추가

- hook 50개짜리 하네스는 유지가 안 된다. **실제로 실패가 발생한 규칙만** 추가한다.
- hook이 액션의 80% 이상을 막으면 규칙이 비현실적인 것이다. 우회 습관이 생기기 전에 고친다.
- 모델이 좋아지면 구성요소를 **하나씩 빼보며** 뭐가 실제로 load-bearing인지 확인한다. 하네스는 모델의 약점을 메우는 것이고, 약점은 줄어든다.

## 셋업 / 값

값은 전부 [`templates/harness/`](../templates/harness/) 실파일. 여기선 무엇을/왜만.

### 권한 — 3패턴과 이행 기준

| 패턴 | 하네스 | 환경 | 승인 빈도 | 용도 |
|---|---|---|---|---|
| **A. approval-first** | 무거운 deny/ask (`Bash(*)`·`Edit(**)`까지 ask) | 없음 | 매 액션 | 프로덕션 repo, 처음 붙이는 프로젝트 |
| **B. curated allow-list** ← 기본값 | deny/ask/allow 균형 | (선택) OS 사용자 분리 | 파괴적 작업만 | 일상 개발 |
| **C. sandboxed full-auto** | `bypassPermissions` | **컨테이너 + non-root + 네트워크 필터 필수** | 거의 없음 | 야간 배치, 대규모 리팩터 |

- 기본은 **B**. `templates/harness/claude/settings.json`이 B다.
  - deny: 루트/홈 삭제, `sudo`, `mkfs`, gitignore되는 env 파일과 `~/.ssh`·`~/.aws` 읽기.
  - ask: `rm -rf *`, `git push`, `git reset --hard`, `git clean`, 의존성 추가/삭제, `curl`/`wget`(외부 통신).
  - allow: 프로젝트 스크립트(`pnpm lint/test/build/typecheck/format`), `git status/diff/log/add/commit`.
- **A → B 이행 기준**: 한 주 승인 프롬프트의 80%가 같은 5개 작업이면, 그 5개를 allow에 이름 박아 넣는다.
- **B → C 이행 기준**: 셋 다 만족할 때만 — (1) 컨테이너 등 프로세스 밖 경계가 있다 (2) audit hook이 JSONL을 영속 저장소로 보낸다 (3) 롤백 전략이 사전 정의돼 있다. C는 프로세스 안 게이트를 끄는 대신 아래 계층이 막는 구조라서, 컨테이너 밖 C는 패턴이 아니라 사고다.
- 평가 순서는 **deny → ask → allow, 첫 매치.** deny는 allow 예외를 못 가진다(`Bash(aws *)` deny면 `Bash(aws s3 ls)` allow도 무효). 광범위 deny는 신중히.
- 인자 위치가 자유로운 플래그(`--no-verify`, `--force`)는 prefix 규칙으로 못 잡는다 → hook.

### Hook — 이벤트별 용도

| 이벤트 | 용도 | 차단 |
|---|---|---|
| `SessionStart` | handoff·TODO 상태 주입, 세션 ID 로깅 | 불가 |
| `UserPromptSubmit` | 의도 분류, 계획 힌트 주입 | exit 2 |
| `PreToolUse` (`Bash`) | 위험 명령 정규식 차단 — **`templates/harness/claude/hooks/pre-tool-use-bash-guard.sh`** | exit 2 |
| `PreToolUse` (`Edit\|Write`) | 보호 경로·워크트리/plan 준비 상태 검사 | exit 2 |
| `PostToolUse` (`Edit\|Write`) | 변경 파일 lint/format 자동 실행, 변경 저널 | 불가(결과 주석만) |
| `PostToolUse` (`*`) | JSONL audit — `post-tool-use-audit.sh`(선택) | 불가 |
| `Stop` | "정말 끝났나" 검증 스크립트, handoff 갱신 강제 | exit 2 = 종료 거부 |

- **exit 2만 차단한다. exit 0은 로깅.** 로그만 남기고 exit 0인 "안전장치"는 안전장치가 아니다.
- 차단 사유는 stderr에 **에이전트가 읽고 우회로를 찾을 수 있게** 구체적으로. "금지"만 쓰면 다른 변형으로 재시도한다.
- hook 스크립트는 `${CLAUDE_PROJECT_DIR}/.claude/hooks/`에 두고 커밋한다. 개인용은 `~/.claude/settings.json`.
- 배치 원칙: **빠른 검사는 커밋 전**(lint, 경량 guard), **무거운 검사는 통합 후**(mutation testing, 상세 리뷰 → CI), **상시 모니터링**(dead code, 드리프트 → 스케줄된 janitor 에이전트).

### 툴별 파일 매핑

벤더들이 서로의 파일을 읽기 시작해서(Copilot이 `CLAUDE.md`·`.claude/rules/`·`.claude/skills/`를, Cursor가 `.claude/agents/`를) 공식 표준보다 이 상호 호환이 실질적 이식성을 만든다. `AGENTS.md`를 SSOT로 두고 provider 파일은 얇은 어댑터로 — 이 repo의 [Provider entrypoints](../AGENTS.md) 규칙 그대로.

| 기능 | Claude Code | Codex | 커밋 |
|---|---|---|---|
| 저장소 지침 | `CLAUDE.md` → `AGENTS.md` 참조 | `AGENTS.md` (root→cwd 순 concat, 하위 `AGENTS.override.md`면 부모 대체, 합산 32 KiB 상한) | ✅ |
| 권한·hook | `.claude/settings.json` | `.codex/config.toml`(`approval_policy`, `sandbox_mode`) + `.codex/hooks.json` | ✅ |
| 개인 오버라이드 | `.claude/settings.local.json`, `~/.claude/settings.json` | `~/.codex/config.toml`, `--profile` | ❌ |
| 스코프 규칙 | `.claude/rules/*.md` | `.codex/rules/*.toml` | ✅ |
| skill | `.claude/skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` | ✅ |
| 서브에이전트 | `.claude/agents/*.md` | `.codex/agents/` | ✅ |
| MCP | `.mcp.json` | `.codex/config.toml` 안 | ✅ (토큰은 env로) |

- Codex는 `.codex/` 안의 것을 **프로젝트를 명시적으로 trust한 뒤에만** 로드한다. 악성 repo clone이 승인 정책을 몰래 바꿀 수 없게 하는 경계. 새 PC에서 hook이 안 돌면 trust부터 확인.
- 우선순위(Codex): CLI 플래그 > `--profile` > `.codex/config.toml` > `~/.codex/config.toml` > `/etc/codex/config.toml` > 기본값.

## 주의 / 알려진 불일치

- **`--dangerously-skip-permissions` / `bypassPermissions`를 홈 디렉터리 자격증명(`~/.ssh`, `~/.aws`, 토큰)이 닿는 호스트에서 켜지 않는다.** 컨테이너 안에서만. 프로덕션 repo에서 "이번 한 번만"도 금지.
- `Write(경로)` 규칙은 Claude Code가 무시한다(경고만). 파일 쓰기 제한은 `Edit(경로)`로.
- `Bash(command:...)`처럼 인자 필드를 직접 제약하는 규칙은 복합 명령으로 우회 가능해서 무시된다. `Bash(rm *)` 형태로.
- 권한 규칙 표기는 블로그마다 다르다(`:*` vs ` *`, `tool == "Edit"` 같은 비공식 matcher). 공식: `Bash(git push *)`(`:*`와 동등), hook `matcher`는 툴 이름/정규식. `templates/harness/README.md`에 대조 기록.
- Codex `hooks.json`·`rules/` 스키마는 이 문서 기준일(2026-09-09)에 검증하지 못했다. 템플릿엔 `config.toml`만 있고, hook은 Claude Code 쪽만 제공한다.
- auto mode(분류기가 액션을 심사)는 A와 B 사이의 중간 옵션이다. 분류기는 보수적으로 튜닝돼 있어(FP 0.4%, FN 17%) `--dangerously-skip-permissions` 대비 개선이지만 사람 리뷰의 대체는 아니다. 쓸 땐 기본 차단 규칙을 **처음부터 쓰지 말고 baseline을 편집**한다.

## 이 규칙 적용하기

1. 이 문서를 대상 repo `docs/conventions/harness-engineering.md`로 복사하고 상단 출처 줄을 복사일로 채운다.
2. `templates/harness/claude/settings.json` → 대상 repo `.claude/settings.json`, `templates/harness/claude/hooks/` → `.claude/hooks/`. 이미 `settings.json`이 있으면 `permissions`·`hooks` 키를 병합한다(덮어쓰지 않는다).
   ```sh
   chmod +x .claude/hooks/*.sh
   echo ".claude/settings.local.json" >> .gitignore
   ```
3. allow의 pnpm 스크립트명을 대상 `package.json`에 맞추고, deny의 env 파일 목록을 대상 `.gitignore`와 대조한다. 자주 쓰는 프로젝트 안 삭제(`rm -rf dist`)는 exact 규칙으로 allow에 추가.
4. Codex를 쓰면 `templates/harness/codex/config.toml` → `.codex/config.toml`. 프로젝트 trust 1회.
5. guard가 동작하는지 확인:
   ```sh
   printf '{"tool_input":{"command":"git commit -m x --no-verify"}}' | bash .claude/hooks/pre-tool-use-bash-guard.sh; echo $?   # 2
   ```
6. `AGENTS.md`의 `## 공통 규칙`에 포인터 한 줄 추가(전체 블록은 `templates/AGENTS.snippet.md`):
   ```markdown
   - .claude/·.codex/·hooks·권한·skills·서브에이전트를 만들거나 바꿀 때, 또는 AGENTS.md에 "매번/절대" 류 규칙을 추가하려 할 때: docs/conventions/harness-engineering.md
   ```
