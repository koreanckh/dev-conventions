# Personal Engineering System — 설계 v2

- Status: Draft v2 (2026-09-18) · v1(`2026-09-17-engineering-system-v1.md`)을 대체
- 구현 저장소: 기존 `dev-conventions`를 그대로 쓴다. 새 저장소를 만들지 않고 이름도 바꾸지 않는다.
- 적용 범위: 본인이 쓰는 **모든 개발 환경**(PC·OS·에이전트)과 모든 프로젝트
- 이 문서는 설계만 다룬다. 적용은 §11 단계대로, 각 단계 검증을 통과한 뒤 다음으로 넘어간다.

---

## 0. 한 줄 요약

**규칙은 환경에 설치하고, 프로젝트에는 값과 사실만 둔다.** 원본은 `dev-conventions` 하나이고, 환경마다 `bootstrap.sh` 한 번으로 설치한다. 프로젝트는 전역 설치가 없는 환경에서도 최소한으로 동작해야 한다.

---

## 1. 현재 상태 (2026-09-18 측정)

설계 근거가 되는 관찰이다. 추측이 아니라 실측값만 적는다.

### 1.1 복사 기반 배포가 깨져 있다

`/apply-conventions`는 규칙 문서를 대상 repo `docs/conventions/`로 복사한다. 원본과 복사본의 차이(출처 줄 제외):

| 문서 | nowhere (복사 07-29) | bus (08-01) | mulzipsa (07-23) | supermarkit |
|---|---|---|---|---|
| todo-workflow.md | 60줄 | 60줄 | 60줄 | 미적용 |
| coding-conventions.md | 8줄 | 7줄 | 25줄 | 미적용 |
| agent-workflow.md | 9줄 | 9줄 | 9줄 | 미적용 |
| harness-engineering.md | 없음 | 없음 | 없음 | 없음 |

- 드리프트가 프로젝트 간 **균일**하다 → 프로젝트가 변형한 게 아니라 원본이 앞서 나가고 복사본이 안 따라온 것.
- 가장 최근 규칙(`harness-engineering.md`)은 **0개 프로젝트**에 도달했다.
- 드리프트 표면적 = 프로젝트 수 × 문서 수. 규칙이 늘수록 나빠지는 구조다.

### 1.2 전역은 이미 두껍지만 원본이 저장소 밖에 있다

| 위치 | 상태 |
|---|---|
| `~/.claude/settings.json` | 35KB · allow 96 / deny 10 / ask 20 · hook 12개 이벤트. **dev-conventions에 없음 → 이 PC가 사실상 원본** |
| `~/.claude/CLAUDE.md` | 없음 |
| `~/.claude/skills/` | 3개(computer-use, orca-cli, orchestration). dev-conventions 유래 0개 |
| `~/.codex/AGENTS.md` | 45줄. lightweight mode 정책 있음 |
| `~/.gemini/GEMINI.md` | 존재 |

- 같은 사람의 정책(lightweight mode)이 Codex에만 있고 Claude Code에는 없다 → **에이전트 간 비대칭**.
- 전역 hook은 모든 이벤트에 동일한 래퍼 명령이 등록돼 있다 → 외부 도구가 관리하는 구역으로 본다. **덮어쓰기 금지.**
- 이 PC가 고장 나면 allow 96개는 복구할 수 없다.

### 1.3 프로젝트 쪽

- 검증 진입점이 제각각이다: `verify-all.sh`(mulzipsa), `check-node-version.mjs`(nowhere), `dev.mjs`(bus). 공통 `scripts/check`는 **0개**.
- 스택: node ~10개, JVM 2개(AutoMornitoring, hmm_mola_back). `packageManager: pnpm` 고정이 없는 node 프로젝트 2개(dark-circles, law) → "pnpm 통일"은 이미 전역 참이 아니다.
- nowhere는 자체 규칙 3개를 자생시켰다(`external-request-discipline`, `refactoring-principles`, `map-module`). 승격 심사를 받은 적 없다.
- `inbox/` 마지막 처리: 2026-07-13.

---

## 2. 목표 / 비목표

### 목표

1. 규칙 본문의 복사본을 프로젝트에서 **0개**로 만든다(드리프트 표면적 제거).
2. 새 환경은 `clone + bootstrap 1회`로 같은 상태가 된다.
3. 쓰는 에이전트 전부(Claude Code·Codex·Gemini CLI)에 **같은 규칙**이 적용된다.
4. 전역 설치가 없는 환경(회사 PC, 클라우드 세션, 협업자)에서도 프로젝트는 최소 기능으로 동작한다.
5. 강제가 필요한 규칙은 지침이 아니라 hook·permissions·스크립트로 집행한다.
6. 프로젝트에는 그 프로젝트에 대한 값·사실·결정만 남는다.
7. 기존 7개 규칙의 본문(검증된 지식)은 보존한다.

