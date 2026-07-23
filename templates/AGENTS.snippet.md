<!--
대상 repo의 AGENTS.md에 아래 "## 공통 규칙" 블록을 병합한다.
- always-on 항목: 경로만 두면 에이전트가 문서를 안 열 수 있으므로, 매 작업에 적용되는 소수 규칙은 여기 인라인으로 박아둔다.
- 포인터 항목: "언제 읽어라" 힌트를 함께 둬서 에이전트가 문서를 열 트리거를 준다.
- CLAUDE.md, GEMINI.md, .agents/rules/repository.md는 AGENTS.md를 참조하는 얇은 어댑터로 유지한다.
- 규칙이 늘면 포인터 줄만 하나씩 추가한다.
-->
## 공통 규칙

<!-- always-on: 아래는 매 작업에 그대로 적용된다 -->
- 작업 방식의 기본값은 **lightweight mode**다. 범위와 완료 조건이 명확하고 국소적이며 쉽게 되돌릴 수 있는 변경은 별도 spec/plan·워크트리·서브에이전트 없이 직접 처리한다.
- 검증 게이트: "통과/완료"를 보고하기 전에 변경 위험에 비례한 관련 검증을 **실제로 실행**하고 결과를 확인한다. 전체 build·typecheck·lint는 영향 범위가 넓거나 저장소 지침이 요구할 때 실행한다.
- 커밋: Conventional Commits(`type(scope): 설명`). **커밋은 사람이 요청할 때만.** pre-commit 훅 우회(`--no-verify`) 금지.
- 패키지 매니저는 **pnpm**으로 통일.
- 자동 생성 파일(라우트 트리·스키마 gen 산출물 등)은 **직접 수정하지 않는다.**
- 남겨둔 주석은 함부로 삭제하지 않는다.

<!-- on-demand: 아래 상황이면 해당 문서를 열어본다 -->
- 코딩 컨벤션(lint·포맷·스택별 tsconfig 등 자세한 값): docs/conventions/coding-conventions.md
- TODO 관리 대상(적용 시 실제 값으로 치환): GitHub Issues `<owner/repo>` · Project `<project-owner>/<project-number>` (`<Project title>`)
- TODO/백로그를 만들거나 상태를 바꿀 때, 또는 무거운 항목을 spec/plan으로 올릴지 판단할 때: `docs/conventions/todo-workflow.md`를 먼저 읽고 **md → GitHub Issue → Project Status를 같은 턴에 함께 갱신한다**. Issue 라벨만 바꾸고 Project가 따라왔다고 가정하지 않는다.
- 풀스택 병렬 진행·작업 격리(워크트리)·가벼운 실행 등 작업 방식: docs/conventions/agent-workflow.md
