# dev-conventions repository guidance

이 repo는 **개발 규칙의 유일한 원본(SSOT)**이다. 규칙은 프로젝트로 복사하지 않고 **환경(전역)에 설치**하며, 프로젝트에는 그 규칙이 이름으로 참조하는 **값과 사실**만 둔다.
빌드/린트/테스트가 없는 문서 repo. 설계 근거는 `docs/specs/2026-09-18-engineering-system-v2.md`이고, 아래 규칙은 이 repo에서 작업할 때 그대로 적용된다.
(이 블록은 `project/AGENTS.template.md` 패턴을 이 repo에도 적용한 dogfooding 예시다.)

## 공통 규칙

- 커밋: Conventional Commits(`type(scope): 설명`, scope는 `skills`/`enforcement`/`project`/`install`/`readme` 등).
- 규칙 문서(skill)는 **자기완결형**으로 유지한다(원칙 + 값 + 주의 한 문서에).
- 설정 값은 산문으로 풀어쓰지 말고 `project/stacks/<stack>/`·`global/enforcement/`의 **실제 파일**로 둔다. 문서에는 "왜"만.
- **프로젝트마다 달라지는 값은 규칙 본문에 적지 않는다.** 파라미터 이름으로 참조하고, 그 목록은 각 skill 맨 아래 "필요한 프로젝트 파라미터"와 `project/AGENTS.template.md`에 둔다. 키를 추가·변경하면 **같은 커밋에서** 양쪽을 고친다 — 키 이름이 전역과 프로젝트의 계약이다.
- 규칙을 추가/수정하면 `README.md`의 "규칙 목록" 표도 함께 갱신한다.
- 남겨둔 주석은 함부로 삭제하지 않는다.
- 브랜치를 파서 여러 세션에 걸치는 작업이면 `docs/handoff/<브랜치명>.md`를 남긴다(→ `global/skills/handoff/SKILL.md`). **작업 브랜치를 먼저 push하고, handoff 문서 자체는 `main`에 직접 커밋한다**(이 repo의 `docs-branch`는 `main`이다). main에서 한 세션에 끝나는 문서 작업엔 만들지 않는다.
- 작업 방식의 기본값은 **lightweight mode**다. 범위와 완료 조건이 명확하고 국소적이며 쉽게 되돌릴 수 있는 변경은 별도 spec/plan 없이 직접 처리하고, 변경 위험에 비례해 검증한다. 무거운 계획·서브에이전트 흐름은 명시적 요청이나 고위험 작업에만 승인 후 사용한다.

## 구조

```
global/        환경(전역)에 설치되는 것. 강제력 3층
  always-on.md          항상 로드되는 소수 규칙. 15줄 예산
  skills/<name>/SKILL.md  규칙 본문. `description`이 "언제 읽어라" 트리거
  skills/SKILL.template.md  새 skill 골격 (이 repo 안에서만 씀)
  enforcement/<agent>/  권한·hook 실파일. 모델이 우회 못 하는 층
project/       프로젝트에 스캐폴딩되는 것 (템플릿 + 스택 config)
install/       targets(설치 매핑) · lib/dc_install.py(설치 동작) · apply-conventions.md
inbox/         다른 프로젝트 원자료. `/import-conventions`로 정규화. 처리분은 `inbox/processed/`
docs/specs/    설계 문서
bootstrap.sh   PC마다 1회. 전역 설치 — `--dry-run`/`--check`/`--copy`/`--uninstall`
```

- `global/`은 설치되므로 **repo 밖 경로를 상대 링크로 걸지 않는다.** skill 사이 링크(`../<name>/SKILL.md`)만 설치 후에도 유효하다. repo 안의 다른 파일은 "dev-conventions의 `<경로>`"처럼 글로 가리킨다.
- `project/*.template.md`(문서 골격)은 채워진 결과물만 대상 repo에 남긴다. 템플릿 파일 자체는 복사하지 않는다.
- 전역 설정 파일(`~/.claude/settings.json` 등)을 직접 고치지 않는다. 원본을 고치고 재설치한다.

규칙 일괄 추가는 `/import-conventions`, 대상 프로젝트 적용은 `/apply-conventions`(단계 5에서 스캐폴딩으로 재작성 예정). 규칙을 새로 정의할 땐 아래 체크리스트.

## 새 규칙 추가하기 (이 순서 그대로)

1. **어느 층인지 먼저 판정한다**(설계 §4 Q2). 어기면 사고다 → `global/enforcement/`. 매 작업에 적용되고 잊으면 안 지켜진다 → `global/always-on.md`(15줄 예산 안일 때만). 특정 상황에서만 필요하거나 30줄이 넘는 절차다 → skill.
2. **맨땅에서 쓰지 말 것.** `cp global/skills/SKILL.template.md global/skills/<이름>/SKILL.md`로 시작한다. frontmatter(`name`·`description`)·섹션 순서·맨 아래 "필요한 프로젝트 파라미터"를 유지한다.
3. `description`은 목차가 아니라 **트리거**다. "…할 때" 형태로, 에이전트가 그 한 줄만 보고 열지 말지 정할 수 있게 쓴다.
4. 문체/깊이 레퍼런스: `global/skills/todo-workflow/SKILL.md`, `global/skills/coding-conventions/SKILL.md`.
5. 값/설정이 있으면 산문 말고 실파일로: 스택 config는 `project/stacks/<이름>/` + 그 폴더 `README.md`(출처·기준 날짜/버전), 권한·hook은 `global/enforcement/`. 실 프로젝트에서 가져왔으면 byte-identical 스냅샷으로.
6. 새 파라미터를 참조하면 `project/AGENTS.template.md`에 같은 커밋으로 줄을 추가한다.
7. `README.md`의 "규칙 목록" 표에 한 줄 추가.

## Provider entrypoints

- `AGENTS.md`를 저장소 지침의 유일한 원본으로 사용한다.
- `CLAUDE.md`, `GEMINI.md`, `.agents/rules/repository.md`는 `AGENTS.md`를 참조하는 얇은 provider 어댑터로 유지하고 공통 지침을 중복하지 않는다.
- 특정 provider에서만 동작하는 지침은 공통 지침으로 표현할 수 없을 때만 해당 provider 디렉터리에 두고, provider 전용인 이유를 문서화한다.