### 비목표

- 분야별 Skill 목차를 미리 만드는 것(v1 §6). **실패가 관찰된 뒤에만** 추가한다.
- Skill과 Convention을 디렉터리로 나누는 것. 한 문서 안의 섹션으로 충분하다.
- 에이전트 이름을 본문에서 지우는 것. 도구별 사실(권한 문법, 파일 위치)은 값어치 있는 지식이다.
- 검색/RAG 계층. skill의 `description`이 인덱스다.
- 설치 프로파일(회사용/개인용 분기). 필요가 관찰되면 추가한다.
- LLM이 전역 규칙을 직접 수정하는 것.

---

## 3. 구조: 세 칸

```
┌─ 환경(전역) ─────────────────────────────────────────────┐
│ 규칙   나는 어떻게 일하는가        원본: dev-conventions/global/ │
│        └ 강제력별 3층: enforcement / always-on / skills        │
└──────────────────────────────────────────────────────────┘
┌─ 프로젝트(repo에 커밋) ───────────────────────────────────┐
│ 파라미터  전역 규칙이 요구하는 이 프로젝트의 값   AGENTS.md      │
│ 사실     목표 · 구조 · 결정 · 운영 · 진행 상태   docs/, scripts/ │
└──────────────────────────────────────────────────────────┘
```

| 칸 | 질문 | 수명 | 바뀌는 계기 |
|---|---|---|---|
| 규칙 | 어떻게 일하는가 | 수년 | 실패 관찰 → 승격 심사 |
| 파라미터 | 이 프로젝트에서 그 규칙의 값은 | 프로젝트 수명 | 스택·도구 변경 |
| 사실 | 이 프로젝트는 무엇이고 왜 이렇게 됐나 | 프로젝트 수명(진행 상태는 며칠) | 개발 그 자체 |

**규칙과 파라미터의 계약:** 전역 규칙은 프로젝트마다 달라지는 값을 본문에 적지 않고 **파라미터 이름으로 참조**한다. "pnpm을 쓴다"가 아니라 "`package-manager` 파라미터의 도구를 쓴다". 이 계약 덕분에 전역과 프로젝트가 같은 주제로 충돌할 일이 구조적으로 없다(v1 §4.6의 5단 우선순위표를 대체한다).

---

## 4. 배치 판정 절차

새 내용이 생기면 이 순서로 한 번만 판정한다. 판정이 안 되면 쪼갠다.

```
Q1. 다른 프로젝트에서도 그대로 참인가?
    ├─ 아니오 ──────────────────────────────► 프로젝트 (Q3)
    └─ 예 ──► 프로젝트마다 달라지는 값이 섞여 있나?
              ├─ 예 → 규칙과 값으로 쪼갠다. 규칙은 Q2, 값은 Q3
              └─ 아니오 → Q2

Q2. (전역) 어떤 강제력이 필요한가?
    ├─ 어기면 사고다(파괴·유출·검증 우회)              → enforcement
    ├─ 매 작업에 적용되고, 잊으면 안 지켜진다            → always-on  (예산 내일 때만)
    └─ 특정 상황에서만 필요하다 / 30줄이 넘는 절차다      → skill

Q3. (프로젝트) 무엇인가?
    ├─ 전역 규칙이 이름으로 참조하는 값                  → 파라미터 (AGENTS.md)
    ├─ 왜 이렇게 됐는가                               → docs/decisions/
    ├─ 지금 어떻게 생겼는가 / 어떻게 운영하는가           → README, docs/
    ├─ 진행 중인 작업의 상태                           → handoff · todo (병합 시 삭제)
    └─ 실행되는 것                                   → scripts/, 실제 config 파일
```

**채택 기준(모든 칸 공통):** *이 문서가 없으면 에이전트가 다르게 행동하는가?* 아니면 쓰지 않는다. 모델이 이미 아는 일반론은 토큰만 쓴다.

**같은 규칙을 여러 층에 두는 것은 허용한다.** `.env` 보호를 always-on(만지지 마) + deny + hook에 겹쳐 두는 건 중복이 아니라 백스톱이다(`harness-engineering.md` 원칙 유지).

---

## 5. 전역 계층 — 강제력 3층

`harness-engineering.md`의 "지침 < hook/권한 < 환경"을 전역에 그대로 적용한다.

