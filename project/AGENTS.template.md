<!--
대상 프로젝트의 `AGENTS.md` 골격. `/apply-conventions`가 이 형태로 스캐폴딩한다.
- **규칙 본문을 여기에 복사하지 않는다.** 규칙은 환경에 설치돼 있고(dev-conventions `global/`), 여기엔 그 규칙이 이름으로 참조하는 **값**만 둔다.
- 각 파라미터 줄은 **혼자 읽혀도 뜻이 통하게** 쓴다(값 + 한 구절). 전역 설치가 없는 환경(클라우드 세션·협업자)에서도 이 줄만 보고 무엇을 해야 하는지 알 수 있어야 한다.
- 목표 ~30줄, 상한 100줄. 넘으면 사실 문서(`docs/`)로 내린다.
- 쓰지 않는 파라미터 줄은 지운다. 값을 모르면 추측해 채우지 말고 비워두고 묻는다.
- 채울 때 이 주석 블록은 지운다.
-->

# <프로젝트명>

<한 문단: 이 프로젝트가 무엇인가. 자세한 건 README.md / docs/architecture.md로.>

## 프로젝트 파라미터

- stack: <예: nestjs + vite-react>
- package-manager: <예: pnpm>
- verify: <예: ./scripts/check> — 완료를 보고하기 전에 실행한다
- verify-quick: <예: pnpm typecheck> — 작은 변경용(선택)
- generated: <예: src/routeTree.gen.ts, prisma/generated/**> — 직접 수정하지 않는다
- issues: github:<owner/repo>
- board: github-project:<project-owner>/<project-number> (`<Project title>`)
- todo: docs/to-do/ — 상태 SSOT. 완료분은 `done/`
- todo-numbering: <issue | local> — `issue`면 GitHub 이슈 번호를 그대로 쓴다(기본). `local`이면 저장소가 자체 배정하며 이유를 `decisions`에 남긴다
- decisions: docs/decisions/ — 기존 결정. 뒤집기 전에 읽는다
- handoff: docs/handoff/ — 브랜치당 1개. 병합 시 삭제
- ops: <예: DEPLOY.md> — 배포·운영(선택)
- commit-types: <예: feat, fix, chore, refactor, style, docs, wip> — 이 저장소에서 쓰는 Conventional Commits type
- worktree: <생략 | never> — `never`면 이유를 `decisions`에 남긴다

<!-- 완료 기준처럼 이 프로젝트에서만 참인 규칙은 아래에 한 줄씩. 전역 규칙을 다시 쓰지 않는다. -->

## 이 프로젝트만의 규칙

- 완료 기준: <예: `dev` 머지 + `origin/dev` push까지>

## 사실 문서

- 구조·설계: <README.md / docs/architecture.md>
- 결정 기록: docs/decisions/
- 운영: <ops 경로>
