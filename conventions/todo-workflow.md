# TODO 관리 워크플로

> 원본(SSOT): dev-conventions. 대상 repo로 복사할 땐 이 줄을 `> 출처: dev-conventions · 복사 YYYY-MM-DD`로 바꿔 남긴다(복사본이 낡았는지 판단용).

`docs/to-do/*.md`(SSOT) + GitHub Issues(미러) + Projects 보드로 to-do/백로그를 관리하는 규칙. **번호는 GitHub 이슈 번호를 그대로 쓴다**(3자리 zero-pad: 이슈 `#7` → `#007`). 한 항목에 번호가 두 개 존재하지 않게 하려는 것이다.
에이전트는 TODO 작업을 수행하는 같은 흐름에서 **md → Issue → Project** 순서로 세 곳을 함께 갱신한다.
`<owner/repo>`, `docs/to-do` 같은 값만 프로젝트에 맞게 바꿔 쓴다.

## 원칙

- **SSOT = repo 안의 md 파일** (`docs/to-do/*.md`). GitHub Issues는 칸반/Projects용 **미러**일 뿐이다.
- **1 주제 = 1 파일 = 1 이슈.** 관련된 것끼리 묶고, 서로 `참고` 링크로 연결한다.
- **번호 = GitHub 이슈 번호.** 직접 배정하지 않는다. 이슈를 먼저 만들어 GitHub가 준 번호를 3자리 zero-pad해서 쓴다(이슈 `#7` → `#007`). 이슈 번호는 PR과 시퀀스를 공유하므로 **미리 예측하지 않는다** — `docs/to-do/`의 마지막 번호 +1로 찍으면 경쟁 상태로 어긋난다.
- 번호는 파일명(`007-<주제>.md`), 문서 제목(`# TODO #007: <제목>`), GitHub 이슈 제목(`[ #007 ] <제목>`)에 동일하게 기록한다. zero-pad는 파일 정렬용이고, 1000번을 넘으면 자릿수는 자연스럽게 늘어난다(`1004-<주제>.md`).
- 번호는 듬성듬성해진다(PR이 사이 번호를 가져간다). 연속이 아닌 게 정상이며 빈 번호를 메우지 않는다. 완료 항목의 번호도 재사용하지 않는다(GitHub가 보장).
- **2026-08-19 이전에 만든 항목은 번호가 이슈 번호와 어긋날 수 있다.** 소급해서 다시 번호를 매기지 않는다(파일명·이슈 본문·상호 링크가 전부 깨진다). 기존 항목은 그대로 두고 신규 항목부터 일치시킨다.
- 최상위 `docs/to-do/`엔 **남은 일만** 둔다. 완료되면 `docs/to-do/done/`으로 이동한다(날짜는 파일명이 아니라 파일 안에).
- 예정에 없던 후속 작업이 생기면 그 자리에서 새 to-do(md + 이슈)로 남긴다.
- 매 작업마다 **md, Issue 본문/라벨/열림 상태, Project 소속/Status를 같은 턴에** 최신 상태로 유지한다.
- Issue 라벨과 Project의 `Status` 필드는 별개다. Auto-add는 Issue를 Project에 넣을 뿐 `status:*` 라벨을 `Todo / In Progress / Done`으로 자동 변환하지 않는다.
- 대상 repo의 `AGENTS.md`에 Issue repo와 Project owner/number/title을 실제 값으로 기록한다. 에이전트가 Project를 이름으로 추측하게 두지 않는다.
- **완료 기준은 프로젝트마다 명시적으로 정한다.** 예: "`dev` 브랜치 머지 + `origin/dev` 푸시까지"를 완료로 보고 main 머지/운영 배포는 to-do 라이프사이클과 분리. 완료 처리 시 md 표기("머지 대기" 등)를 믿지 말고 **실제 git 상태로 검증**한다(예: `git log origin/dev..dev`가 비었는지).

## to-do md 파일 템플릿

`docs/to-do/<NNN>-<주제>.md`(`NNN` = 이슈 번호) — 대상 repo에서는 아래 골격이 정본이다(이 문서가 함께 복사된다). dev-conventions 안에서 바로 복사해 쓸 실파일은 `templates/todo-file.template.md`이며, 대상 repo의 `docs/to-do/`에는 두지 않는다(최상위엔 남은 일만).