| 층 | 집행자 | 로드 시점 | 넣는 것 |
|---|---|---|---|
| enforcement | 하네스(모델 우회 불가) | 항상 | deny/ask/allow, guard hook |
| always-on | 모델(잊을 수 있음) | 항상 | 매 작업 규칙. **15줄 예산** |
| skills | 모델(호출해야 로드) | 상황별 | 규칙 본문·절차 |

### 5.1 enforcement

- 원본: `global/enforcement/<agent>/`. 기존 `templates/harness/`를 옮긴다.
- **먼저 역수집한다.** 현재 `~/.claude/settings.json`에서 이식 가능한 부분(공통 deny/ask/allow)을 추출해 원본에 넣는다. 머신 고유 키(§7.7)는 제외한다.
- 전역에는 **모든 프로젝트에 공통인 것만**: 파괴 명령 deny, 자격증명 경로 deny, push/reset/의존성 변경 ask, `git status/diff/log` allow.
- 프로젝트 고유 allow(그 프로젝트의 스크립트명)는 전역에 넣지 않는다 → 프로젝트 `.claude/settings.json`(§6.4).
- 설치는 **병합만** 한다. 기존 항목·다른 도구의 hook은 건드리지 않는다(§7.3).

### 5.2 always-on

- 원본: `global/always-on.md` **한 파일**. 에이전트 무관 문장으로 쓴다.
- 예산 15줄. 넘으면 skill로 내리거나 enforcement로 올린다. 여기에 남는 건 "잊으면 안 지켜지는데 코드로 강제할 수도 없는 것"뿐이어야 한다.
- 프로젝트마다 달라지는 값은 금지. 파라미터 이름으로만 참조한다.

초안(현재 `AGENTS.snippet.md`의 always-on 블록 + `~/.codex/AGENTS.md`의 정책을 합쳐 재작성):

```markdown
# 개인 전역 규칙 (dev-conventions · always-on)

- 프로젝트 AGENTS.md의 `프로젝트 파라미터`와 명시 규칙이 이 문서보다 우선한다. 필요한 파라미터가 없으면 추측하지 말고 저장소에서 확인하거나 묻는다.
- 기본은 lightweight mode다. 범위·완료 조건이 명확하고 국소적·가역적인 변경은 spec/plan·워크트리·서브에이전트 없이 직접 처리한다. 무거운 절차(계획·리뷰·병렬 dispatch류 skill 포함)는 명시적 요청이나 고위험 작업에만, 이유와 비용을 설명하고 승인받은 뒤 쓴다.
- 완료/통과를 보고하기 전에 `verify` 파라미터의 명령을 **실제로 실행**하고 결과를 확인한다. 테스트를 지우거나 약화시켜 통과시키지 않는다.
- `generated` 파라미터에 해당하는 파일은 직접 수정하지 않는다.
- `decisions` 경로의 결정 기록과 충돌하는 변경은 하지 않는다. 뒤집어야 하면 먼저 알리고 새 결정 기록을 남긴다.
- 커밋은 Conventional Commits. 훅 우회(`--no-verify`) 금지.
- 남겨둔 주석은 함부로 삭제하지 않는다.
- 세션 시작 시 `handoff` 경로에 현재 브랜치 문서가 있으면 읽고 시작한다. 실패로 확정된 접근과 대화에서만 나온 결정은 **그 순간** handoff에 적는다.
- 재사용 가능한 교훈은 전역 규칙을 직접 고치지 말고 후보로 제안한다.
```

### 5.3 skills

- 원본: `global/skills/<name>/SKILL.md`. 기존 `conventions/*.md`를 변환한다.
- 형식은 평범한 markdown + frontmatter(`name`, `description`). 네이티브 skill 지원이 있는 에이전트는 그대로 읽고, 없는 에이전트는 always-on 끝에 자동 생성되는 **포인터 인덱스**(`- <description>: <절대경로>`)로 읽는다. 원본 하나, 소비 방식 둘.
- **`description`은 "언제 읽어라" 트리거다.** 기존 `AGENTS.snippet.md` on-demand 블록의 문구를 그대로 승격한다 — 이미 써보고 다듬은 문장이다.
  예: `DB/트랜잭션 리소스를 쓰는 코드를 작성·수정할 때(경계·롤백·부수효과·동시성)`

변환 규칙:

| 기존 문서의 부분 | 처리 |
|---|---|
| 원칙·주의·알려진 불일치 본문 | **그대로 보존** |
| 상단 `> 원본(SSOT)…복사 YYYY-MM-DD` 줄 | 삭제(복사하지 않으므로) |
| 하단 "이 규칙 적용하기"(복사 절차) | 삭제 → `## 필요한 프로젝트 파라미터` 섹션으로 교체 |
| 본문에 박힌 프로젝트 값 | 파라미터 이름 참조로 치환 |
| 스택별 실 config(`templates/<stack>/`) | skill이 아니다. `project/stacks/`에 남는다(프로젝트에 실제로 존재해야 하는 파일) |

