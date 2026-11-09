# rawtolaw 계획 A(#001 기반과 수집·미러)에서 나온 후보 3건 — 2026-10-21

출처: rawtolaw 저장소, to-do #001(브랜치 `todo/001-plan-a-foundation-ingest`, 병합 `59b3875`). 셋 다 이 작업에서 실제로 밟은 것이다.

## 1. docker Postgres를 `pg_isready`로 기다리면 너무 일찍 통과한다 (deployment · 로컬 DB 기동 절차)

**관찰:** 계획대로 `docker compose up -d db` 뒤 `until pg_isready …; do sleep 1; done`으로 기다렸다. 루프가 곧바로 빠져나왔는데, 이어서 실행한 `psql`은 `FATAL: the database system is shutting down`으로 실패했다. postgres 이미지의 entrypoint는 `docker-entrypoint-initdb.d` 스크립트를 돌리려고 **임시 서버를 띄웠다가 내리고** 본 서버를 다시 띄운다. `pg_isready`는 그 임시 서버에도 "accepting connections"로 응답한다. 같은 문제가 `law` 저장소에서도 있었는지는 확인하지 않았다.

**후보 규칙:** 로컬·CI에서 postgres 컨테이너가 준비됐는지 볼 때는 `pg_isready`가 아니라 **실제 쿼리**로 기다린다. 예: `until docker compose exec -T db psql -U <user> -d <initdb가 만드는 DB> -tAc 'select 1' >/dev/null 2>&1; do sleep 1; done`. initdb 스크립트가 만드는 DB에 붙어야 init이 끝났다는 게 보장된다. compose `healthcheck`의 `pg_isready`도 같은 함정이 있다.

## 2. 오래 걸리는 작업이 브랜치에서 돌 땐 그 clone에서 브랜치를 바꾸지 않는다 — main 문서는 임시 워크트리로 (handoff · agent-workflow) — `2026-10-19-dub-004-lessons.md` 1번의 두 번째 관찰

**관찰:** 작업 브랜치에서 실데이터 수집(약 51분, 단계마다 `uv run`으로 새 프로세스)을 백그라운드로 돌리는 중에, 사용자 결정을 main의 handoff·to-do에 바로 적어야 했다. 원래 clone에서 `git switch main`을 하면 main엔 아직 없는 엔진 코드가 작업 트리에서 사라진다. 그러면 다음 단계 프로세스가 import에 실패한다. 그래서 main을 scratchpad 임시 워크트리로 띄워 거기서 커밋·push하고 머지까지 마친 뒤 `git worktree remove`로 지웠다. 지운 다음에야 원래 clone을 main으로 바꿀 수 있었다(dub 1번과 같은 "main이 묶인다" 현상).

**후보 규칙(dub 1번에 덧붙일 것):** "원래 clone은 main, 작업 브랜치는 워크트리" 배치를 기본으로 한다. 이번처럼 원래 clone에서 브랜치 작업 중에 **장기 실행 프로세스가 작업 트리를 읽고 있으면** 그 clone의 체크아웃을 바꾸지 않는다. main 문서는 임시 워크트리에서 커밋하고, 끝나면 바로 `git worktree remove`한다. 장기 실행을 시작하기 전에 "그동안 main 문서를 어디서 고칠지"를 정해 둔다.

## 3. `Read(.env*)` 거부 규칙이 `.env.example`까지 막는다 (harness-engineering · 권한 설정)

**관찰:** 템플릿 `engine/.env.example`(실제 키 없음, 이름과 로컬 기본값만)의 포트를 고치려 하자 Bash `sed -i`와 Write 도구가 모두 거부됐다("File is covered by a Read deny rule"). 결국 사용자가 `!` 명령으로 직접 고쳤다. 처음 만들 때 `cp`는 통과했다. 그래서 같은 파일이 경로마다 다르게 취급됐다(우회로가 되므로 그 뒤로는 쓰지 않았다).

**후보 규칙:** 비밀값 보호 deny는 `.env`, `.env.*`를 막되 `.env.example`·`.env.sample`은 예외로 두는 패턴을 harness 기본값으로 검토한다(가능하면 allow로 덮는다). 예외를 두지 않으면 에이전트가 템플릿을 관리할 수 없다. 관리하지 못하는 템플릿은 실제 설정과 어긋난다. 반대로 예외를 둘 수 없는 환경이라면, 프로젝트 문서에 "`.env.example`은 사람이 고친다"를 명시한다(rawtolaw는 계획 문서에 적었다).