```markdown
# TODO #000: <제목>

- **번호:** #000 (= GitHub 이슈 번호, 3자리 zero-pad)
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

번호를 GitHub에서 받아와야 하므로 **이슈를 먼저 만든다.** 내용의 SSOT는 여전히 md이고, GitHub가 맡는 건 발번뿐이다. 아래 1~4는 **같은 턴에 끝낸다** — `draft-` 파일이 커밋에 남으면 안 된다.

1. **초안 작성** — `docs/to-do/draft-<주제>.md`에 템플릿대로 내용을 채운다. 번호 자리(`#000`)와 `이슈:` 줄은 비워둔다.
2. **이슈 생성 → 번호 획득** — 제목엔 아직 번호를 넣지 않는다(번호를 모르는 상태다).
   ```sh
   # Project 접근이 처음이면 먼저: gh auth refresh -s project
   URL=$(gh issue create --repo <owner/repo> \
     --title "<제목>" \
     --body-file docs/to-do/draft-<주제>.md \
     --label "status:대기" --label "priority:<상|중|하>" \
     --project "<Project title>")
   N=${URL##*/}                  # 이슈 번호 (예: 7)
   NNN=$(printf '%03d' "$N")     # 파일·문서 표기 (예: 007)
   ```
3. **번호 확정** — 파일을 rename하고 md 안의 번호를 채운다.
   ```sh
   mv docs/to-do/draft-<주제>.md "docs/to-do/$NNN-<주제>.md"   # draft는 보통 아직 untracked라 git mv가 아니다
   ```
   - 제목: `# TODO #$NNN: <제목>`
   - `번호:` `#$NNN`
   - `이슈:` `[<owner/repo>#$N](https://github.com/<owner/repo>/issues/$N) (미러 / 이 파일이 SSOT)`
4. **이슈에 반영** — 제목에 번호 접두사를 붙이고, 본문을 확정된 md로 덮어쓴다.
   ```sh
   gh issue edit "$N" --repo <owner/repo> --title "[ #$NNN ] <제목>"
   { printf '> **SSOT:** `docs/to-do/%s-<주제>.md` (이 이슈는 미러)\n\n' "$NNN"; \
     cat "docs/to-do/$NNN-<주제>.md"; } \
     | gh issue edit "$N" --repo <owner/repo> --body-file -
   ```

## 상태 전환 (항상 md → Issue → Project 순서)

| 단계 | md | GitHub Issue | Project Status |
|---|---|---|---|
| 등록/대기 | `상태: 대기` | 라벨 `status:대기`, open | `Todo` |
| 착수 | `상태: 진행` | 라벨 `status:진행`, open | `In Progress` |
| 진행 중 | 체크박스 `- [x]` + 진행 근거 갱신 | Issue 본문도 최신 md로 갱신 | `In Progress` |
| 완료 | 체크박스 전부 `[x]` + `상태: 완료 (날짜)` → 파일을 `done/`으로 이동 | 본문 경로를 `done/`으로 갱신 + `status:완료` + close | `Done` |

## GitHub Project 연결과 Status

### Project 1회 셋업

1. Project의 `Workflows` → `Auto-add to project`에서 대상 repository를 선택하고 필터를 `is:issue`로 설정한 뒤 켠다. repo의 일부 Issue만 TODO라면 전용 라벨을 만들고 `is:issue label:<전용라벨>`처럼 좁힌다.
2. 기본 workflow에서 `Item added to project → Todo`, `Item closed → Done`, `Item reopened → Todo`를 켠다.
3. Auto-add를 켜기 전에 있던 Issue는 자동 소급되지 않으므로 한 번 직접 넣는다:
   ```sh
   gh issue edit <N...> --repo <owner/repo> --add-project "<Project title>"
   ```

### 매 작업에서 에이전트가 확인할 것

- Issue 생성 시 `gh issue create --project "<Project title>"`로 Project 소속을 보장한다. Auto-add는 안전망이다.
- `대기 → 진행`처럼 Issue가 열린 채 상태만 바뀌는 경우 Project `Status`도 명시적으로 `In Progress`로 바꾼다. Issue 라벨 변경만으로 보드 컬럼이 이동했다고 가정하지 않는다.
- 완료/재오픈은 Project 기본 workflow 결과까지 확인한다.
- Project/필드 ID가 필요한 CLI 작업은 다음 조회 결과로 `gh project item-edit` 인자를 채운다:
  ```sh
  gh project view <project-number> --owner <project-owner> --format json
  gh project field-list <project-number> --owner <project-owner> --format json
  gh project item-list <project-number> --owner <project-owner> --format json
  gh project item-edit --id <item-id> --project-id <project-id> \
    --field-id <status-field-id> --single-select-option-id <status-option-id>
  ```
- 마무리 전 `gh issue view <N> --repo <owner/repo> --json state,labels,projectItems`로 Issue와 Project 상태를 함께 검증한다.

## 주의