always-on에 둘 수 없는 규칙을 skill로 내릴 때는 **안 불리면 안 지켜진다**는 걸 전제로 한다. 반드시 지켜져야 하면 enforcement로 올린다.

---

## 6. 프로젝트 계층

### 6.1 파라미터

위치: 프로젝트 `AGENTS.md`의 `## 프로젝트 파라미터` 섹션. 에이전트가 항상 읽는 파일이라 자동 로드되고, `key: value` 형태라 스크립트도 읽을 수 있다. 별도 파일을 만들지 않는다.

```markdown
## 프로젝트 파라미터

- stack: nestjs + vite-react
- package-manager: pnpm
- verify: ./scripts/check — 완료를 보고하기 전에 실행한다
- verify-quick: pnpm typecheck — 작은 변경용(선택)
- generated: src/routeTree.gen.ts, prisma/generated/** — 직접 수정하지 않는다
- issues: github:owner/repo
- board: github-project:owner/12
- decisions: docs/decisions/ — 기존 결정. 뒤집기 전에 읽는다
- handoff: docs/handoff/
- ops: docs/ops/ — 배포·운영(선택)
```

규칙:

1. **키 이름이 전역 규칙과의 계약이다.** 키를 추가·변경하면 `global/`과 `project/AGENTS.template.md`를 같은 커밋에서 고친다.
2. **각 줄은 혼자 읽혀도 뜻이 통하게 쓴다**(값 + 한 구절). 전역 설치가 없는 에이전트도 `verify` 줄만 보고 무엇을 해야 하는지 안다. 이것이 §7.6 degraded mode를 공짜로 만든다.
3. 프로젝트가 전역 규칙을 따르지 않기로 했다면 파라미터로 선언하고(`worktree: never`), 이유는 `decisions/`에 남긴다.
4. `AGENTS.md`는 파라미터 + 프로젝트 고유 규칙 + 사실 문서 포인터만. 목표 ~30줄, 상한 100줄.

### 6.2 사실

| 종류 | 위치 | 비고 |
|---|---|---|
| 목표·범위·구조 | `README.md`, `docs/architecture.md` | 이미 있는 것을 쓴다. 새 디렉터리(`.ai/`)를 강제하지 않는다 |
| **결정** | `docs/decisions/NNN-<slug>.md` | **신규.** 아래 참고 |
| 운영 | `docs/ops/`, compose·워크플로 실파일 | |
| 진행 상태 | `docs/handoff/<브랜치>.md`, todo | 기존 규칙 유지. 병합 시 삭제 |
| 프로젝트 고유 규칙 | `docs/` 아래 자유 | 예: nowhere `map-module.md` |

**결정 기록**은 v1에서 가져오는 가장 값어치 있는 신규 항목이다. 에이전트가 "개선"이라며 의도된 결정을 되돌리는 문제는 handoff로 못 막는다(병합 시 삭제되므로). 한 파일 = 한 결정, 한 화면 이내:

```markdown
# NNN. <결정 한 줄>
- 날짜 / 상태: 채택 | 폐기(→ NNN)
## 맥락      무엇이 문제였나
## 결정      무엇을 하기로 했나
## 버린 대안  왜 안 했나 — 에이전트가 다시 제안할 법한 것 위주
## 되돌릴 조건 언제 이 결정을 다시 봐야 하나
```

채택 기준은 같다: **에이전트가 모르면 되돌릴 법한 결정만** 적는다.

### 6.3 `scripts/check` 계약

- 모든 프로젝트는 `verify` 파라미터가 가리키는 **단일 진입점**을 가진다. 기본값 `./scripts/check`.
- 인자 없이 실행, 종료 코드 0 = 통과. 내부 구성은 스택마다 자유(`pnpm lint && pnpm typecheck && pnpm test`, `./gradlew check` …).
- 실패 메시지는 에이전트가 읽고 고칠 수 있게 구체적으로.
- 기존 스크립트가 있으면(`verify-all.sh`) 감싸거나 `verify`가 그것을 직접 가리키게 한다. 이름 통일이 목적이 아니라 **진입점이 하나**인 게 목적이다.
- Stop hook으로 자동 실행하는 것은 **보류**한다. 질의응답 세션까지 막으면 우회 습관이 생긴다. always-on 규칙으로 시작하고, 미실행 완료 보고가 실제로 관찰되면 "코드 변경이 있을 때만" 조건으로 추가한다.

### 6.4 프로젝트에 두는 에이전트 설정

