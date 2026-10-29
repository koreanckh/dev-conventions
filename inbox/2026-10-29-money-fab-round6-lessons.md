# money-fab 라운드 6(#009)에서 나온 후보 1건 — 2026-10-29

출처: money-fab 저장소, to-do #009·#010 등록(2026-10-29). 이 작업에서 실제로 밟은 것이다.

## `gh issue create --project`가 Projects(classic) 폐지 오류로 실패한다 — 만든 뒤 `gh project item-add` (todo-workflow)

**관찰:** todo-workflow 스킬의 "이슈 생성 → 번호 획득" 절대로 `gh issue create ... --project "Money-fab To-Do"`를 실행했더니 `error fetching repo projects (classic): GraphQL: Projects (classic) is being deprecated ... (repository.projects)`로 이슈 자체가 만들어지지 않았다(서버 chois의 gh version 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu0.3)). `--project` 없이 이슈를 만든 뒤 `gh project item-add <번호> --owner <owner> --url <이슈 URL> --format json`으로 넣으면 됐고, 돌려받은 item id로 바로 `gh project item-edit`(Status)까지 이어졌다. 이슈 #9·#10 두 번 같은 방식으로 확인했다.

**후보 규칙:** todo-workflow의 이슈 생성 예시에서 `--project`를 빼고, 생성 직후 `gh project item-add`로 Project에 넣는 두 단계로 바꾼다. `item-add --format json`의 `id`를 Status 변경에 그대로 쓰면 `item-list`로 다시 찾을 필요가 없다. gh가 classic 조회를 하지 않는 버전으로 올라가면 다시 확인한다.
