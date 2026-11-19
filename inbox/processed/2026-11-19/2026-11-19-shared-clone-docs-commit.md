# 후보 1건 — ness #141에서 관찰 (2026-11-19)

## 여러 세션이 같은 작업 트리를 쓰는 저장소에서는 `docs-branch` 문서 커밋을 전용 워크트리에서 하고, 커밋 직전에 브랜치와 스테이징을 확인한다

관찰: 같은 clone(`~/dev/ness`)을 Claude 세션 둘이 동시에 쓰고 있었다.

- 세션 B가 워크플로 이름을 정리하려고 그 clone에서 `git switch -c chore/workflow-names`를 하고 파일 7개를 스테이징해 두었다.
- 세션 A는 그 clone이 계속 main이라고 믿고 to-do를 고쳐 `git add docs/to-do/141-….md && git commit`을 했다.
- `git commit`은 인덱스 전체를 커밋하므로, B가 스테이징해 둔 7개(워크플로 3개 삭제 포함)가 A의 to-do 커밋 메시지로 B의 브랜치에 커밋됐다. A의 to-do 수정은 빠졌다.
- 신호는 있었다. 직전의 `git pull --ff-only`가 `There is no tracking information for the current branch`로 실패했다. 그런데 커밋이 다음 줄이라 `&&`로 묶이지 않아 그대로 돌았다.
- push 전에 알아채서 `git reset --soft HEAD~1`로 B의 상태(스테이징 그대로)를 되돌렸다. 그 뒤 A는 scratchpad에 `git worktree add <scratchpad>/ness-main origin/main`으로 전용 작업 트리를 만들어 to-do 커밋을 그쪽에서만 했고, 같은 날 열 번 넘게 커밋하는 동안 다시 섞이지 않았다.

규칙(handoff 스킬 「`docs-branch` 문서를 어디서 고치나」에 들어갈 자리):

- **여러 세션이 같은 clone을 쓰면 그 clone의 HEAD·인덱스를 믿지 않는다.** 다른 세션이 언제든 브랜치를 바꾸거나 스테이징해 둘 수 있다. 지금 기본 배치(「원래 clone = `docs-branch`, 문서는 원래 clone에서 고친다」)가 이 경우엔 깨진다.
- `docs-branch` 문서는 그 세션 전용 임시 워크트리에서 고치고 커밋·push한다(`git worktree add <scratchpad>/<repo>-docs origin/<docs-branch>`, push는 `HEAD:<docs-branch>`). 끝나면 `git worktree remove`.
- 커밋 직전에 `git branch --show-current`와 `git diff --cached --name-status`가 예상(브랜치 이름, 내가 고친 파일만)과 같은지 확인하고, 다르면 멈춘다. rename은 `--name-only`에 새 경로만 나오므로 `--name-status`로 본다.
- 경로를 지정해 커밋하면(`git commit -- <경로>`) 인덱스의 다른 변경이 섞이지 않는다.

같이 본 반대쪽 원인(별도 후보로 다룰지 심사 때 판단): 세션 B가 공용 clone에서 `git switch -c`를 해서 모든 세션의 HEAD가 함께 옮겨졌다. 코드 브랜치 작업은 처음부터 워크트리에서 하고, 공용 clone은 `docs-branch`에 두는 쪽(agent-workflow 「작업 격리」)이 짝이다.

재사용 이유: 한 저장소에 세션 여럿(Orca 워크트리, 병렬 Claude/Codex)을 붙이는 일이 흔해졌다. 「to-do·handoff는 `docs-branch`에 직접 커밋」 규칙이 있는 모든 저장소에서, 공용 clone에서 커밋하는 한 같은 섞임이 생긴다.

## 처리 (2026-11-19)

- 규칙 4줄: handoff 「`docs-branch` 문서를 어디서 고치나」에 불릿 2개로 넣었다(공용 clone이면 세션 전용 워크트리 · 커밋 직전 브랜치·스테이징 확인). 워크트리는 `--detach`로 띄우게 적었다 — 같은 절의 「임시 워크트리를 남기면 `git switch main`이 막힌다」와 충돌하지 않게.
- 같은 절의 「이때만 임시 워크트리」는 경우가 둘이 돼 「이때는」으로 풀었다. `pull` 불릿에는 `no tracking information` 실패가 신호였다는 한 문장을 덧붙였다.
- 반대쪽 원인(공용 clone에서 `git switch -c`): 별도 후보로 빼지 않고 agent-workflow 「작업 격리」에 한 줄로 넣었다.