- `.claude/settings.json`: **그 프로젝트 고유 allow만**(스크립트명, `rm -rf dist` 같은 exact 규칙). 공통 deny/ask는 전역에서 온다.
- 전역이 없는 환경에 대비해 최소 deny를 겹쳐 두는 것은 허용한다(백스톱).
- `CLAUDE.md`·`GEMINI.md`·`.agents/rules/repository.md`는 `AGENTS.md`를 가리키는 얇은 진입점으로 유지(기존 규칙 그대로).

### 6.5 프로젝트에 두지 않는 것

- 전역 규칙 본문의 복사본(`docs/conventions/*.md`) → 삭제한다.
- 전역 always-on 문장의 복제 → 파라미터 줄의 한 구절로 충분하다.

---

## 7. 이식성 설계

### 7.1 환경 축과 요구

| 축 | 경우 | 요구 |
|---|---|---|
| 머신 | 개인 Mac(현재) · 회사 PC · 새 PC | clone + bootstrap 1회로 동일 상태 |
| 에이전트 | Claude Code · Codex · Gemini CLI | 같은 always-on, 같은 skill 본문 |
| OS/셸 | macOS · Linux · WSL | bash + git + python3만 가정. GNU 전용 플래그 금지 |
| 전역 없음 | 클라우드 세션 · 컨테이너 · 협업자 · 정책상 설치 불가 | 프로젝트만으로 최소 동작(§7.6) |

Windows 네이티브(WSL 아님)는 지원 범위 밖으로 둔다.

### 7.2 원본은 하나, 설치는 환경마다

```
dev-conventions (git · 유일한 원본)
        │  bootstrap.sh
        ▼
환경의 전역 설정  ~/.claude  ~/.codex  ~/.gemini      ← 설치본. 직접 수정하지 않는다
```

- 전역 파일을 직접 고치지 않는다. 고칠 일이 생기면 원본을 고치고 재설치한다.
- 예외: 머신 고유 값(§7.7)과 다른 도구가 관리하는 구역.
- 복사 표면적이 `프로젝트 수 × 문서 수`에서 `환경 수 × 1`로 줄어든다. 환경은 2~3개고 갱신은 명령 하나다.

### 7.3 설치 방식 — 가리킬 수 있으면 가리키고, 못 가리키면 구역을 정해 복사한다

| 대상 | 방식 | 이유 |
|---|---|---|
| skills | **디렉터리 심링크** `<config>/skills/<name>` → `<repo>/global/skills/<name>` | 복사본이 없으면 드리프트도 없다. `git pull`이 곧 갱신 |
| hook 스크립트 | 심링크 또는 repo 절대경로 직접 참조 | 위와 같음 |
| always-on | **관리 구역 복사** — 대상 파일 안 `<!-- BEGIN dev-conventions -->` … `<!-- END dev-conventions -->` 사이만 교체 | 세 에이전트 공통으로 동작하는 유일한 방식. 구역 밖의 기존 내용은 보존 |
| settings(JSON/TOML) | **키 단위 병합** — 자기가 추가한 항목을 lock 파일에 기록해 두고, 다음 설치 때 그 항목만 갱신·제거 | JSON엔 주석이 없어 구역 표시가 불가. 다른 도구·수동 항목을 건드리지 않기 위함 |

- 심링크를 못 쓰는 환경은 `--copy`로 설치한다. 이때는 §7.5의 낡음 감지가 유일한 안전망이다.
- 모든 설치 동작은 **멱등**이다. 두 번 실행해도 결과가 같다.
- 덮어쓰기 전에는 항상 백업한다(`<file>.bak-<timestamp>`). 전역 `settings.json`은 이미 두 번 백업된 이력이 있다.

### 7.4 에이전트별 설치 매핑

| | Claude Code | Codex | Gemini CLI |
|---|---|---|---|
| 설정 디렉터리 | `${CLAUDE_CONFIG_DIR:-~/.claude}` | `${CODEX_HOME:-~/.codex}` | `~/.gemini` |
| always-on | `CLAUDE.md` 관리 구역 | `AGENTS.md` 관리 구역 | `GEMINI.md` 관리 구역 |
| skills | `skills/<name>/` 링크 | `skills/<name>/` 링크 | 포인터 인덱스(always-on 구역 끝에 자동 생성) |
| enforcement | `settings.json` 병합 + hook | `config.toml`·`rules/` | 없음 |
| 명령 | `commands/apply-conventions.md` | — | — |

