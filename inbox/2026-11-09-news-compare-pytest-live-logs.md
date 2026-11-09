# 운영 폴더에서 돌리는 테스트가 운영 로그에 쓰지 않게 한다 — 2026-11-09

출처: news-compare 저장소, to-do `docs/to-do/done/2026-11-06-pytest-log-isolation.md`(fix `501d68f`). 이 작업에서 실제로 밟은 것이다.

## 후보: 테스트의 기본 state·로그 경로는 운영 파일을 가리키지 않는다 (coding-conventions · 테스트 / deployment · 배포 검증)

**관찰:** 배포 절차가 운영 checkout에서 `pip install -e .` 다음에 pytest를 돌린다. 테스트 하나가 `--state-dir` 없이 CLI `main()`을 불렀다. 그러자 로깅 설정(프로세스당 한 번만 핸들러를 붙임)이 저장소 기본 `state/logs/nc.log`, 즉 운영 로그에 파일 핸들러를 붙였다. 이후 모든 테스트 로그가 그 파일로 들어갔다. 배포 직후 운영 로그에 `ERROR … chrome busy` 같은 가짜 오류가 찍혔고, 실제 장애로 오인할 뻔했다. 경로(`/tmp/pytest-of-…`)를 보고서야 테스트 로그인 줄 알았다. 이전 배포 때도 같은 줄이 10건 있었는데 아무도 몰랐다.

**후보 규칙:**
- 운영 checkout에서도 테스트를 돌리는 프로젝트는 테스트 conftest에서 앱의 기본 state·로그 경로를 tmp로 돌린다(autouse).
- 테스트가 붙인 로그 핸들러는 테스트가 끝날 때 닫고 뗀다.
- 회귀 테스트로 "인자 없이 실행해도 파일 핸들러가 저장소 state 아래를 가리키지 않음"을 둔다.
- 빈 checkout에서 전체 스위트를 돌린 뒤 저장소 `state/`가 생기지 않는지 한 번 확인한다.
