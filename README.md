# dev-conventions

여러 PC(회사/개인)와 여러 에이전트(Claude Code·Codex·Gemini CLI)를 오가도 똑같이 지켜지는 개발 규칙의 **유일한 원본**.

**규칙은 환경에 설치하고, 프로젝트에는 값과 사실만 둔다.** 규칙 본문을 프로젝트로 복사하지 않으므로 드리프트할 복사본이 없다. 설계 근거와 단계별 계획: `docs/specs/2026-09-18-engineering-system-v2.md`.

> **현재 상태:** 설계 §11 **단계 1~5 완료** — 이 PC 설치, 활성 프로젝트 3개(nowhere·bus·mulzipsa) 전환, `/apply-conventions` 스캐폴딩 재작성까지.
> 남은 것: 단계 6(다른 PC에서 clone + bootstrap — **이 전까지 이식성은 미검증**), 단계 7(승격 트리거).

## 규칙 목록

강제력 3층 중 **skills** 층. 각 문서의 `description`이 "언제 읽어라" 트리거다.

| 규칙 | 문서 | 요약 |
|---|---|---|
| TODO 관리 | `global/skills/todo-workflow/SKILL.md` | 번호 = **GitHub 이슈 번호**(3자리 zero-pad, 이슈 먼저 발행해 받는다) + md(SSOT) → GitHub Issue → Project Status 동시 갱신 + 라벨·Auto-add 셋업 · 무거운 항목은 spec/plan 연계 |
| 코딩 컨벤션 | `global/skills/coding-conventions/SKILL.md` | 커밋·훅·주석·자동생성물 + 스택별 실 config는 `project/stacks/<stack>/` |
| 에이전트 작업 규칙 | `global/skills/agent-workflow/SKILL.md` | lightweight 기본 · 위험 비례 검증 · 병렬 dispatch/워크트리는 승인된 병합 단위에 사용 |
| 작업 인계 | `global/skills/handoff/SKILL.md` | 브랜치당 1개 · 덮어쓰기 · 한 화면 · 이미 실패한 접근 기록 · WIP 커밋과 함께 push · 병합 시 삭제 |
| 트랜잭션 관리 | `global/skills/transaction-management/SKILL.md` | 언어/프레임워크 무관 원칙 · 짧은 경계 · 부수효과는 커밋 후 · 낙관적 락·멱등성 · 분산 트랜잭션 지양 |
| 배포 | `global/skills/deployment/SKILL.md` | 이미지 build와 운영 배포 분리 · 불변 태그 · 실행/교체 전략 선택 · secret/healthcheck/롤백·DB migration 경계 |
| 하네스 설정 | `global/skills/harness-engineering/SKILL.md` | 지침 < hook/권한 < 환경 계층 · "매번/절대"는 hook·deny로 · 지침 파일은 목차 · 생성/평가 분리 · 권한 3패턴(기본 B) |

그 밖의 두 층:

- `global/always-on.md` — 항상 로드되는 소수 규칙(15줄 예산). 잊으면 안 지켜지는데 코드로 강제할 수도 없는 것만.
- `global/enforcement/` — 하네스가 집행하는 권한·hook 실파일. 모델이 우회할 수 없다. 값의 출처와 역수집 기록은 그 폴더 README.

## 구조