- bootstrap은 **설정 디렉터리가 존재하는 에이전트에만** 설치한다. 없는 에이전트는 건너뛰고 보고한다.
- 에이전트별 차이는 이 표(=`install/targets`)와 `global/enforcement/<agent>/`에만 있다. `always-on.md`와 `skills/`에는 에이전트 분기가 없다. 단, 도구별 **사실**을 본문에 적는 건 허용한다(§2 비목표).
- `~/.codex/AGENTS.md`의 기존 "Superpowers policy"는 always-on 초안에 흡수됐다. 설치 시 관리 구역으로 대체하고, `templates/global/codex/`는 폐기한다.

### 7.5 낡음 감지

복사가 남는 곳(always-on 구역, settings 병합, `--copy` 모드)은 낡을 수 있다. **낡음을 없애려 하지 말고 보이게 만든다.**

- 설치 시 `<config>/.dev-conventions.lock` 기록: `repo`(경로), `commit`(설치 시점 HEAD), `installed_at`, `mode`(link|copy), `managed`(자기가 넣은 settings 항목).
- `bootstrap.sh --check`: lock의 `commit`과 repo HEAD를 비교. 다르면 종료 코드 1과 함께 한 줄 출력. repo가 없는 환경이면 조용히 0.
- 호출 지점: (1) 수동, (2) SessionStart hook — 하루 1회로 제한, 차단하지 않음(경고 한 줄만).
- 심링크 모드에서 남는 낡음은 "pull을 안 했다"뿐이다. 원격 비교는 네트워크가 필요하므로 **선택 기능**으로 두고, 실패하면 조용히 넘어간다.

### 7.6 전역이 없는 환경 (degraded mode)

클라우드 세션·컨테이너·협업자 환경에는 `~/.claude`가 없다. 이 환경에서 프로젝트는:

| 있다 | 없다 |
|---|---|
| 무엇을 실행해 검증하나(`verify`) | lightweight mode 등 개인 작업 스타일 |
| 무엇을 건드리면 안 되나(`generated`) | handoff·todo의 상세 절차 |
| 왜 이렇게 됐나(`decisions/`) | 전역 deny/ask (→ 프로젝트 최소 deny로 백스톱) |
| 스택·패키지 매니저·이슈 트래커 | skill 본문 |

**판정 기준: 없어지는 것은 "나의 스타일"이고, 남는 것은 "프로젝트의 무결성"이다.** 이 구분이 §4 Q1(다른 프로젝트에서도 참인가)과 같은 선이라는 점이 설계가 일관된다는 증거다.

본인 소유의 원격 환경에서 전체 규칙이 필요하면 거기서도 `bootstrap.sh`를 실행한다. 저장소에 비밀정보가 없으므로 public clone으로 충분하다.

### 7.7 머신 고유 값 — 원본에 넣지 않는 것

- 절대경로(`additionalDirectories`, repo clone 위치) — bootstrap이 설치 시점에 감지해 주입한다(현행 방식 유지).
- 토큰·자격증명.
- 취향·UI 설정(`model`, `theme`, `statusLine`, `tui`, 플러그인 목록).
- 다른 도구가 등록한 hook.

bootstrap은 이 키들을 읽지도 쓰지도 않는다.

### 7.8 `bootstrap.sh` 계약

```
bootstrap.sh              설치/갱신 (멱등)
bootstrap.sh --check      낡음 검사만. 0=최신, 1=낡음
bootstrap.sh --dry-run    바뀔 내용만 출력
bootstrap.sh --copy       심링크 대신 복사
bootstrap.sh --uninstall  lock에 기록된 자기 설치분만 제거
```

- 의존성: bash, git, python3(JSON/TOML 병합). `sed -i`처럼 BSD/GNU가 갈리는 호출은 쓰지 않는다.
- 자기 위치로 repo 경로를 감지한다(현행 유지).
- 끝나면 에이전트별로 무엇을 설치·건너뛰었는지 표로 보고한다.

---

## 8. `dev-conventions` 저장소 구조 (after)

```
dev-conventions/
├── AGENTS.md · CLAUDE.md · GEMINI.md        이 repo 자체의 지침(현행)
├── README.md                                 구조·설치·규칙 목록
├── bootstrap.sh                              §7.8
├── global/                                   ── 환경에 설치되는 것 ──
│   ├── always-on.md                          §5.2  (단일 원본, 15줄 예산)
│   ├── skills/<name>/SKILL.md                §5.3  (기존 conventions/*.md)
│   └── enforcement/
│       ├── claude/  settings.fragment.json · hooks/*.sh
│       └── codex/   config.fragment.toml · rules/
├── project/                                  ── 프로젝트에 스캐폴딩되는 것 ──
│   ├── AGENTS.template.md                    파라미터 섹션 골격
│   ├── decision.template.md
│   ├── check.template.sh
│   ├── handoff.template.md · todo-file.template.md
│   └── stacks/<stack>/                       실 config (기존 templates/nestjs 등)
├── install/
│   ├── targets                               §7.4 매핑
│   └── apply-conventions.md                  프로젝트 스캐폴딩 명령(재작성)
├── inbox/                                    승격 후보(현행 유지)
└── docs/specs/                               이 문서
```

