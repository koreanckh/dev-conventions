---
description: dev-conventions 규칙을 현재 프로젝트에 적용한다 — 규칙 본문이 아니라 파라미터·검증 진입점·결정 기록을 스캐폴딩한다
---

# /apply-conventions $ARGUMENTS

현재 프로젝트(cwd)를 **v2 구조**로 맞춘다. 규칙 본문은 환경(전역)에 설치돼 있으므로 **복사하지 않는다.** 이 커맨드가 만드는 것은 그 규칙이 이름으로 참조하는 **값**과, 값만으로는 안 되는 **실행되는 것**(검증 진입점)이다.

**하지 않는 것:** 애플리케이션 코드 수정 · 규칙 본문 복사 · 커밋 · 기존 config 덮어쓰기 · 없는 배포/테스트 파일 관성 생성.

## 소스 레포 경로 결정 (이 순서)

1. 인자 `$ARGUMENTS`가 있으면 그 경로.
2. 환경변수 `$DEV_CONVENTIONS_DIR`.
3. 기본값 `{{DEV_CONVENTIONS_DIR}}` (`bootstrap.sh`가 감지해 넣은 경로).

없거나 존재하지 않으면 멈추고 알린다. 이하 `<SRC>`.

## 0. 먼저 실태를 조사한다 (쓰기 전에 읽는다)

추측으로 파라미터를 채우지 않는다. 아래를 **실제로 확인**하고 모르는 값은 비워 두고 묻는다.

| 확인할 것 | 어디서 |
|---|---|
| 스택·패키지 매니저 | `package.json`(`packageManager`)·`pyproject.toml`·`pubspec.yaml`·`build.gradle` |
| **이미 있는 검증 진입점** | `scripts/`(`verify-all.sh`·`check`·`dev.mjs`), `package.json`의 scripts, CI 워크플로 |
| 자동 생성물 | 마이그레이션 디렉터리(drizzle·alembic·prisma), `*.gen.*`, `.next/types` |
| 이슈·보드 | `git remote`, `gh issue list`, `gh project list --owner <owner>` |
| **to-do 번호 체계** | `docs/to-do/*.md`의 `번호:`와 `이슈:` 줄을 **대조**한다. 어긋나면 `todo-numbering: local`이다 |
| handoff 위치·형태 | `docs/handoff/`·`docs/agent/`의 실제 파일 |
| **문서 브랜치**(`docs-branch`) | 통합 브랜치가 `main`인지 `dev`인지, main에 직접 push가 막혀 있는지(`gh api repos/<owner>/<repo>/branches/main/protection`) |
| 운영 문서 | `DEPLOY.md`·`docs/ops/`·`deploy/` |
| 기존 규칙 복사본 | `docs/conventions/*.md` |

## 1. 복사본을 지우기 전에 드리프트를 건진다 (제일 중요)

`docs/conventions/*.md`가 있으면 **바로 지우지 않는다.** 복사본에는 그 프로젝트가 덧붙인 내용이 섞여 있다(실제 사례: Node 버전 함정, 커밋 type 목록, 브랜치 번호 규칙, "커밋은 사람이 요청할 때만").

```sh
# 복사본과 원본을 대조해 "복사본에만 있는 줄"을 본다
diff <(git -C <SRC> show <복사 시점 커밋>:conventions/<이름>.md) docs/conventions/<이름>.md | grep '^>'
```

복사 시점 커밋을 모르면 현재 `<SRC>/global/skills/<이름>/SKILL.md`와 대조하고, 출처 줄·"이 규칙 적용하기" 절 차이는 무시한다. 건진 줄은 성격에 따라 옮긴다.

| 건진 것 | 어디로 |
|---|---|
| 프로젝트마다 다른 값(커밋 type·패키지 매니저·경로) | `AGENTS.md` 파라미터 |
| 실행돼야 의미가 있는 지식(검사 순서·환경 함정) | **검증 스크립트 안으로** — 산문이 아니라 코드로 |
| 이 프로젝트에서만 참인 규칙 | `AGENTS.md`의 `## 이 프로젝트만의 규칙` |
| 전역 규칙과 어긋나는 실태 | 4단계의 결정 기록 |
| 이 저장소가 자체로 쓴 규칙 문서 | **지우지 않는다.** 그대로 두고 AGENTS.md에서 가리킨다 |

## 2. `AGENTS.md`를 파라미터 형태로 만든다

`<SRC>/project/AGENTS.template.md`를 골격으로 쓴다. 기존 `AGENTS.md`의 **프로젝트 고유 내용(경계·도메인 설명)은 보존**하고, 복사된 공통 규칙 블록만 걷어낸다.

- 각 파라미터 줄은 **혼자 읽혀도 뜻이 통하게**(값 + 한 구절). 전역 설치가 없는 환경에서 이 줄만 읽고 움직일 수 있어야 한다.
- 쓰지 않는 파라미터 줄은 지운다. 모르는 값은 채우지 말고 묻는다.
- 목표 ~30줄, 상한 100줄.
- `CLAUDE.md`·`GEMINI.md`·`.agents/rules/repository.md`는 `AGENTS.md`를 가리키는 얇은 진입점으로 두고 공통 지침을 복제하지 않는다.

