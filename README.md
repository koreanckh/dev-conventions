# dev-conventions

여러 PC(회사/개인)와 여러 에이전트(Claude Code·Codex·Gemini CLI)를 오가도 똑같이 지켜지는 개발 규칙의 **유일한 원본**.

**규칙은 환경에 설치하고, 프로젝트에는 값과 사실만 둔다.** 규칙 본문을 프로젝트로 복사하지 않으므로 드리프트할 복사본이 없다. 설계 근거와 단계별 계획: `docs/specs/2026-09-18-engineering-system-v2.md`.

> **현재 상태:** 설계 §11 **단계 1(원본 구성) 완료**. 전역 설치(`bootstrap.sh` §7.8 계약)는 단계 2에서 구현한다.
> 그때까지 `global/`은 원본으로만 존재하고 어떤 환경에도 설치돼 있지 않다. `/apply-conventions`도 단계 5 재작성 전까지 실행하지 않는다.

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
  apply-conventions.md     프로젝트 스캐폴딩 커맨드 (단계 5에서 재작성)
bootstrap.sh               PC마다 1회 실행
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

## 이동성

- 이 repo를 public으로 두면 새 PC는 clone 후 `./bootstrap.sh` 한 번으로 같은 상태가 된다(스크립트·비밀정보 없음). 단계 2부터 유효하다.
- 설치는 **가리킬 수 있으면 가리킨다**: skills와 hook은 심링크, always-on은 대상 파일 안 관리 구역만 교체, settings는 키 단위 병합. 복사 표면적이 `프로젝트 수 × 문서 수`에서 `환경 수 × 1`로 줄어든다.
- 전역 설정 파일을 직접 고치지 않는다. 고칠 일이 생기면 이 repo를 고치고 재설치한다.