- `conventions/` → `global/skills/`, `templates/<stack>/` → `project/stacks/`, `templates/harness/` → `global/enforcement/`.
- `/apply-conventions`는 이름을 유지하되 하는 일이 바뀐다: **문서 복사 → 프로젝트 스캐폴딩**(파라미터 섹션, `scripts/check`, `docs/decisions/`, 스택 config, 프로젝트 고유 allow).

---

## 9. 기존 7개 규칙 배치표

| 규칙 | skill로 가는 본문 | always-on | enforcement | 프로젝트 파라미터 |
|---|---|---|---|---|
| harness-engineering | 전부. 단 "프로젝트마다 settings 복사" 절차는 §5.1·§6.4로 재작성 | — | 권한 패턴 B의 공통분 | 고유 allow |
| agent-workflow | 병렬 dispatch·워크트리·가벼운 실행 | lightweight mode 한 줄 | — | (거부 시) `worktree` |
| handoff | 무엇을 담고 빼나·갱신 시점·병합 시 삭제 | 시작 시 읽기·그 순간 기록 | — | `handoff` |
| todo-workflow | 번호 규칙·3중 동기화·spec/plan 연계 | — | — | `issues`, `board` |
| coding-conventions | 커밋·훅·주석·자동생성물 | 커밋 형식·주석·`generated` | `--no-verify` 차단 hook | `package-manager`, `stack`, `generated` + `project/stacks/` 실파일 |
| transaction-management | 전부 | — | — | — |
| deployment | 원칙 전부 | — | — | `ops` + compose·워크플로 실파일 |

"pnpm 통일"은 전역 규칙에서 **파라미터 기본값**으로 내린다(§1.3 근거). `/apply-conventions`가 node 프로젝트에 기본값으로 제안한다.

---

## 10. 승격 루프

파이프라인은 이미 있다(`inbox/` + `/import-conventions`). 빠진 건 **트리거**다.

```
프로젝트 작업 ──► 교훈 발견 ──► 후보 1건 (dev-conventions/inbox/)
                                   │  사람이 심사
                        ┌──────────┼───────────┐
                        ▼          ▼           ▼
                   전역 규칙     프로젝트 사실    기각
                 (§4 Q2로 층 결정)  (그 repo docs/)
```

- **트리거를 작업 종료에 묶는다**: 브랜치 병합으로 handoff를 삭제하는 시점에 "재사용할 교훈이 있었나"를 한 번 묻는다(handoff skill에 한 줄 추가). 사람 기억에 의존하지 않는다.
- 에이전트는 후보를 **제안만** 한다. `global/`을 직접 고치지 않는다(always-on 마지막 줄).
- 심사 기준은 §4 채택 기준 + "**실제로 실패가 관찰됐는가**". 관찰되지 않은 일반론은 기각한다.
- 첫 심사 대상: nowhere의 `external-request-discipline.md`, `refactoring-principles.md`. `map-module.md`는 프로젝트 사실로 남긴다.

---

## 11. 적용 단계

각 단계는 **검증을 통과해야** 다음으로 간다. 1~2단계는 어떤 프로젝트도 건드리지 않는다.

| # | 단계 | 하는 일 | 검증 |
|---|---|---|---|
| 1 | 원본 구성 | `global/`·`project/` 구조로 재배치. 7개 문서를 §5.3 규칙으로 변환. 현재 전역 `settings.json`에서 공통분 역수집 | 변환 전후 본문 diff에서 삭제된 것이 출처 줄·"적용하기" 절뿐인지 확인 |
| 2 | bootstrap + 이 PC 설치 | §7.8 구현. `--dry-run` → 설치 | 새 세션에서 (a) always-on이 로드되는가 (b) skill 7개가 목록에 뜨는가 (c) 기존 hook·allow가 그대로인가 (d) 재실행해도 diff 0 (e) §13 가정 1~4 판정 |
| 3 | 파일럿 1개 | nowhere: AGENTS.md 파라미터화, `scripts/check`, `docs/decisions/` 첫 기록, `docs/conventions/` 삭제 | 실제 작업 1건을 새 구조로 수행. 에이전트가 `verify`를 스스로 찾아 실행하는가 |
| 4 | degraded 검증 | 전역 설치가 없는 상태(`CLAUDE_CONFIG_DIR`를 빈 디렉터리로)에서 nowhere 작업 | §7.6의 "있다" 열이 실제로 동작하는가 |
| 5 | 나머지 프로젝트 | `/apply-conventions` 재작성 후 순차 적용. JVM 1개 포함 | 프로젝트 내 규칙 복사본 0개. JVM에서 node 규칙이 끼어들지 않는가 |
| 6 | 두 번째 환경 | 다른 PC에서 clone + bootstrap | 소요 시간, 수동 개입 횟수. **이 단계 전까지 이식성은 미검증이다** |
| 7 | 승격 트리거 | handoff skill에 트리거 추가. nowhere 자생 규칙 2건 심사 | 한 달 뒤 inbox 처리 기록이 생겼는가 |

