# dev-conventions

여러 PC(회사/개인)를 오가도 지켜지는 나만의 공통 개발 규칙 모음.
각 규칙은 `conventions/`에 **자기완결형 문서 한 개**로 정리돼 있고, 실제 설정 값은 `templates/`에 **복사용 실파일**로 둔다. 새 프로젝트엔 그대로 복붙해서 쓴다.

## 규칙 목록

| 규칙 | 문서 | 요약 |
|---|---|---|
| TODO 관리 | `conventions/todo-workflow.md` | `#000` 3자리 고정 번호 + `docs/to-do/*.md`(SSOT) + GitHub Issues 미러 + Projects 보드 |
| 코딩 컨벤션 | `conventions/coding-conventions.md` | pnpm·Conventional Commits·husky/lint-staged·검증 게이트 + 스택별 실 config는 `templates/<stack>/` |
| 에이전트 작업 규칙 | `conventions/agent-workflow.md` | 변경 전 계획-승인 · 풀스택 계약 확정 후 병렬 dispatch · 가벼운 실행(무거운 검증은 CI) |

## 구조

```
AGENTS.md                 저장소 공통 지침 원본(SSOT)
CLAUDE.md                 Claude Code용 얇은 진입점 → AGENTS.md
GEMINI.md                 Gemini CLI용 얇은 진입점 → AGENTS.md
.agents/rules/
  repository.md           공통 agent rule 진입점 → AGENTS.md
bootstrap.sh              전역 /apply-conventions 커맨드 설치(PC마다 1회, 경로 자기감지)
install/
  apply-conventions.md    bootstrap이 ~/.claude/commands/로 설치하는 커맨드 본체
conventions/              규칙 원본 문서(원칙 + 셋업 + 적용법)
inbox/                    다른 프로젝트 원자료 → /import-conventions로 정규화
templates/
  AGENTS.snippet.md       대상 repo AGENTS.md에 병합하는 "## 공통 규칙" 블록
  convention.template.md  새 규칙 문서 골격
  todo-file.template.md   to-do md 파일 원본
  nestjs/                 NestJS: tsconfig(.build).json · eslint.config.mjs · .prettierrc
  vite-react/             Vite/React: tsconfig 3종 · eslint.config.js · components.json
  next/                   Next.js: tsconfig.json · eslint.config.mjs (Next 16 flat)
```

> `templates/<stack>/` config는 SuperMarkit 실 config 스냅샷(2026-07-13)이다. 각 폴더 README에 기준 버전과 주의사항이 있다.

## 새 프로젝트에 규칙 적용하기

### 방법 A — `/apply-conventions` (추천)

먼저 PC마다 1회, 이 repo에서 전역 커맨드를 설치한다(clone 경로 무관, `bootstrap.sh`가 자기 위치를 감지):

```sh
./bootstrap.sh
```

그다음 **적용할 프로젝트 폴더에서** 실행:

```sh
/apply-conventions            # 기본 소스 = bootstrap이 감지한 이 repo 경로
/apply-conventions <경로>      # 다른 clone을 쓰려면 경로 지정 (또는 DEV_CONVENTIONS_DIR)
```

문서 복사(+출처 줄 자동 채움)·스택 감지 후 config 복사·`AGENTS.md` 공통 지침 병합·provider 진입점 구성·라벨 셋업까지 해준다. 덮어쓰기·`gh` 실행 전엔 확인한다.

### 방법 B — 수동

각 규칙 문서 맨 아래 **"이 규칙 적용하기"** 절차를 따른다. 공통 패턴:

1. `conventions/<규칙>.md`를 대상 repo `docs/conventions/`로 복사하고, 문서 상단 출처 줄을 **복사일**로 채운다(복사본이 낡았는지 판단용).
2. 쓰는 스택이면 `templates/<stack>/`의 config 파일을 대상 repo에 복사(설치 버전에 맞춰 조정 후 `pnpm lint`/`pnpm build` 확인).
3. 규칙 문서의 셋업 명령(라벨 생성 등)을 1회 실행.
4. 대상 repo `AGENTS.md`의 `## 공통 규칙` 섹션을 `templates/AGENTS.snippet.md`로 채우고, `CLAUDE.md`, `GEMINI.md`, `.agents/rules/repository.md`는 `AGENTS.md`를 참조하는 얇은 진입점으로 둔다.

> **왜 이 방식인가 (에이전트 참조 관점):** `AGENTS.md`에 공통 지침을 한 번만 두고, 각 agent가 자동으로 읽는 provider 진입점에서 이를 참조하면 agent를 바꿔도 같은 규칙이 적용된다.
> - **always-on 소수 규칙**(검증 게이트·커밋·자동생성물 금지 등)은 `AGENTS.md`에 **인라인**으로 둔다 — 상세 문서 경로만 있으면 에이전트가 문서를 안 열 수 있다.
> - **나머지 규칙**은 포인터로 두되 **"언제 읽어라" 힌트**를 붙여 문서를 열 트리거를 준다.
> - provider별 파일에는 공통 지침을 복제하지 않는다. provider 전용 동작이 꼭 필요한 경우에만 그 이유와 함께 별도로 둔다.
> - 상세 설명·값은 `docs/conventions/` 문서와 config 파일에. 규칙이 늘면 포인터 줄만 하나씩 추가.

## 새 규칙 추가하기

### 방법 A — 원자료 일괄 import (추천)

다른 프로젝트에서 쓰던 규칙을 `inbox/`에 아무 형식으로나 모아두고, 이 repo에서 **`/import-conventions`** 실행. 주제별로 분해해 기존 규칙과 대조 후 **신규 생성/갱신**하고, README 표·AGENTS 포인터까지 정리해준다. 자세한 건 `inbox/README.md`.

### 방법 B — 하나씩 수동

`templates/convention.template.md`를 `conventions/<이름>.md`로 복사해서 시작(골격·출처 줄·"적용하기" 포함). 상세 순서는 `AGENTS.md`의 "새 규칙 추가하기" 체크리스트 참고. 요약:

1. 템플릿 복사 → 채우기(자기완결형: 원칙 + 셋업 + 적용법).
2. 값이 있으면 `templates/<이름>/`에 실파일 + 폴더 README(출처·기준 버전).
3. 위 "규칙 목록" 표에 한 줄, `templates/AGENTS.snippet.md` 포인터에 한 줄 추가.

## 이동성

- 이 repo를 GitHub public repo로 두면 새 PC에서 clone/다운로드만 하면 됨 (스크립트·비밀정보 없음).
- 각 프로젝트에 복사된 규칙(`docs/conventions/*` + config 파일 + `AGENTS.md` + provider 진입점)은 그 repo에 커밋되므로, repo를 clone하는 어떤 PC에서든 자동으로 따라온다.
- 복사본은 원본과 **자동 동기화되지 않는다.** 복사일(출처 줄)로 낡음 여부를 판단하고, 원본이 바뀌면 필요한 repo에 다시 반영한다.
