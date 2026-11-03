# 후보: 손맛 연구소 MVP에서 나온 재사용 교훈 4건

- **출처:** sonmat-lab MVP 구현(2026-11-02~03, Flutter 3.47.9 + drift · NestJS 11 · 홈서버 chois `dev` 계정)
- **dev-conventions에 지금 있는 것:** 아래 넷 다 없다(`pkill`·drift·WebCrypto·body limit 검색 0건).

## 1. `pkill -f '<패턴>'`은 그 패턴이 든 내 셸까지 죽인다

에이전트가 개발 서버를 끄려고 `pkill -f 'nest start'` 같은 명령을 Bash 도구로 보내면, 그 명령줄 자체가 패턴과 맞아
도구 셸이 함께 죽는다(출력 없이 끝남). 같은 호스트의 운영 프로세스(다른 uid)가 패턴에 걸릴 위험도 있다.
→ 끌 때는 포트로 PID를 찾는다(`ss -ltnp 'sport = :3801'`) — 내 uid 프로세스만, 운영 포트는 건드리지 않는다.
재사용: 홈서버에서 개발 서버를 띄우고 끄는 모든 프로젝트.

## 2. drift를 쓰는 Flutter 위젯 테스트는 기본 설정이면 끝나지 않는다

drift 스트림은 닫힐 때 타이머를 쓰는데 위젯 테스트의 가짜 시계에서는 돌지 않아 `flutter test`가 멈춘다.
→ 테스트 DB를 `DatabaseConnection(NativeDatabase.memory(), closeStreamsSynchronously: true)`로 열고,
끝에 위젯을 내린 뒤 `tester.runAsync(db.close)`. 스트림이 살아 있을 때 `runAsync` 하나에 DB 쓰기는 한 번만
(두 번이면 첫 쓰기로 깨어난 화면 쪽 조회가 잠금을 쥐고 가짜 시계를 기다려 교착 — 여러 행은 `batch`로).
재사용: Flutter + drift 프로젝트의 테스트 지원 파일 기본값.

## 3. HTTP(Tailscale IP) 미리보기에서는 브라우저 암호화 API가 없다

"Tailscale IP에 HTTP로 바인딩해 링크를 준다" 규칙대로 Flutter 웹을 띄우면 secure context가 아니라
`flutter_secure_storage`(WebCrypto)가 실패해 로그인 토큰을 못 저장했다. 같은 이유로 `crypto.subtle`·Service Worker·
클립보드 쓰기 등도 막힌다.
→ 미리보기 전용 대체 경로(웹은 토큰을 로컬 DB에)를 두거나 `tailscale serve`로 HTTPS를 준다. 미리보기 규칙에 한 줄 경고 후보.

## 4. NestJS(Express) JSON 본문 한도 기본 100KB가 로컬 우선 앱의 첫 동기화를 막는다

오프라인에 쌓인 기록을 처음 올리는 push가 100KB를 넘어 413. 단위 테스트는 작은 본문만 써서 못 잡았다.
→ 동기화 서버는 `app.useBodyParser('json', { limit: … })`를 명시하고 "큰 첫 push" 테스트를 둔다.
재사용: 로컬 우선 + 서버 동기화 구조의 서버 기본값.
