<!--
대상 repo의 CLAUDE.md(및 AGENTS.md)에 아래 "## 공통 규칙" 블록을 그대로 붙여넣는다.
- always-on 항목: 경로만 두면 에이전트가 문서를 안 열 수 있으므로, 매 작업에 적용되는 소수 규칙은 여기 인라인으로 박아둔다.
- 포인터 항목: "언제 읽어라" 힌트를 함께 둬서 에이전트가 문서를 열 트리거를 준다.
- 규칙이 늘면 포인터 줄만 하나씩 추가.
-->
## 공통 규칙

<!-- always-on: 아래는 매 작업에 그대로 적용된다 -->
- 변경 착수 전 계획 제시 + 명시적 승인. 방법 전환도 재승인. (조사/질문답변은 예외)
- 검증 게이트: "통과/완료"를 보고하기 전에 build·typecheck·lint를 **실제로 실행**하고 결과를 확인한다. 실행 없이 완료 주장 금지.
- 커밋: Conventional Commits(`type(scope): 설명`). **커밋은 사람이 요청할 때만.** pre-commit 훅 우회(`--no-verify`) 금지.
- 패키지 매니저는 **pnpm**으로 통일.
- 자동 생성 파일(라우트 트리·스키마 gen 산출물 등)은 **직접 수정하지 않는다.**
- 남겨둔 주석은 함부로 삭제하지 않는다.

<!-- on-demand: 아래 상황이면 해당 문서를 열어본다 -->
- 코딩 컨벤션(lint·포맷·스택별 tsconfig 등 자세한 값): docs/conventions/coding-conventions.md
- TODO/백로그를 만들거나 상태를 바꿀 때: docs/conventions/todo-workflow.md
- 풀스택 병렬 진행·가벼운 실행 등 작업 방식: docs/conventions/agent-workflow.md
