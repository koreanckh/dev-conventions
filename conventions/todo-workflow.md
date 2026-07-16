# TODO 관리 워크플로

> 원본(SSOT): dev-conventions. 대상 repo로 복사할 땐 이 줄을 `> 출처: dev-conventions · 복사 YYYY-MM-DD`로 바꿔 남긴다(복사본이 낡았는지 판단용).

`docs/to-do/*.md`(SSOT) + GitHub Issues(미러) + Projects 보드로 to-do/백로그를 관리하는 규칙.
`<owner/repo>`, `docs/to-do` 같은 값만 프로젝트에 맞게 바꿔 쓴다.

## 원칙

- **SSOT = repo 안의 md 파일** (`docs/to-do/*.md`). GitHub Issues는 칸반/Projects용 **미러**일 뿐이다.
- **1 주제 = 1 파일 = 1 이슈.** 관련된 것끼리 묶고, 서로 `참고` 링크로 연결한다.
- 최상위 `docs/to-do/`엔 **남은 일만** 둔다. 완료되면 `docs/to-do/done/`으로 이동한다(날짜는 파일명이 아니라 파일 안에).
- 예정에 없던 후속 작업이 생기면 그 자리에서 새 to-do(md + 이슈)로 남긴다.
- 매 작업마다 **md와 이슈를 함께** 최신 상태로 유지한다(보드는 이슈에서 자동 반영).
- **완료 기준은 프로젝트마다 명시적으로 정한다.** 예: "`dev` 브랜치 머지 + `origin/dev` 푸시까지"를 완료로 보고 main 머지/운영 배포는 to-do 라이프사이클과 분리. 완료 처리 시 md 표기("머지 대기" 등)를 믿지 말고 **실제 git 상태로 검증**한다(예: `git log origin/dev..dev`가 비었는지).
- **커밋은 사람이 요청할 때만.**

## to-do md 파일 템플릿

`docs/to-do/<주제>.md` (복사용 원본: 이 repo `templates/todo-file.template.md`):

```markdown
# TODO: <제목>

- **상태:** 대기 | 진행 | 완료 (YYYY-MM-DD)
- **이슈:** [<owner/repo>#N](https://github.com/<owner/repo>/issues/N) (미러 / 이 파일이 SSOT)
- **등록일:** YYYY-MM-DD
- **우선순위:** 상 | 중 | 하 (+한 줄 근거)

## 배경        # 왜 이 일이 생겼나
## 문제        # 구체적 시나리오 / 재현
## 손봐야 할 곳  # - [ ] 체크박스 액션들 (파일 경로 포함)
## 참고        # 관련 파일, 연관 to-do 링크
```

## 워크플로 (순서 중요)

1. **md 먼저 작성** (SSOT).
2. 같은 내용으로 이슈 생성:
   ```sh
   gh issue create --repo <owner/repo> \
     --title "<제목>" \
     --body-file docs/to-do/<주제>.md \
     --label "status:대기" --label "priority:<상|중|하>"
   ```
3. **양방향 참조 연결:**
   - 이슈 본문 맨 위에 SSOT 경로 추가:
     ```sh
     { printf '> **SSOT:** `docs/to-do/<주제>.md` (이 이슈는 미러)\n\n'; cat docs/to-do/<주제>.md; } \
       | gh issue edit <N> --repo <owner/repo> --body-file -
     ```
   - md의 `이슈:` 줄에 방금 만든 이슈 링크를 채운다.

## 상태 전환 (항상 md 먼저 → 이슈 맞추기)

| 단계 | md | GitHub |
|---|---|---|
| 착수 | `상태: 진행` | 라벨 `status:진행` |
| 진행 중 | 체크박스 `- [x]` 갱신 | — |
| 완료 | 체크박스 전부 `[x]` + `상태: 완료 (날짜)` → 파일을 `done/`으로 이동 | `status:완료` 라벨 + `gh issue close <N>` |

## 주의

- gh 토큰이 **Issues/Projects 전용 fine-grained PAT**면 코드(Contents) API는 접근 불가하다. 코드 변경은 기존 SSH/git 경로로만.

---

## 이 규칙 적용하기 (새 프로젝트당 1회)

**1. 파일 복사** — 이 문서와 템플릿을 대상 repo로:

```sh
mkdir -p docs/conventions docs/to-do/done
cp <dev-conventions>/conventions/todo-workflow.md docs/conventions/
cp <dev-conventions>/templates/todo-file.template.md docs/to-do/  # 원하면
```

**2. 라벨 세트 생성** — `<owner/repo>`만 바꿔 붙여넣기:

```sh
REPO=<owner/repo>
gh label create "status:대기"   --repo "$REPO" --color BFBFBF --description "대기 (다음에 진행)"
gh label create "status:진행"   --repo "$REPO" --color 1D76DB --description "진행 중"
gh label create "status:완료"   --repo "$REPO" --color 0E8A16 --description "완료"
gh label create "priority:상"   --repo "$REPO" --color D93F0B --description "우선순위 상"
gh label create "priority:중"   --repo "$REPO" --color FBCA04 --description "우선순위 중"
gh label create "priority:하"   --repo "$REPO" --color C2E0C6 --description "우선순위 하"
```

Projects 보드는 이슈 라벨(`status:*`) 기준으로 자동 유입되게 구성한다(수동 칸반이면 status 라벨 = 컬럼).

**3. 공통 지침 포인터** — `AGENTS.md`의 `## 공통 규칙` 섹션에 "언제 읽어라" 힌트를 붙인 한 줄을 추가한다(전체 블록은 `templates/AGENTS.snippet.md`):

```markdown
- TODO/백로그를 만들거나 상태를 바꿀 때: docs/conventions/todo-workflow.md
```