되돌리기: 2단계는 `--uninstall` + 백업 복원. 3·5단계는 프로젝트별 커밋 revert. 1단계는 dev-conventions 브랜치에서 진행한다.

---

## 12. 성공 기준

| 지표 | 현재 | 목표 |
|---|---|---|
| 프로젝트 내 전역 규칙 복사본 | 13개(3개 프로젝트) | 0 |
| 최신 규칙이 도달한 프로젝트 | 0 / 전체 | 전체(설치 즉시) |
| 에이전트 간 always-on 일치 | 불일치(Codex만 정책 보유) | 3개 동일 |
| 전역 설정의 원본 위치 | 이 Mac | dev-conventions |
| 새 환경 셋업 | 수동·미측정 | clone + 명령 1회 |
| 공통 검증 진입점 보유 프로젝트 | 0 | 활성 프로젝트 전부 |
| 작업당 정정 횟수("그거 아니야, 다시") | 미측정 | 파일럿에서 기록 시작, 감소 추세 |

마지막 지표가 안 줄면 문서가 제 값을 못 하는 것이다. 그때는 구성요소를 하나씩 빼보며 무엇이 실제로 하중을 받는지 확인한다(`harness-engineering.md` 원칙).

---

## 13. 검증이 필요한 가정

이 설계가 참이라고 가정했지만 작성 시점에 확인하지 못한 것. **2단계에서 판정한다.**

1. Claude Code가 심링크된 `~/.claude/skills/<name>/`을 따라 읽는다. — 아니면 `--copy`를 기본으로 바꾸고 §7.5 비중이 커진다.
2. Codex의 전역 skill 경로와 `SKILL.md` frontmatter 호환. — 아니면 Codex도 포인터 인덱스로 내린다.
3. Gemini CLI의 네이티브 skill·import 지원 여부. — 지원하면 포인터 인덱스 대신 네이티브로 올린다.
4. 전역 `settings.json`의 hook 래퍼가 외부 도구 관리 구역이라는 추정, 그리고 배열에 항목을 추가해도 그 도구가 덮어쓰지 않는가.
5. always-on 15줄 예산이 실제로 충분한가. — 파일럿에서 판단.
6. 프로젝트 `.claude/settings.json`의 allow가 전역 deny/ask와 의도대로 합성되는가(평가 순서 deny → ask → allow).

---

## 14. 안 하기로 한 것과 이유

| 안 | 버린 이유 |
|---|---|
| 처음부터 새 저장소로 재작성 | 버려지는 건 모델이 재생성 못 하는 검증된 지식이고, 얻는 건 미검증 목차다. 깨진 건 배포 한 곳이다 |
| v1의 Skill × Convention × Stack 6칸 분류 | 문서마다 분류 고민이 붙는다. "자기완결형 문서 한 개"가 낫다 |
| v1 §6 분야별 Skill 목차 선작성 | 채택 기준(에이전트가 다르게 행동하는가)을 통과할 항목이 적다. 실패 관찰 후 추가 |
| v1 Rule 10(본문에 에이전트 이름 금지) | 도구별 사실이 가장 값어치 있는 지식이다. 분기를 설치 계층에 가두는 것으로 충분하다 |
| git submodule로 프로젝트에 연결 | 관리 부담이 크고 협업자·클라우드 환경에서 깨지기 쉽다 |
| 복사 유지 + 낡음 검사만 추가 | 표면적(프로젝트 × 문서)이 그대로다. 감지해도 갱신 비용이 남는다 |
| Stop hook으로 `verify` 강제 | 아직 실패가 관찰되지 않았고 질의응답 세션을 막는다. 관찰 후 조건부로 |
| 별도 파라미터 파일(`.agents/params.yml`) | 에이전트가 자동으로 읽지 않는다. AGENTS.md 한 섹션이면 충분하다 |
| 설치 프로파일(회사/개인) | 필요가 관찰되지 않았다 |
