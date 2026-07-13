# CLAUDE.md — dev-conventions

이 repo는 여러 프로젝트에 공통으로 복사해 쓰는 **개발 규칙 원본(SSOT)** 모음이다.
빌드/린트/테스트가 없는 문서 repo. 아래 규칙은 이 repo에서 작업할 때 그대로 적용된다.
(이 블록은 `templates/CLAUDE.snippet.md` 패턴을 이 repo에도 적용한 dogfooding 예시다.)

## 공통 규칙

- 커밋: Conventional Commits(`type(scope): 설명`, scope는 `todo`/`coding`/`readme`/`templates` 등). **커밋은 사람이 요청할 때만.**
- 규칙 문서는 **자기완결형**으로 유지한다(원칙 + 셋업 + 적용법 한 문서에).
- 설정 값은 산문으로 풀어쓰지 말고 `templates/<stack>/`의 **실제 파일**로 둔다. 문서에는 "왜"만.
- 규칙을 추가/수정하면 `README.md`의 "규칙 목록" 표와 포인터도 함께 갱신한다.
- 남겨둔 주석은 함부로 삭제하지 않는다.

## 구조

- `conventions/*.md` — 규칙 원본. 각 문서 맨 아래 "이 규칙 적용하기" 절차 포함.
- `templates/` — 대상 repo로 복사하는 실파일(config 스캐폴딩, CLAUDE 스니펫, 문서 템플릿).
- `inbox/` — 다른 프로젝트 원자료를 모아두는 곳. `/import-conventions`로 분석·정규화(→ `.claude/commands/import-conventions.md`). 처리분은 `inbox/processed/`로 이동.
- `README.md` — 규칙 목록 + 적용/추가 방법.

규칙 일괄 추가는 `/import-conventions`(방법 A), 하나씩은 아래 체크리스트(방법 B).

## 새 규칙 추가하기 (이 순서 그대로)

1. **맨땅에서 쓰지 말 것.** `cp templates/convention.template.md conventions/<이름>.md`로 시작한다. 섹션 순서·상단 출처 줄·맨 아래 "이 규칙 적용하기"를 유지한다.
2. 문체/깊이 레퍼런스: 기존 `conventions/todo-workflow.md`, `conventions/coding-conventions.md`.
3. 값/설정이 있으면 산문 말고 `templates/<이름>/`에 **실파일** + 그 폴더 `README.md`(출처·기준 날짜/버전). 실 프로젝트에서 가져왔으면 byte-identical 스냅샷으로.
4. `README.md`의 "규칙 목록" 표에 한 줄 추가.
5. `templates/CLAUDE.snippet.md`에 포인터 추가 — **매 작업에 적용되면** always-on 블록에 인라인, **특정 상황에만이면** on-demand에 "언제 읽어라" 힌트와 함께.
