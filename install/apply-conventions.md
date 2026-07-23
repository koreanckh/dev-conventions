---
description: dev-conventions 레포의 규칙을 현재 프로젝트에 복사·병합해 적용한다
---

# /apply-conventions $ARGUMENTS

dev-conventions 레포의 규칙을 **현재 작업 중인 프로젝트**(cwd)에 적용한다. 규칙은 대상 repo로 복사되어 커밋되므로, 이후 어느 PC에서 clone해도 따라온다.

## 소스 레포 경로 결정 (이 순서)

1. 인자 `$ARGUMENTS`가 있으면 그 경로.
2. 환경변수 `$DEV_CONVENTIONS_DIR`.
3. 기본값 `{{DEV_CONVENTIONS_DIR}}` (이 커맨드를 설치한 `bootstrap.sh`가 감지해 넣은 경로).

결정된 경로가 없거나 존재하지 않으면 멈추고 사용자에게 알린다. 이하 이 경로를 `<SRC>`로 표기한다.

## 절차

1. **문서 복사** — `mkdir -p docs/conventions`. `<SRC>/conventions/*.md`를 `docs/conventions/`로 복사하고, 각 파일 상단 출처 줄을 `> 출처: dev-conventions · 복사 <오늘 날짜>`로 바꾼다. 대상에 같은 파일이 이미 있으면 덮기 전에 diff를 보여주고 확인한다.
2. **스택 감지 + config 복사** — 대상 `package.json`의 deps로 스택을 판별한다:
   - `@nestjs/*` → `<SRC>/templates/nestjs/`
   - `vite` + `react` → `<SRC>/templates/vite-react/`
   - `next` → `<SRC>/templates/next/`
   판별 결과를 사용자에게 확인한 뒤 해당 폴더의 config 파일만 프로젝트 루트로 복사한다(폴더 `README.md`는 제외). **기존 config가 있으면 덮지 말고** diff를 보여주고 물어본다. 안 쓰는 스택 config는 넣지 않는다.
3. **공통 지침 + provider 진입점 구성**
   - `<SRC>/templates/AGENTS.snippet.md`의 `## 공통 규칙` 블록을 대상 `AGENTS.md`에만 병합한다. 파일이 없으면 생성하고, 같은 섹션이 있으면 **중복 줄 없이** 병합한다.
   - TODO 관리 대상 줄의 `<owner/repo>`, `<project-owner>`, `<project-number>`, `<Project title>`은 git remote와 실제 GitHub Project 조회 결과로 치환한다. placeholder를 남기거나 Project를 추측하지 않는다.
   - `CLAUDE.md`와 `GEMINI.md`는 `@./AGENTS.md`, `.agents/rules/repository.md`는 `@../../AGENTS.md`를 참조하는 얇은 진입점으로 구성한다.
   - 기존 진입점에 provider 전용 지침이나 다른 내용이 있으면 보존한다. 공통 지침이 중복되어 있거나 얇은 진입점으로 바꾸려면 먼저 diff를 보여주고 확인한다.
4. **1회 셋업** — 적용한 규칙 문서의 "이 규칙 적용하기"에 셋업 명령이 있으면 실행 여부를 물어본 뒤 실행한다. `<owner/repo>`는 대상 repo의 git remote에서 채운다. TODO 규칙은 라벨 생성만으로 끝내지 않는다.
   - GitHub Project의 owner/title/number를 확인하고 대상 `AGENTS.md`의 TODO 관리 대상 줄에 영구 기록한다. CLI가 Project를 못 읽으면 `gh auth refresh -s project` 승인을 안내한다.
   - Project `Workflows`의 Auto-add가 대상 repository + `is:issue` 필터로 `On`인지 사용자에게 확인받는다. `Item added → Todo`, `Item closed → Done`, `Item reopened → Todo`도 확인한다.
   - 기존 Issue는 Auto-add가 소급하지 않으므로 `gh issue edit <N...> --add-project "<Project title>"`로 넣는다.
   - `gh issue list --json number,state,labels,projectItems`로 실제 Project 소속과 Status를 검증한다. Issue 라벨과 Project Status가 별개임을 명시한다.
5. **리포트** — 복사/병합/provider 진입점/라벨 셋업/Project Auto-add/기존 Issue 반영/Status 검증 결과를 구분해 요약한다. Project 권한이나 UI 설정 때문에 확인하지 못한 단계는 완료로 보고하지 말고 정확한 blocker를 적는다.

## 원칙

- 기존 파일 덮어쓰기·`gh` 같은 외부 명령 실행 전에는 **반드시 확인**한다.
- 쓰는 스택 config만 넣는다.
- `AGENTS.md`를 공통 지침의 원본으로 사용하고 provider 진입점에 공통 지침을 중복하지 않는다.
- **커밋하지 않는다** (사용자가 요청할 때만).