- **이슈를 못 만들면 번호도 없다.** `gh`가 실패하거나 오프라인이면 `draft-<주제>.md`로 남기고, 번호를 임의로 찍지 않는다. 이 상태로 손을 떼야 하면 draft 경로와 미발행 사실을 보고한다(브랜치 작업이면 handoff의 `다음 한 수`에).
- `gh project` 또는 `--project`가 `not found`, `Resource not accessible`로 실패하면 프로젝트가 없다고 단정하지 말고 `gh auth refresh -s project` 후 재시도한다.
- gh 토큰이 **Issues/Projects 전용 fine-grained PAT**면 코드(Contents) API는 접근 불가하다. 코드 변경은 기존 SSH/git 경로로만.
- Project 권한이나 UI 설정 때문에 세 곳을 모두 갱신하지 못했으면 정확한 실패 명령/대상을 보고하고 동기화 완료라고 말하지 않는다.

## spec/plan 연계 (무거운 to-do)

to-do는 **무엇을·왜·됐나**의 SSOT다. **어떻게 만들지**(설계·구현 분해)는 별도로 spec/plan(brainstorming→spec, writing-plans→plan; `docs/superpowers/`)이 맡는다. to-do가 척추, spec/plan은 무거운 to-do에만 느슨하게 매달린다.

- **언제 올리나:** 사소·기계적·자명한 to-do는 spec 없이 `손봐야 할 곳` 체크박스로 바로 처리한다. 설계 결정·여러 접근·교차 관심사·리스크가 있으면 brainstorming → spec → plan → 실행으로 간다.
- **어디에:** spec/plan은 `docs/superpowers/`에 그대로 둔다. to-do 파일 밑으로 옮기지 않는다(superpowers 스킬 동작과 충돌 방지).
- **연결(양방향):** to-do의 `참고` 섹션에 spec/plan 경로를, spec 상단에 대응 to-do(`docs/to-do/007-<주제>.md`, `#007`) 링크를 남긴다.
- **생성 순서 무관:** to-do를 먼저 잡고 나중에 brainstorm해도 되고, brainstorm하다 여러 조각으로 쪼개지면 각 조각을 새 to-do로 등록해도 된다.
- **상태는 언제나 to-do에서만** 판단한다(spec/plan은 상태를 추적하지 않는다). 실행 중 세션 내 task 체크리스트는 휘발성이라 백로그 to-do와는 별개 층이다.
- **진행 중 맥락은 to-do가 아니라 handoff에** 둔다. to-do는 *무엇을·왜·됐나*의 안정적 SSOT이므로 세션 단위의 휘발성 상태(어디까지 했나·뭘 시도했다 실패했나)를 섞지 않는다 → [작업 인계](handoff.md).
- **개발 격리:** 워크트리는 to-do가 아니라 **병합 단위(plan)** 에 붙인다(에픽 to-do는 우산, 워크트리는 그 밑 plan 단위) → [에이전트 작업 규칙](agent-workflow.md)의 "작업 격리".

---

## 이 규칙 적용하기 (새 프로젝트당 1회)

**1. 파일 복사** — 이 문서를 대상 repo로 (템플릿 파일은 복사하지 않는다 — 위 "to-do md 파일 템플릿" 절이 함께 따라온다):

```sh
mkdir -p docs/conventions docs/to-do/done
cp <dev-conventions>/conventions/todo-workflow.md docs/conventions/
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

**3. Project 연결** — Project 접근 권한과 built-in workflow를 설정한다.

```sh
gh auth refresh -s project  # gh project/--project 접근이 안 될 때 1회
gh project list --owner <project-owner>
```

Project 화면의 `Workflows`에서 다음을 확인한다.

- `Auto-add to project`: 대상 repository + 필터 `is:issue`, `On`
- `Item added to project`: `Status = Todo`
- `Item closed`: `Status = Done`
- `Item reopened`: `Status = Todo`

기존 Issue는 소급 추가되지 않으므로 직접 넣고 결과를 확인한다.

```sh
gh issue edit <N...> --repo <owner/repo> --add-project "<Project title>"
gh issue list --repo <owner/repo> --state all --json number,state,labels,projectItems
```

**4. 공통 지침 포인터** — `AGENTS.md`의 `## 공통 규칙` 섹션에 "언제 읽어라" 힌트를 붙인 한 줄을 추가한다(전체 블록은 `templates/AGENTS.snippet.md`):

```markdown
- TODO 관리 대상: GitHub Issues `<owner/repo>` · Project `<project-owner>/<project-number>` (`<Project title>`)
- TODO/백로그를 만들거나 상태를 바꿀 때: docs/conventions/todo-workflow.md
```