## 3. 검증 진입점을 정한다 (`verify`)

**이미 진입점이 있으면 새로 만들지 않는다.** `verify`가 그것을 직접 가리킨다 — 이름 통일이 목적이 아니라 진입점이 하나인 게 목적이다(실제 사례: mulzipsa의 `scripts/verify-all.sh`).

없으면 `<SRC>/project/check.template.sh` → `scripts/check`(+`chmod +x`)로 만들고 그 프로젝트의 실제 명령으로 바꾼다. 규칙:

- **지금 통과하는 범위로만 정의한다.** 로컬에서 돌 수 없는 검사(툴 미설치·전용 env 필요)는 넣지 않되, **빠졌다는 사실과 수동 실행법을 스크립트 주석에 적는다.** 조용히 건너뛰는 단계는 안전장치가 아니다.
- e2e·DB가 필요한 검사는 기본에서 빼고 여는 법을 적는다.
- 환경 함정이 있으면 **맨 앞 단계로** 넣는다(예: Node 버전 확인 — 범위 밖에서는 테스트가 실패가 아니라 시작을 못 한다).
- 만들었으면 **실제로 한 번 돌린다.** 실패하면 그건 드러난 사실이다 — 고치는 건 이 커맨드의 일이 아니다. to-do로 세우거나, 실패 단계를 빼고 이유를 적는다.

## 4. 전역 규칙과 어긋나는 실태는 결정으로 기록한다

조사에서 전역 기본값과 다른 점이 나오면 `<SRC>/project/decision.template.md` → `docs/decisions/NNN-<slug>.md`.

- 자주 나오는 것: `todo-numbering: local`(번호 자체 배정 — 기존 저장소만), `docs-branch: branch`(main이 보호돼 문서 직행이 막힘), handoff 형태, 워크트리 미사용.
- **맥락은 관찰된 사실로 쓴다.** 왜 그렇게 했는지 모르면 지어내지 말고 사용자에게 묻는다.
- `버린 대안`에 **전역 기본값을 왜 안 쓰는지**를 적는다. 이게 나중에 에이전트가 "정리"하겠다고 되돌리는 걸 막는 유일한 장치다.

## 5. 복사본을 지우고 옛 링크를 안내한다

- 전역 규칙 복사본만 `git rm`한다. 자생 규칙은 남긴다.
- 과거 to-do·spec·plan·handoff 안의 옛 경로는 **고치지 않는다**(그 시점의 기록이다). 대신 `docs/conventions/README.md`에 "없어진 경로 → 지금 읽을 것" 표를 남긴다.

## 6. 프로젝트 고유 하네스만 둔다

- `.claude/settings.json`: **그 프로젝트 고유 allow만**(검증 진입점, 프로젝트 스크립트). 공통 deny/ask는 전역 설치본에서 온다. 전역이 없는 환경 대비 최소 deny(`Read(.env)` 등)를 겹쳐 두는 건 허용한다.
- `.claude/settings.local.json`을 `.gitignore`에 넣는다.
- **주의:** 프로젝트 allow는 그 설정 디렉터리에서 워크스페이스를 trust하기 전까지 무시된다. 새 환경에서는 첫 대화형 실행이 필요하다.
- 스택 config(`eslint`·`prettier`·`tsconfig`)는 **기존에 있으면 덮지 않는다.** 새 프로젝트를 시작할 때만 `<SRC>/project/stacks/<stack>/`을 초기값으로 쓴다 — 덮으면 lint 규칙이 바뀌어 코드에 재정렬 diff가 번진다.

## 7. 검증하고 보고한다

1. `verify`를 **실제로 실행**한다.
2. 실행 뒤 `git status`를 본다 — 검증이 추적되는 파일을 건드리는 경우가 있다(실제 사례: flutter가 `ios/Flutter/*.xcconfig`를 다시 씀). 그런 파일은 되돌리고, 그 사실을 `AGENTS.md`에 적는다.
3. **`git add -A`를 쓰지 않는다.** 툴체인 산출물·임시 파일이 딸려 들어온다(실제 사례: `Podfile`, `scratchpad/`). 바꾼 경로를 하나씩 적는다.
4. 리포트: 무엇을 옮겼는지 · 무엇을 빼고 왜인지 · **사람이 판단해야 할 것**(모르는 파라미터, 전역과 어긋나는 실태, verify에서 뺀 검사)을 구분해 적는다.

## 원칙

- 기존 파일 덮어쓰기·`gh` 실행 전에는 확인받는다.
- **커밋하지 않는다.** 대상 저장소 규칙이 대개 "커밋은 사람이 요청할 때만"이다.
- 규칙 본문을 프로젝트로 복사하지 않는다. 그게 이 구조가 없애려는 것이다.
- git은 빈 디렉터리를 추적하지 않는다. `mkdir`만 한 항목은 셋업 완료로 보고하지 않는다.
