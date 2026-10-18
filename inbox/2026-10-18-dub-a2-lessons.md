# dub (a2) 병합에서 나온 후보 4건 — 2026-10-18

출처: dub 저장소, 구현 계획 (a2) 분석 모델 단계(GPU 서버 작업). 넷 다 실제로 밟은 것이다.

## 1. docs-branch 문서를 작업 브랜치에서 고쳐 옮기지 않는다 (handoff·agent-workflow)

**관찰:** 작업 브랜치에서 스펙(docs-branch에 커밋할 문서)을 고친 뒤 `git stash` → `git switch main` → `git stash pop`으로 옮겼다. main에는 같은 표에 앞서 커밋한 행이 있었고, 브랜치의 파일에는 그 행이 없어서 같은 자리에서 충돌했다. 브랜치는 main의 문서 커밋을 받지 않으므로, 브랜치 쪽 문서는 갈수록 낡는다.

**후보 규칙:** docs-branch에 갈 문서는 작업 브랜치에서 고치지 않는다. 브랜치 코드를 먼저 커밋하고 docs-branch로 전환해 직접 고친 뒤 돌아온다(워크트리를 쓰면 main 체크아웃 쪽에서). "문서는 워크트리를 따라가지 않는다"의 실행 절차로 붙일 만하다.

## 2. ruff 0.17은 Markdown 안의 Python 코드 블록도 포맷 검사한다 (coding-conventions, python 스택)

**관찰:** `uvx ruff@0.17.1 format --check .`가 계획 문서(`docs/superpowers/plans/*.md`)의 ```python 블록 때문에 실패했다. 함수 사이 빈 줄, 120자 줄바꿈 같은 것이다. 파이썬 파일은 하나도 안 바뀐 상태였다.

**후보 규칙:** 계획·스펙에 코드 블록을 넣었으면 `ruff format <문서>`를 돌려 둔다. 또는 docs를 format 대상에서 뺄지 프로젝트마다 정한다.

## 3. 라이선스 게이트는 lock의 전이 의존성까지 본다 (라이선스 확인 절차가 있는 프로젝트)

**관찰:** FireRedVAD(코드·가중치 Apache-2.0)의 pip 패키지가 `kaldiio`에 의존했다. 그런데 kaldiio의 유일한 LICENSE는 NTT "SOFTWARE LICENSE AGREEMENT FOR EVALUATION"(내부 평가 전용)이었다. PyPI 라이선스 필드는 비어 있었고 GitHub 표시는 "Other"였다. 모델 카드만 봤으면 놓쳤다.

**후보 규칙:** 새 의존성을 넣으면 lock을 갱신한 뒤 설치된 배포판의 라이선스 메타데이터(License-Expression / License / classifier)를 전부 훑는다. 비어 있거나 "Other"·"UNKNOWN"인 것은 저장소 LICENSE 원문을 읽는다.

## 4. GPU torch는 드라이버에 맞는 CUDA 인덱스를 플랫폼 마커로 고정한다 (python 스택, GPU)

**관찰:** PyPI 기본 torch(2.11 이후)는 CUDA 13을 요구한다(`cuda-toolkit==13.x`). 그래서 드라이버 550(CUDA 12.4까지) 서버에서는 돌지 않는다. torchaudio는 2.11에서 개발이 끝났고 torch 버전을 정확히 요구한다.

**후보 규칙:** `[[tool.uv.index]]`로 cu12x 인덱스를 `explicit = true`로 두고, `torch = [{ index = "...", marker = "sys_platform == 'linux'" }]`로 Linux에만 건다. Mac 개발 장비도 같은 lock으로 PyPI 휠을 받는다. `environments = ["sys_platform == 'linux'", "sys_platform == 'darwin'"]`로 lock을 좁힌다. 모델마다 torch 버전이 갈리면 단계(프로젝트)별로 환경을 나눠 해결한다.
