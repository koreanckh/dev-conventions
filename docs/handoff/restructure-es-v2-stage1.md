# Handoff: restructure/es-v2-stage1

- **갱신:** 2026-09-18 09:55 · home
- **브랜치:** restructure/es-v2-stage1 (base: main) · 커밋 6개, origin에 push됨
- **워크트리:** 없음
- **TODO:** 없음 (이 repo는 to-do 체계 미적용)
- **먼저 읽을 것:** `docs/specs/2026-09-18-engineering-system-v2.md` §11(적용 단계) · §13(가정 판정 기록) · `README.md`의 "설치와 제거"

## 다음 한 수

nowhere에서 **새 세션**으로 작은 작업 1건을 시켜, 에이전트가 `verify`(`./scripts/check`)를 스스로 찾아 실행하는지 본다(§11 단계 3 검증). 그 다음 단계 4(degraded mode).

## 지금 상태

- 단계 1(원본 구성)·2(bootstrap + 이 PC 설치)·3(파일럿 nowhere) 완료. 단계 3의 **행동 검증 1건만 남았다**(아래 "다음 한 수").
- nowhere 커밋 `8b3a9ba` (main, **push 안 함** — 사용자가 커밋까지만 요청): AGENTS.md 파라미터화, `scripts/check`, 결정 기록 2건, 전역 복사본 5개 삭제(자생 규칙 3개 + 안내 README 유지), `.claude/settings.json`.
- nowhere `./scripts/check`: 통과 41초(node 검사 → lint → typecheck → server 1935 · web 730 · map-core 10).
- 파일럿이 전역 계약 키 2개를 요구했다 → `todo-numbering`·`commit-types` 추가, 템플릿·skill 동시 수정, 재설치 완료.

## 이미 해봤고 안 된 것

- `install/targets`에 `legacy_section = ## Superpowers policy`를 따옴표 없이 썼더니 configparser가 `#`을 인라인 주석으로 먹어 빈 값이 됐다 → `#`으로 시작하는 값은 큰따옴표로 감싼다(파서가 벗겨낸다).
- 첫 `--uninstall`이 codex에서 크래시했다. `managed["settings"]`가 항상 `{permissions:{},hooks:{}}`라 truthy → `config.toml`을 JSON으로 파싱하려 했다. 확장자로 분기하고 빈 dict는 `{}`로 정리해 고쳤다.
- `--copy` 모드 재실행이 복사본을 갱신하지 않았다(실디렉터리는 무조건 건너뜀). lock에 기록된 우리 설치분이면 해시 비교 후 교체하도록 고쳤다.

## 대화에서만 나온 결정

- nowhere의 handoff 형태(`docs/agent/` 통합본 + to-do 갈래별, 끝나도 유지)는 **사용자가 의도한 것**이라고 확인했다 → 결정 기록 002로 남겼다. 전역 기본형으로 "고치려" 들지 말 것.
- nowhere의 과거 to-do·spec·plan 안의 옛 `docs/conventions/*` 링크는 **고치지 않았다.** 그 시점 기록이라서. 대신 `docs/conventions/README.md`에 "없어진 경로 → 지금 읽을 것" 표를 뒀다.

- Claude 설정 디렉터리 2개(`~/.claude`, `~/.claude-personal`) **둘 다** 설치하기로 했다(사용자 선택). skills·commands는 심링크로 공유돼 물리적으론 한 벌이다.
- `~/.codex/AGENTS.md`의 Superpowers policy는 설계대로 관리 구역으로 대체했다. 다만 "어떤 skill을 언제 안 쓰나" 구체 목록은 always-on 2줄로 압축되면 손실이라, `agent-workflow` skill에 절을 만들어 보존했다. **Codex에서 lightweight mode가 약해졌다고 느끼면 이 결정을 먼저 의심한다**(백업: `~/.codex/AGENTS.md.bak-20260918-092353`).
- `--check`의 SessionStart hook 자동 배선(§7.5 호출 지점 2)은 **하지 않았다.** 전역 hook은 외부 도구 관리 구역이라 항목을 더 얹기 전에 §13 가정 4가 시간으로 검증되길 기다린다. 지금은 수동 `./bootstrap.sh --check`만.

## 검증 상태

- dev-conventions: `./bootstrap.sh` 재실행 변경 0건, `--check` 0. 설치 표면 해시 방식이라 문서 커밋으로는 낡음이 뜨지 않는다.
- nowhere: `./scripts/check` 통과(커밋 직전 재실행). 전역 규칙 복사본 5 → 0.
- 아직 안 돌림: **새 세션에서 에이전트가 `verify`를 스스로 찾아 실행하는가**(§11 단계 3 검증의 핵심). 이 세션은 그 파일을 직접 쓴 세션이라 증거가 못 된다.
- 미판정: §13 가정 3(Gemini CLI 미설치) · 가정 6(프로젝트 allow와 전역 deny/ask 합성 — nowhere `.claude/settings.json`을 깔아뒀으니 다음 nowhere 세션에서 관찰 가능).

## 환경 (PC 간)

- 필요 도구: bash, git, python3(3.11+ — `tomllib`). 외부 서비스·secret 없음.
- 다른 PC에서는 clone 후 `./bootstrap.sh --dry-run`으로 먼저 본다. 설정 디렉터리가 없는 에이전트는 자동으로 건너뛴다.
