# 보류 후보: Python 스택 템플릿 (`project/stacks/python/`)

- **심사:** 2026-10-16 · 판정 **보류**(기각 아님) · 기록은 이 파일 「심사 메모」
- **원본:** dub(한국어 영상 AI 더빙, `~/sandbox/dub`) 구현 계획 (a1) — `docs/superpowers/plans/2026-10-16-cycle1-a1-foundation.md`의 Global Constraints "환경 관리 원칙"과 Task 1
- **사용자 방침(2026-10-16):** "개발하기 쉬운 방식 말고 관리하기 좋은 방식" — 버전을 전부 고정하고, 어긋나면 조용히 고치지 말고 실패하게 한다.

## 되살릴 조건

**dub에서 계획 (a1)이 main에 병합되고, 정기 갱신(`./scripts/lock --upgrade` → `./scripts/check`)을 한 번 거친 뒤.** 2026-10-16 현재 `feat/cycle1-a1` 미병합. 그 전에는 실사용 근거가 없고, 스택 config는 byte-identical 스냅샷으로 가져와야 하니 가져올 파일도 없다.

조건이 충족되면 **재심사하지 않고** 아래 승격안을 올린다. 「되살릴 때 확인할 사실」만 실측해서 채운다.

## 왜 필요한가

`project/stacks/`에 nestjs·next·vite-react만 있고 Python이 없다. coding-conventions의 "스택별 기본값"이 비어 있어 dub에서 도구를 처음부터 골랐다.

## 관찰한 것 (uv 0.10.0, macOS, 2026-10-16 시제품)

1. **Python 선택이 장비 상태에 따라 바뀐다.** 설정 없이 uv에 맡겼더니 같은 세션에서 pyenv 3.12.10, Homebrew 3.14.6, uv 관리 3.12.12가 번갈아 잡혔다.
2. **`--locked` 없는 `uv run`은 낡은 lock을 조용히 고친다.** `--locked`를 주면 실패한다.
3. **루트 공용 `uv.toml`은 일부 프로젝트에서만 먹는다.** `[tool.uv]` 표(예: `[tool.uv.sources]`)가 있는 프로젝트에서는 조용히 무시된다. 반만 적용되는 공용 설정이 가장 나쁘다.
4. 반면 루트 `ruff.toml`(`[tool.ruff]` 없는 하위 pyproject)과 루트에서 실행하는 `mypy.ini`는 정상 적용된다.
5. 독립 uv 프로젝트 여럿이 경로 의존성으로 공용 패키지를 쓰면, 공용 패키지의 의존성 변경이 모든 하위 lock을 낡게 만든다 → 한 번에 다시 잠그는 스크립트가 필요하다.

## 심사 메모 (2026-10-16)

- **dub 고유 구조가 섞여 있었다.** 관찰 3·5와 거기서 나온 규칙(프로젝트마다 같은 블록 + 줄 단위 검사, 전 프로젝트 일괄 lock, `_projects.sh`)은 dub D10 「단계마다 독립 uv 프로젝트, 워크스페이스로 묶지 않는다」 때문에 생겼다. D10의 이유는 모델 간 torch·CUDA 의존성 충돌이다(dub 설계 `docs/superpowers/specs/2026-10-16-dubbing-pipeline-design.md` 135·729행). 단일 프로젝트나 uv 워크스페이스(lock 하나)에선 이 문제가 생기지 않는다 → 승격안을 **기본**과 **독립 프로젝트 여럿일 때**로 나눴다.
- **원안에 없던 재료:** dub `ruff.toml`의 한국어 때문에 끈 규칙(E501 — 한글 폭 2 계산, RUF001-003 — 가운뎃점(·)을 헷갈리는 문자로 잡음). 한국어로 주석·메시지를 쓰는 모든 Python 저장소에 그대로 참이라 기본값에 넣는다.
- **공통 규칙 쪽 구멍:** coding-conventions 「공통 규칙」의 `pre-commit 훅 — husky + lint-staged`와 `package-manager` 기본 pnpm은 사실상 node 전용이다. Python 스택을 올릴 때 같이 고친다(아래 「승격 때 같이 고칠 것」).
- 원안 9번(GPU 컨테이너)은 아직 해 보지 않은 것이라 승격안에서 뺐다(「후속」).
- 원안의 description 후보는 둘 자리가 없다 — coding-conventions는 skill 하나에 description 하나다. 기존 description에 키워드만 더한다.

## 승격안

### 기본 (모든 Python 프로젝트)

