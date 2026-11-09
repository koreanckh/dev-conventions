# dub (a3) 병합에서 나온 후보 3건 — 2026-10-19

출처: dub 저장소, 구현 계획 (a3) LLM 단계(culture·translate)와 `llm/` 호출 계층. 셋 다 실제로 밟은 것이다(GPU 서버 세션이 정리하고, gh가 있는 Mac에서 올린다).

## 1. ruff의 Markdown 코드 블록 검사 — 두 번째 관찰: 문서만 바꾼 커밋도 검증 명령을 돌린다 (coding-conventions 검증 게이트)

**관찰:** (a2) 후보 2번(`2026-10-18-dub-a2-lessons.md`, ruff 0.17은 Markdown 안의 Python 코드 블록도 포맷 검사한다)과 같은 함정을 다시 밟았다. 이번에는 main에 직접 올린 계획 문서 커밋(코드 예시가 든 계획)이 `./scripts/check`를 깨뜨렸고, `91c56e6`(계획 코드 예시를 ruff format에 맞춘다)으로 고쳤다.

**후보 규칙(보강):** 「완료 전에 검증 명령을 실제로 실행한다」의 예외로 「문서만 바꿨으면 건너뛴다」를 두지 않는다. 문서도 lint·format 대상일 수 있다(코드 블록). 같은 함정이 두 번 나왔으니 (a2) 후보와 묶어 처리한다.

## 2. pytest `item.keywords`에는 디렉터리 이름도 들어간다 — 마커 판정은 `item.get_closest_marker(name)`으로 (python 스택, 테스트 게이트)

**관찰:** `@pytest.mark.llm` 테스트를 환경 변수로 열고 닫는 conftest에서 `if "llm" in item.keywords`로 판정했다. `llm/` 프로젝트 안의 테스트는 경로에 `llm` 디렉터리가 있어 마커가 없어도 keywords에 `llm`이 들어갔고, 그 프로젝트 테스트가 전부 건너뛰어졌다.

**후보 규칙:** 마커로 테스트를 고를 때는 `item.get_closest_marker("<이름>") is not None`을 쓴다. `item.keywords`는 노드 이름·디렉터리·클래스 이름까지 섞인 집합이다. 마커 이름과 같은 디렉터리가 생기는 순간 조용히 깨진다.

## 3. pydantic 필드 이름이 `BaseModel` 속성과 겹치면 경고만 나고 기본값이 메서드로 바뀐다 — 필드 이름 경고는 오류로 본다 (python 스택)

**관찰:** pydantic 모델에 `BaseModel`의 속성과 같은 이름(`register` 등)의 필드를 두었더니 경고만 나고, 그 필드의 기본값이 부모의 메서드로 바뀌었다.

**후보 규칙:** pytest `filterwarnings = ["error::UserWarning:pydantic.*"]`처럼 pydantic의 필드 이름 경고를 오류로 올린다. 또는 필드 이름을 정할 때 `BaseModel`의 공개 속성(`model_*`, `register`, `copy`, `json`, `dict` 등)과 겹치는지 본다.
