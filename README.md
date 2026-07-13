# dev-conventions

여러 PC(회사/개인)를 오가도 지켜지는 나만의 공통 개발 규칙 모음.
각 규칙은 `conventions/`에 **자기완결형 문서 한 개**로 정리돼 있고, 실제 설정 값은 `templates/`에 **복사용 실파일**로 둔다. 새 프로젝트엔 그대로 복붙해서 쓴다.

## 규칙 목록

| 규칙 | 문서 | 요약 |
|---|---|---|
| TODO 관리 | `conventions/todo-workflow.md` | `docs/to-do/*.md`(SSOT) + GitHub Issues 미러 + Projects 보드 |
| 코딩 컨벤션 | `conventions/coding-conventions.md` | pnpm·Conventional Commits·husky/lint-staged·검증 게이트 + 스택별 실 config는 `templates/<stack>/` |
| 에이전트 작업 규칙 | `conventions/agent-workflow.md` | 변경 전 계획-승인 · 풀스택 계약 확정 후 병렬 dispatch · 가벼운 실행(무거운 검증은 CI) |

## 구조

```
conventions/            규칙 원본 문서(원칙 + 셋업 + 적용법)
templates/
  CLAUDE.snippet.md     대상 repo CLAUDE.md에 붙여넣는 "## 공통 규칙" 블록
  todo-file.template.md to-do md 파일 원본
  nestjs/               NestJS: tsconfig(.build).json · eslint.config.mjs · .prettierrc
  vite-react/           Vite/React: tsconfig 3종 · eslint.config.js · components.json
  next/                 Next.js: tsconfig.json · eslint.config.mjs (Next 16 flat)
```

> `templates/<stack>/` config는 SuperMarkit 실 config 스냅샷(2026-07-13)이다. 각 폴더 README에 기준 버전과 주의사항이 있다.

## 새 프로젝트에 규칙 적용하기

각 규칙 문서 맨 아래 **"이 규칙 적용하기"** 절차를 따른다. 공통 패턴:

1. `conventions/<규칙>.md`를 대상 repo `docs/conventions/`로 복사하고, 문서 상단 출처 줄을 **복사일**로 채운다(복사본이 낡았는지 판단용).
2. 쓰는 스택이면 `templates/<stack>/`의 config 파일을 대상 repo에 복사(설치 버전에 맞춰 조정 후 `pnpm lint`/`pnpm build` 확인).
3. 규칙 문서의 셋업 명령(라벨 생성 등)을 1회 실행.
4. 대상 repo `CLAUDE.md`(및 `AGENTS.md`)의 `## 공통 규칙` 섹션을 `templates/CLAUDE.snippet.md`로 채운다.

> **왜 이 방식인가 (에이전트 참조 관점):** 진입 파일(CLAUDE.md/AGENTS.md)은 세션 시작 시 자동으로 읽힌다.
> - **always-on 소수 규칙**(검증 게이트·커밋·자동생성물 금지 등)은 CLAUDE.md에 **인라인**으로 박는다 — 경로 포인터만 있으면 에이전트가 문서를 안 열 수 있다.
> - **나머지 규칙**은 포인터로 두되 **"언제 읽어라" 힌트**를 붙여 문서를 열 트리거를 준다.
> - 상세 설명·값은 `docs/conventions/` 문서와 config 파일에. 규칙이 늘면 포인터 줄만 하나씩 추가.

## 새 규칙 추가하기

### 방법 A — 원자료 일괄 import (추천)

다른 프로젝트에서 쓰던 규칙을 `inbox/`에 아무 형식으로나 모아두고, 이 repo에서 **`/import-conventions`** 실행. 주제별로 분해해 기존 규칙과 대조 후 **신규 생성/갱신**하고, README 표·CLAUDE 포인터까지 정리해준다. 자세한 건 `inbox/README.md`.

### 방법 B — 하나씩 수동

`templates/convention.template.md`를 `conventions/<이름>.md`로 복사해서 시작(골격·출처 줄·"적용하기" 포함). 상세 순서는 `CLAUDE.md`의 "새 규칙 추가하기" 체크리스트 참고. 요약:

1. 템플릿 복사 → 채우기(자기완결형: 원칙 + 셋업 + 적용법).
2. 값이 있으면 `templates/<이름>/`에 실파일 + 폴더 README(출처·기준 버전).
3. 위 "규칙 목록" 표에 한 줄, `templates/CLAUDE.snippet.md` 포인터에 한 줄 추가.

## 이동성

- 이 repo를 GitHub public repo로 두면 새 PC에서 clone/다운로드만 하면 됨 (스크립트·비밀정보 없음).
- 각 프로젝트에 복사된 규칙(`docs/conventions/*` + config 파일 + `CLAUDE.md` 포인터)은 그 repo에 커밋되므로, repo를 clone하는 어떤 PC에서든 자동으로 따라온다.
- 복사본은 원본과 **자동 동기화되지 않는다.** 복사일(출처 줄)로 낡음 여부를 판단하고, 원본이 바뀌면 필요한 repo에 다시 반영한다.