1. Python은 uv가 관리하는 인터프리터만: `requires-python = ">=3.X,<3.(X+1)"` + `[tool.uv] python-preference = "only-managed"`. pyenv·Homebrew·conda Python을 섞지 않는다.
2. uv 버전 고정: `[tool.uv] required-version = ">=0.N,<0.(N+1)"`.
3. 검증·실행·문서 예시는 전부 `uv run --locked`(`uv lock --check` 포함). `--locked` 없는 `uv run`은 낡은 lock을 조용히 고친다.
4. 개발 도구: ruff는 `uvx ruff@<버전>`으로 루트에서 한 번, mypy·pytest는 dev 그룹에 `==` 고정. mypy는 프로젝트 의존성을 읽어야 해서 uvx로 빼지 않는다.
5. ruff: 한국어 주석·메시지를 쓰면 `E501`(줄 길이는 formatter에 맡김)·`RUF001`-`RUF003`을 끈다. 이유를 config 주석으로 남긴다.
6. 업데이트는 정해진 주기에 한 번에(월 1회 `--upgrade` → 검증). GitHub가 연결되면 Renovate·Dependabot.
7. 쓰지 않을 것: conda/mamba(패키지 관리자가 둘이 되고, Anaconda 기본 채널은 일정 규모 이상 조직의 상업 이용에 유료 약관), Poetry·pip-tools·pyenv(uv와 기능 중복).
8. 들여쓰기 4칸(백엔드 공통 규칙과 같음).

### 독립 uv 프로젝트 여럿일 때 (dub형)

먼저 **uv 워크스페이스로 충분한지** 본다 — lock 하나라 아래가 전부 필요 없다. 프로젝트끼리 의존성이 충돌할 때(dub: 단계별 torch·CUDA)만 독립 프로젝트로 가고, 그 이유를 `decisions`에 남긴다.

9. uv 설정은 **프로젝트마다 같은 블록**으로 두고, 검증 스크립트가 줄 단위로 일치를 검사한다. 루트 공용 `uv.toml`은 쓰지 않는다(관찰 3).
10. lock은 `scripts/lock` 하나로만 바꾼다 — 모든 프로젝트를 한 번에, `--upgrade`는 정기 갱신 때만(관찰 5).
11. 여러 프로젝트가 공유하는 라이브러리는 마이너 범위로 좁힌다(예: `pydantic>=2.14,<2.15`) — 모든 환경이 같은 마이너로 계약을 해석한다.

### 후속 (아직 해 보지 않음)

- GPU·네이티브 의존성이 큰 실행 단위는 컨테이너(CUDA 베이스 이미지 digest 고정 + `uv sync --locked`) — dub (a2)에서 해 본 뒤 보강한다.

## 되살릴 때 확인할 사실 (재심사 아님)

- **Python 패치 버전 고정.** 기본 1번은 pyenv·Homebrew가 섞이는 것(관찰 1)은 막지만, uv 관리 3.12.x가 둘 이상 깔리면 다시 갈릴 수 있다. 정기 갱신 뒤 dub에서 실제로 갈렸는지 보고, 갈렸으면 `.python-version`(정확한 패치) 고정을 기본에 더한다. 2026-10-16 dub에는 `.python-version`이 없다.
- shellcheck가 셸 변수 뒤 한글(→ coding-conventions 「셸 스크립트」)을 경고하는지 — 경고하면 `scripts/check`에 넣는다.

## 가져올 실파일 (dub 병합 후)

`ruff.toml`, `mypy.ini`(strict + pydantic 플러그인), `scripts/check`(환경값·lock 검사 포함), pyproject 공통 블록(`[tool.uv]`·dev 그룹). 독립 프로젝트형 추가분으로 `scripts/lock`, `scripts/_projects.sh`. 폴더 README에 출처·기준 버전(uv 0.10.0, Python 3.12.12, ruff 0.17.1, mypy 2.4.0, pytest 9.1.1 — 갱신 뒤 값으로)과 기본/추가분 구분을 적는다.

## 승격 때 같이 고칠 것

- `global/skills/coding-conventions/SKILL.md` — 「스택별 기본값」에 `### Python / uv → project/stacks/python/`. 공통 규칙의 `pre-commit 훅 — husky + lint-staged`를 node 한정으로 적고 Python 쪽(검사 진입점 `scripts/check`, 훅 도입 여부)을 정하거나 「알려진 불일치」에 남긴다. `package-manager` 설명에 Python은 uv.
- 같은 문서 description에 키워드 추가(예: "…lint·포맷·tsconfig·uv/lock·커밋 규칙 등 스택 기본값을 정할 때").
- `project/AGENTS.template.md` — `stack`·`package-manager` 예시 값에 `python`·`uv`.
- `README.md` 규칙 목록 표의 코딩 컨벤션 행.
