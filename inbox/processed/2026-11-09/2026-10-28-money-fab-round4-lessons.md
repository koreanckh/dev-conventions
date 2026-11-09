# money-fab 라운드 4(#004)에서 나온 후보 2건 — 2026-10-28

출처: money-fab 저장소, to-do #004(브랜치 `feat/round4-stock-selection`, 병합 `5c1a703`). 둘 다 이 작업에서 실제로 밟은 것이다.

## 1. chois 서버에서 메모리 소프트 상한은 다른 프로세스를 죽인다 — 하드 상한만 쓴다 (전역 CLAUDE.md 환경 절 · agent-workflow)

**관찰:** 램이 모자란 작업(셀 하나 최대 3GB)을 서버에서 돌리려고 `systemd-run --user --scope -p MemoryHigh=300M -p MemorySwapMax=500M`로 "넘으면 느려지는" 상한을 시험했다. 압박이 68~71%로 오르자 `user@2001.service`의 systemd-oomd 정책(압박 50% 초과가 20초)이 **시험 프로세스가 아니라 Claude Code 터미널 pty 두 개**를 죽였다(2026-10-27 17:45). 같은 계정의 Hermes·작업·터미널이 모두 한 사용자 슬라이스 안에 있어서, oomd는 회수량이 큰 다른 cgroup을 고른다. 반면 `-p MemoryMax=… -p MemorySwapMax=0`(하드, 스왑 0)은 넘는 순간 그 작업만 커널 OOM으로 죽고(exit 137) oomd는 움직이지 않았다. 다음 날 같은 방식(2.5GB)으로 진단 스크립트가 상한에 걸렸을 때도 그 작업만 죽었다. `CPUQuota`는 느려질 뿐 안전했다. 별도로, 하드 상한 안에서도 계정 전체 압박이 오르므로 `/sys/fs/cgroup/.../memory.pressure`를 2초마다 읽어 some>30·full>20이 3번 이어지면 작업을 멈추는 감시기를 붙였다.

**후보 규칙:** chois(dev 계정)에서 무거운 작업은 `systemd-run --user --scope -p MemoryMax=<실측 최고치+여유> -p MemorySwapMax=0 -p CPUQuota=<n>%` + `nice`로만 돌린다. `MemoryHigh`·스왑으로 압박을 끄는 방식은 쓰지 않는다. sudo 없이 된다(cpu·memory가 사용자에게 위임돼 있다). 전역 CLAUDE.md "환경" 줄에 한 줄로 붙일 만하다.

## 2. 출력을 파일로 돌린 장시간 파이썬 작업은 버퍼링 때문에 로그가 빈다 (coding-conventions · 장시간 실행)

**관찰:** `uv run mf research run … > run.log 2>&1 &`로 수십 분 도는 작업을 돌렸는데, 중간에 SIGTERM으로 끝나자 로그가 비어 있었다. 터미널이 아닌 파일로 가는 stdout은 블록 버퍼라 `print`가 버퍼에 남은 채 프로세스가 죽었다. 어디까지 갔는지 알 수 없어 실행 세 번을 날렸다. `PYTHONUNBUFFERED=1`을 붙인 뒤로는 셀마다 진행이 바로 찍혔다.

**후보 규칙:** 백그라운드·nohup·리다이렉트로 돌리는 파이썬 장시간 작업은 `PYTHONUNBUFFERED=1`(또는 `python -u`)을 붙이고, 사용자에게 주는 실행 명령에도 넣는다. 진행 로그를 남기는 CLI라면 `print(..., flush=True)`를 기본으로 한다.
