# 후보: Engineering System v2 브랜치 병합 시점의 교훈 (2026-09-18)

`handoff` skill의 승격 트리거를 처음으로 실제로 돌린 결과다. 브랜치 `restructure/es-v2-stage1`의 handoff를 지우기 직전에 읽고 추렸다.

**후보가 아닌 것:** handoff의 "이미 해봤고 안 된 것" 3건(configparser `#` 인라인 주석, `--uninstall` 크래시, `--copy` 갱신 누락)은 이 저장소 설치기의 버그라 다른 프로젝트에선 뜻이 없다. 코드와 커밋에 남아 있다. 프로젝트별 결정(bus Python 제외, nowhere handoff 형태 등)은 각 저장소 `decisions`/`AGENTS.md`에 있다.

---

## A. 스테이징 규율 — `git add -A` 금지를 모든 커밋으로 넓힌다 → `coding-conventions` 후보

지금 `git add -A` 금지는 `handoff` skill의 **wip 커밋 절차에만** 있다("손을 떼는 시점은 `.env`·덤프·로그가 가장 많이 굴러다니는 순간이다"). 오늘 실패는 wip가 아니라 **평범한 작업 커밋**에서 났다.

**관찰된 실패 (3건, 저장소 2개):**
1. nowhere — `git add -A`가 사용자가 전부터 두고 있던 미추적 `scratchpad/sale-result-gap.sql`을 쓸어 담았다.
2. mulzipsa — 검증 스크립트가 flutter 툴체인으로 **새로 만든** `ios/Podfile`이 딸려 들어왔다.
3. mulzipsa — 검증이 **추적 중인** `ios/Flutter/*.xcconfig` 두 개를 다시 썼다. `-A`가 아니어도 `git add .`이면 실렸을 것이다.

셋 다 커밋 전에 잡았지만, 잡은 건 규칙이 아니라 우연히 `git status`를 본 덕이다.

**승격안 (coding-conventions의 커밋 절에 두 줄):**
- 스테이징은 **바꾼 경로를 하나씩** 적는다. `git add -A`·`git add .`를 쓰지 않는다 — 검증·빌드가 만든 산출물과 사용자가 두고 간 미추적 파일이 함께 실린다.
- **검증을 돌린 뒤에는 커밋 전에 `git status`를 다시 본다.** 검증 도구가 추적 파일을 고치는 경우가 있다. 내가 바꾸지 않은 변경이 보이면 커밋에 싣지 말고 원인을 확인한다.

**enforcement로 올릴 수 있나:** `git add -A`는 prefix 규칙으로 잡히므로 `ask`에 넣을 수 있다(`Bash(git add -A:*)`, `Bash(git add .:*)`). 다만 사람이 직접 쓰는 경우까지 매번 묻게 되니, 지침 먼저 두고 실제로 또 새면 올리는 게 `harness-engineering`의 "실패한 뒤에 추가"에 맞다.

---

## B. 하네스 도구 사실 3개 → `harness-engineering` 후보("주의 / 알려진 불일치" 절)

전부 degraded 실험(단계 4)에서 실측했다. 모델이 모르는 도구 사실이고, 모르면 잘못된 결론을 낸다.

1. **프로젝트 `.claude/settings.json`의 `permissions.allow`는 그 설정 디렉터리에서 워크스페이스를 trust하기 전까지 무시된다.** 실측 메시지: `Ignoring 6 permissions.allow entries from .claude/settings.json: this workspace has not been trusted.` → 새 환경에서 프로젝트 백스톱은 자동이 아니다. 첫 대화형 실행의 trust 수락(또는 `.claude.json`의 `hasTrustDialogAccepted`)이 필요하다.
2. **Claude Code 자격증명은 설정 디렉터리 경로별로 Keychain 항목이 갈린다**(기본은 `Claude Code-credentials`, `CLAUDE_CONFIG_DIR`을 주면 경로 해시가 붙은 별도 항목). 그래서 빈 `CLAUDE_CONFIG_DIR`로는 로그인 없이 헤드리스(`claude -p`) 실행이 안 된다. "전역 설치 없는 환경"을 흉내 내려면 인증된 프로필에서 설치분만 걷어내는 쪽이 실용적이다.
3. **always-on의 lightweight 정책이 빠지면 Superpowers의 SessionStart 주입("1% 확률이라도 skill을 불러라")이 이긴다.** 같은 과제에서 전역 설치 있는 세션은 절차 skill을 부르지 않았고, 없는 세션은 시작하자마자 `systematic-debugging`을 불렀다(n=1). 지침 파일 사이의 **우선순위 싸움은 실제로 일어나고, 빠진 쪽이 진다.**

---

## 사람이 결정할 것

- [ ] A를 `coding-conventions`에 넣을까? (권고: 예. enforcement는 보류)
- [ ] B를 `harness-engineering`에 넣을까? (권고: 예. 1·2는 도구 사실, 3은 관찰 1회라 "n=1" 표시를 달아서)