```
global/                    ── 환경에 설치되는 것 ──
  always-on.md             항상 로드. 15줄 예산
  skills/<name>/SKILL.md   규칙 본문(frontmatter의 description이 트리거)
  skills/SKILL.template.md 새 skill 골격 (이 repo 안에서만)
  enforcement/
    claude/                settings.fragment.json · hooks/*.sh
    codex/                 config.fragment.toml
project/                   ── 프로젝트에 스캐폴딩되는 것 ──
  AGENTS.template.md       프로젝트 파라미터 섹션 골격
  decision.template.md     결정 기록 골격 (docs/decisions/NNN-<slug>.md)
  check.template.sh        단일 검증 진입점 골격 (scripts/check)
  handoff.template.md · todo-file.template.md
  stacks/nestjs · vite-react · next    실제 config 파일
install/
  targets                  에이전트별 설치 매핑
  lib/dc_install.py        설치 동작(구역 교체·키 병합·심링크·lock)
  apply-conventions.md     프로젝트 스캐폴딩 커맨드 (파라미터·verify·결정 기록)
bootstrap.sh               PC마다 1회 실행 — 설치/갱신/검사/제거
inbox/                     다른 프로젝트 원자료 → /import-conventions
docs/specs/                설계 문서
AGENTS.md                  이 repo 작업 지침 (CLAUDE.md·GEMINI.md는 얇은 어댑터)
```

## 두 계층의 계약

전역 규칙은 프로젝트마다 달라지는 값을 본문에 적지 않고 **파라미터 이름으로 참조**한다. "pnpm을 쓴다"가 아니라 "`package-manager` 파라미터의 도구를 쓴다".

프로젝트는 그 값을 `AGENTS.md`의 `## 프로젝트 파라미터` 섹션에 둔다(골격: `project/AGENTS.template.md`).

```markdown
## 프로젝트 파라미터

- stack: nestjs + vite-react
- package-manager: pnpm
- verify: ./scripts/check — 완료를 보고하기 전에 실행한다
- generated: src/routeTree.gen.ts — 직접 수정하지 않는다
- issues: github:owner/repo
- decisions: docs/decisions/ — 기존 결정. 뒤집기 전에 읽는다
- handoff: docs/handoff/
```

각 줄은 **혼자 읽혀도 뜻이 통하게** 쓴다(값 + 한 구절). 전역 설치가 없는 환경(클라우드 세션·협업자)에서도 `verify` 줄만 보고 무엇을 해야 하는지 알 수 있어야 한다 — 그게 degraded mode를 공짜로 만든다.

## 새 프로젝트에 적용하기

적용할 프로젝트 폴더에서 `/apply-conventions`. 규칙 본문을 복사하지 않고 **프로젝트 계층만 스캐폴딩**한다.

1. 실태 조사(스택·기존 검증 진입점·to-do 번호 체계·자동 생성물·이슈/보드)
2. 기존 `docs/conventions/` 복사본이 있으면 **지우기 전에 드리프트를 건진다** — 복사본에는 그 프로젝트가 덧붙인 내용이 섞여 있다
3. `AGENTS.md`를 파라미터 형태로(프로젝트 고유 내용은 보존)
4. `verify` 진입점 — **이미 있으면 그걸 가리키고**, 없으면 `scripts/check`를 만든다. 지금 통과하는 범위로만
5. 전역과 어긋나는 실태는 `docs/decisions/`에 기록(전역 기본값을 왜 안 쓰는지까지)
6. 복사본 삭제 + 옛 링크 안내 README, 프로젝트 고유 allow
7. `verify` 실행 → 보고. **커밋은 하지 않는다**

코드는 건드리지 않는다. `verify`가 빨간불이면 그건 드러난 사실이고, 고치는 건 별도 작업이다.

## 새 규칙 추가하기

### 방법 A — 원자료 일괄 import (추천)

다른 프로젝트에서 쓰던 규칙을 `inbox/`에 아무 형식으로나 모아두고 이 repo에서 **`/import-conventions`** 실행. 주제별로 분해해 기존 규칙과 대조 후 신규 생성/갱신하고 README 표까지 정리한다. 자세한 건 `inbox/README.md`.

### 방법 B — 하나씩 수동

`AGENTS.md`의 "새 규칙 추가하기" 체크리스트를 따른다. 요약:

1. 어느 층인지 판정(enforcement / always-on / skill).
2. `global/skills/SKILL.template.md`를 복사해 채운다(자기완결형: 원칙 + 값 + 주의 + 필요한 파라미터).
3. 값이 있으면 실파일로(`project/stacks/<이름>/` 또는 `global/enforcement/`) + 폴더 README(출처·기준 버전).
4. 새 파라미터를 쓰면 `project/AGENTS.template.md`를 같은 커밋에서 고친다.
5. 위 "규칙 목록" 표에 한 줄 추가.

## 설치와 제거

PC마다 한 번, 이 repo에서:

```sh
./bootstrap.sh              # 설치/갱신 (멱등 — 두 번 돌려도 결과 같음)
./bootstrap.sh --dry-run    # 바뀔 내용만 출력. 아무것도 쓰지 않는다
./bootstrap.sh --check      # 낡음 검사만. 0=최신, 1=낡음
./bootstrap.sh --copy       # 심링크를 못 쓰는 환경
./bootstrap.sh --uninstall  # lock에 기록된 자기 설치분만 제거
./bootstrap.sh --agent claude   # 한 에이전트만
```

설치 대상은 `install/targets`가 정하고, 실제 동작은 `install/lib/dc_install.py`가 한다. 규칙:

- **설정 디렉터리가 있는 에이전트에만** 설치한다. 없으면 건너뛰고 보고한다(디렉터리를 새로 만들지 않는다).
- skills와 hook은 **심링크/절대경로**로 가리킨다 → `git pull`이 곧 갱신이다. always-on은 대상 파일 안 `<!-- BEGIN dev-conventions -->` 구역만, settings는 **없는 항목만 추가**한다. 기존 항목과 다른 도구의 hook은 건드리지 않는다.
- 덮어쓰기 전에 `<file>.bak-<timestamp>`로 백업한다.
- 설치 기록은 `<config>/.dev-conventions.lock`(repo 경로·commit·설치 표면 해시·mode·추가한 항목). `--uninstall`은 **여기 적힌 것만** 지운다.
- `--check`는 커밋이 아니라 **실제로 설치되는 파일들의 해시**를 비교한다. 규칙과 무관한 커밋으로는 낡았다고 하지 않고, 규칙을 고치면 커밋 전에도 낡았다고 한다.
- **계정 프로필마다 한 번씩 돌린다.** 회사/개인 계정을 나눠 쓰면 설정 디렉터리도 나뉜다:

  ```sh
  ./bootstrap.sh                                                   # 기본 프로필 전부
  CLAUDE_CONFIG_DIR=~/.claude-personal ./bootstrap.sh --agent claude
  CODEX_HOME=~/.codex-personal         ./bootstrap.sh --agent codex
  ```

  프로필 목록은 머신마다 다르므로 저장소에 적지 않는다. 대신 bootstrap이 **설치되지 않은 프로필로 보이는 디렉터리를 찾아 한 줄로 알린다**(`~/.claude*`, `~/.codex*`). 프로필끼리 `skills`·`commands`를 심링크로 공유하면 그쪽은 자동으로 "최신"이 되고 각자 파일(`settings.json`·`config.toml`)만 병합된다. lock은 프로필마다 생긴다.

`--uninstall`이 되돌리지 못하는 것: 설치할 때 **관리 구역으로 대체된 옛 수기 섹션**(예: `~/.codex/AGENTS.md`의 `## Superpowers policy`). 그 내용은 같은 자리의 `.bak-*` 파일에 있다.

## 이동성

- 이 repo를 public으로 두면 새 PC는 clone 후 `./bootstrap.sh` 한 번으로 같은 상태가 된다(스크립트·비밀정보 없음). 의존성은 bash·git·python3뿐이다.
- 설치는 **가리킬 수 있으면 가리킨다**: skills와 hook은 심링크, always-on은 대상 파일 안 관리 구역만 교체, settings는 키 단위 병합. 복사 표면적이 `프로젝트 수 × 문서 수`에서 `환경 수 × 1`로 줄어든다.
- 전역 설정 파일을 직접 고치지 않는다. 고칠 일이 생기면 이 repo를 고치고 재설치한다.
