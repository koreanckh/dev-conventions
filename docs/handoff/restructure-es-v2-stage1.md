# Handoff: restructure/es-v2-stage1

- **갱신:** 2026-09-18 12:15 · home
- **브랜치:** restructure/es-v2-stage1 (base: main) · 커밋 13개, origin에 push됨
- **워크트리:** 없음
- **TODO:** 없음 (이 repo는 to-do 체계 미적용)
- **먼저 읽을 것:** `docs/specs/2026-09-18-engineering-system-v2.md` §11(적용 단계) · §13(가정 판정 기록) · `README.md`의 "설치와 제거"

## 다음 한 수

**단계 6의 진짜 절반** — 다른 PC에서 clone + `./bootstrap.sh`(계정 프로필마다). 소요 시간과 사람 손이 몇 번 가는지 잰다. 그게 끝나면 이 브랜치를 main에 병합할 수 있다(병합 때 이 파일 삭제 + 승격 트리거 질문).

## 지금 상태

- 단계 1~5·7 완료, 6은 메커니즘만 검증(다른 기계 미검증).
- 전환된 프로젝트 3개 전부 push — nowhere `615a66f` · bus `c398575` · mulzipsa `ac56ea8`. 복사본 13 → 0.
- **첫 승격 완료:** `refactoring-principles` → 전역 skill. nowhere 원본은 판정만 남기게 줄였다(128 → 47줄) — **nowhere 쪽은 스테이징만 하고 커밋 안 함**(그 저장소 규칙: 커밋은 사람이 요청할 때만).
- 보류 후보 `external-request-discipline`은 `inbox/held-*.md`에 조건·승격안과 함께 살아 있다.
- 설치: 프로필 5개 전부 최신(skill 8개). 단계 2 검증 (a) — 새 세션에서 always-on 로드 — 도 확인됐다.
- 범위 밖 복사본: `blog`(3) · `law`(6).

## 이미 해봤고 안 된 것

- `install/targets`에 `legacy_section = ## Superpowers policy`를 따옴표 없이 썼더니 configparser가 `#`을 인라인 주석으로 먹어 빈 값이 됐다 → `#`으로 시작하는 값은 큰따옴표로 감싼다(파서가 벗겨낸다).
- 첫 `--uninstall`이 codex에서 크래시했다. `managed["settings"]`가 항상 `{permissions:{},hooks:{}}`라 truthy → `config.toml`을 JSON으로 파싱하려 했다. 확장자로 분기하고 빈 dict는 `{}`로 정리해 고쳤다.
- `--copy` 모드 재실행이 복사본을 갱신하지 않았다(실디렉터리는 무조건 건너뜀). lock에 기록된 우리 설치분이면 해시 비교 후 교체하도록 고쳤다.

## 대화에서만 나온 결정

- 세 프로젝트 **전부** to-do 번호를 자체 배정하고 있었다(이슈 번호와 불일치) → 전부 `todo-numbering: local` + 결정 기록. 전역 기본값(`issue`)이 실제로는 어느 저장소에서도 안 쓰이고 있다 — 기본값을 바꿀지는 별개 판단으로 남겨 둔다.
- bus의 Python(`bus-data`) 검증은 `verify`에서 **뺐다**(ruff·mypy 미설치, 전용 venv 없음). 빠진 사실과 수동 실행법을 스크립트 주석에 적었다.
- mulzipsa의 `verify-all.sh`는 **부작용이 있다** — 앱 검증이 추적 파일(`ios/Flutter/*.xcconfig`)을 다시 쓴다. AGENTS.md에 되돌리라고 적어 뒀다.

- nowhere의 handoff 형태(`docs/agent/` 통합본 + to-do 갈래별, 끝나도 유지)는 **사용자가 의도한 것**이라고 확인했다 → 결정 기록 002로 남겼다. 전역 기본형으로 "고치려" 들지 말 것.
- nowhere의 과거 to-do·spec·plan 안의 옛 `docs/conventions/*` 링크는 **고치지 않았다.** 그 시점 기록이라서. 대신 `docs/conventions/README.md`에 "없어진 경로 → 지금 읽을 것" 표를 뒀다.

- Claude 설정 디렉터리 2개(`~/.claude`, `~/.claude-personal`) **둘 다** 설치하기로 했다(사용자 선택). skills·commands는 심링크로 공유돼 물리적으론 한 벌이다.
- `~/.codex/AGENTS.md`의 Superpowers policy는 설계대로 관리 구역으로 대체했다. 다만 "어떤 skill을 언제 안 쓰나" 구체 목록은 always-on 2줄로 압축되면 손실이라, `agent-workflow` skill에 절을 만들어 보존했다. **Codex에서 lightweight mode가 약해졌다고 느끼면 이 결정을 먼저 의심한다**(백업: `~/.codex/AGENTS.md.bak-20260918-092353`).
- `--check`의 SessionStart hook 자동 배선(§7.5 호출 지점 2)은 **하지 않았다.** 전역 hook은 외부 도구 관리 구역이라 항목을 더 얹기 전에 §13 가정 4가 시간으로 검증되길 기다린다. 지금은 수동 `./bootstrap.sh --check`만.

## 검증 상태

- 단계 6 부분 검증: 새 clone + 가짜 HOME으로 설치 전 과정 확인(심링크·hook이 clone 경로를 가리킴, 재실행 0건, 없는 에이전트 건너뜀, `--check` 0). **남은 미검증분은 "다른 기계"뿐이다.**

- dev-conventions: `./bootstrap.sh` 재실행 변경 0건, `--check` 0. 설치 표면 해시 방식이라 문서 커밋으로는 낡음이 뜨지 않는다.
- nowhere: `./scripts/check` 통과(커밋 직전 재실행). 전역 규칙 복사본 5 → 0.
- 아직 안 돌림: **새 세션에서 에이전트가 `verify`를 스스로 찾아 실행하는가**(§11 단계 3 검증의 핵심). 이 세션은 그 파일을 직접 쓴 세션이라 증거가 못 된다.
- 미판정: §13 가정 3(Gemini CLI 미설치) · 가정 6(프로젝트 allow와 전역 deny/ask 합성 — nowhere `.claude/settings.json`을 깔아뒀으니 다음 nowhere 세션에서 관찰 가능).

## 환경 (PC 간)

- 필요 도구: bash, git, python3(3.11+ — `tomllib`). 외부 서비스·secret 없음.
- 다른 PC에서는 clone 후 `./bootstrap.sh --dry-run`으로 먼저 본다. 설정 디렉터리가 없는 에이전트는 자동으로 건너뛴다.
