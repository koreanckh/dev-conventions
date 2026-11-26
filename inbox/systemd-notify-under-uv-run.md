# 후보 1건 — money-fab #022에서 관찰 (2026-11-21)

## systemd `Type=notify` 서비스는 `uv run`으로 띄우지 않는다

관찰: 장중 감시 서비스를 `Type=notify` + `WatchdogSec=60` + `ExecStart=uv run … mf ai watch`로 만들었다. uv(0.13.4)는 python을 **자식 프로세스**로 띄우고, systemd(255)는 기본값(`NotifyAccess=main`)에서 main PID가 보낸 알림만 받는다. 그래서 python이 보낸 `READY=1`·`WATCHDOG=1`이 버려지고(저널: `… only permitted for main PID`), 시작 제한 시간에 죽고 재시작하기를 되풀이할 뻔했다. 단위 테스트는 유닛 파일 문자열만 봐서 못 잡았다. 최종 검토에서 잡았고, `systemd-run --user --wait -p Type=notify -p WatchdogSec=10 …`로 `uv run`(실패)과 `.venv/bin/python`(성공)을 나란히 돌려 확인했다.

- 고친 것: `ExecStart=<프로젝트>/.venv/bin/<콘솔 스크립트>`로 python을 main PID로 띄운다(배포가 `uv sync --frozen`으로 venv를 만든다). `NotifyAccess=main`은 명시해 둔다. `NotifyAccess=all`은 자식 아무나 알림을 보낼 수 있어 피했다.
- 확인 방법: 새 notify 유닛은 실제로 한 번 띄워 `systemctl --user status`가 `active (running)`이고 저널에 `main PID` 줄이 없는지 본다.

재사용 이유: uv로 관리하는 Python 서비스를 systemd notify·watchdog으로 돌리는 다른 프로젝트도 같은 함정을 밟는다. `poetry run`·`npm run`처럼 자식을 띄우는 다른 실행기도 마찬가지일 가능성이 크다(미확인).
