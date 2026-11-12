# 후보 2건 — money-fab #022에서 관찰 (2026-11-11)

## 1. 정기 작업에서 구독 계정의 `claude -p`를 부를 때

관찰: 매일 아침 공시 점수를 구독 로그인의 `claude -p`(Haiku)로 매기게 만들면서 밟은 것.

- `--bare`는 OAuth 로그인을 읽지 않는다 → 구독으로는 못 돈다. 대신 끌 것을 하나씩 끈다:
  `--tools "" --strict-mcp-config --disable-slash-commands --no-session-persistence --setting-sources project --settings '{"disableAllHooks":true}'`.
- 프롬프트를 인자로 주면 stdin을 3초 기다린 뒤 진행한다. 입력은 stdin으로 보낸다(인자가 없으면 대기가 없다).
- 작업 폴더가 저장소 안이면 그 저장소의 CLAUDE.md가 입력에 따라 들어간다. 저장소 밖 빈 폴더(`~/.cache/<앱>/claude-cwd`)에서 부른다. 확인은 결과 JSON의 입력 토큰 수로 한다(지침이 끼면 수천 토큰 뛴다).
- 출력은 `--output-format json --json-schema …`로 받고, 받은 쪽에서 id·범위·enum을 다시 검사한다.
- systemd 서비스에는 PATH가 없으니 `claude` 경로를 배포 때 `command -v claude`로 찾아 유닛에 박는다.

재사용 이유: 구독 사용량으로 LLM 분류를 돌리려는 다른 프로젝트(Hermes 연동 등)도 같은 플래그 조합이 필요하다.

## 2. 기다리는 반복문은 조건 명령의 오류를 숨기지 않는다

관찰: `until journalctl --since "today 15:49" ... 2>/dev/null | grep -q Finished; do sleep 20; done`이 1시간 38분 동안 끝나지 않았다. `"today 15:49"`는 journalctl이 못 읽는 시각이라 매번 오류가 났는데, `2>/dev/null`이 그걸 숨겨 "아직 안 끝남"과 구별되지 않았다. 작업은 15:50:05에 이미 끝나 있었다.

- 시각은 절대값(`"2026-11-11 15:49"`)으로 쓴다.
- 반복문을 걸기 전에 조건 명령을 한 번 그냥 돌려 본다. 오류는 숨기지 않고, 조건 명령이 실패하면 반복을 끝낸다.
- 반복문에는 상한 시간을 둔다.

재사용 이유: 배포·배치 완료를 기다리는 모든 반복문에 같은 함정이 있다.
