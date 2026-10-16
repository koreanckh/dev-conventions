# 후보: Python 스택 템플릿 (`project/stacks/python/`)

- **출처:** dub(한국어 영상 AI 더빙, `~/sandbox/dub`) 구현 계획 (a1) — `docs/superpowers/plans/2026-10-16-cycle1-a1-foundation.md`의 Global Constraints "환경 관리 원칙"과 Task 1
- **처리 시점:** dub에서 계획 (a1)이 병합되고 정기 갱신(`./scripts/lock --upgrade` → `./scripts/check`)을 한 번 거친 뒤. 그 전에는 실사용 근거가 없다. 그때 dub의 실파일을 byte-identical 스냅샷으로 가져온다.
- **사용자 방침(2026-10-16):** "개발하기 쉬운 방식 말고 관리하기 좋은 방식" — 버전을 전부 고정하고, 어긋나면 조용히 고치지 말고 실패하게 한다.

## 왜 필요한가

`project/stacks/`에 nestjs·next·vite-react만 있고 Python이 없다. coding-conventions의 "스택별 기본값"이 비어 있어 dub에서 도구를 처음부터 골랐다.

## 관찰한 것 (uv 0.10.0, macOS, 2026-10-16 시제품)

1. **Python 선택이 장비 상태에 따라 바뀐다.** 설정 없이 uv에 맡겼더니 같은 세션에서 pyenv 3.12.10, Homebrew 3.14.6, uv 관리 3.12.12가 번갈아 잡혔다.
2. **`--locked` 없는 `uv run`은 낡은 lock을 조용히 고친다.** `--locked`를 주면 실패한다.
3. **루트 공용 `uv.toml`은 일부 프로젝트에서만 먹는다.** `[tool.uv]` 표(예: `[tool.uv.sources]`)가 있는 프로젝트에서는 조용히 무시된다. 반만 적용되는 공용 설정이 가장 나쁘다.
4. 반면 루트 `ruff.toml`(`[tool.ruff]` 없는 하위 pyproject)과 루트에서 실행하는 `mypy.ini`는 정상 적용된다.
5. 독립 uv 프로젝트 여럿이 경로 의존성으로 공용 패키지를 쓰면, 공용 패키지의 의존성 변경이 모든 하위 lock을 낡게 만든다 → 한 번에 다시 잠그는 스크립트가 필요하다.

## 승격안

1. Python은 uv가 관리하는 인터프리터만: `requires-python = ">=3.X,<3.(X+1)"` + `[tool.uv] python-preference = "only-managed"`. pyenv·Homebrew·conda Python을 섞지 않는다.
2. uv 버전 고정: `[tool.uv] required-version = ">=0.N,<0.(N+1)"`.
3. uv 설정은 **프로젝트마다 같은 블록**으로 두고, 검증 스크립트가 줄 단위로 일치를 검사한다. 루트 공용 `uv.toml`은 쓰지 않는다.
4. lock은 `scripts/lock` 하나로만 바꾼다(모든 프로젝트를 한 번에, `--upgrade`는 정기 갱신 때만). 검증·실행·문서 예시는 전부 `uv run --locked`.
5. 개발 도구: ruff는 `uvx ruff@<버전>`으로 루트에서 한 번, mypy·pytest는 프로젝트 dev 그룹에 `==` 고정.
6. 여러 프로젝트가 공유하는 라이브러리는 마이너 범위로 좁힌다(예: `pydantic>=2.14,<2.15`).
7. 업데이트는 정해진 주기에 한 번에(월 1회 `scripts/lock --upgrade` → 검증). GitHub가 연결되면 Renovate·Dependabot.
8. 쓰지 않을 것: conda/mamba(패키지 관리자가 둘이 되고, Anaconda 기본 채널은 일정 규모 이상 조직의 상업 이용에 유료 약관), Poetry·pip-tools·pyenv(uv와 기능 중복).
9. GPU·네이티브 의존성이 큰 실행 단위는 컨테이너(CUDA 베이스 이미지 digest 고정 + `uv sync --locked`) — dub (a2)에서 실제로 해 본 뒤 보강한다.

## 가져올 실파일 (dub 병합 후)

`ruff.toml`, `mypy.ini`(strict + pydantic 플러그인), `scripts/check`(환경값·lock 검사 포함), `scripts/lock`, `scripts/_projects.sh`, pyproject 공통 블록(`[tool.uv]`·dev 그룹). 폴더 README에 출처·기준 버전(uv 0.10.0, Python 3.12.12, ruff 0.17.1, mypy 2.4.0, pytest 9.1.1)을 적는다.

description 후보(coding-conventions "스택별 기본값"에 Python 줄 추가): "Python 프로젝트의 uv·lint·타입 검사·lock 기본값을 정할 때"
