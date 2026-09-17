---
name: deployment
description: Docker/GitHub Actions/운영 배포·롤백을 만들거나 바꿀 때
---

# 배포 컨벤션

Docker 이미지와 GitHub Actions를 사용하는 서비스의 **빌드·릴리스·운영 배포·롤백·검증 경계**를 정한다.
구체적인 서버 주소, 포트, 도메인, secret 값은 프로젝트마다 다르므로 `ops` 파라미터가 가리키는 운영 문서와 실행 가능한 workflow/script에 기록한다. 아래에서 `ops`는 그 문서를 뜻하고, 기본값은 repo 루트의 `DEPLOY.md`다.

## 원칙

- **빌드와 운영 배포를 분리한다.** 애플리케이션 repo의 CI는 이미지를 빌드해 registry에 push하고, 운영 배포는 별도 job 또는 infra repo가 명시적으로 실행한다.
- **배포 가능한 산출물은 불변이어야 한다.** 같은 커밋을 다시 빌드하지 않고 `sha-<short-sha>` 또는 image digest로 배포·롤백한다. `latest`는 편의용 포인터이지 배포 이력의 근거가 아니다.
- **운영 배포는 명시적 승인을 기본으로 한다.** 기본 흐름은 `main` push로 이미지 생성 → 검증된 태그를 production `workflow_dispatch`로 배포한다. 완전 자동 배포가 필요하면 실패 영향·롤백·승인 정책을 `ops`에 별도로 명시한다.
- **상태 경계를 섞지 않는다.** `구현`, `로컬 검증`, `커밋`, `push`, `이미지 생성`, `운영 배포`, `공개 검증`을 각각 확인한다. 앞 단계 성공을 다음 단계 성공으로 보고하지 않는다.
- **운영 secret은 이미지에 넣지 않는다.** 공개되어도 되는 빌드 시점 값과 서버 전용 런타임 값을 분리하고, 런타임 secret은 GitHub production Environment 또는 동등한 secret store에서 주입한다.
- **롤백은 배포 전에 준비한다.** 직전 정상 이미지 태그, 되돌리는 명령, healthcheck, DB 호환 범위를 배포 전에 알 수 있어야 한다.
- **실행 파일과 문서를 함께 유지한다.** workflow·compose·배포 script가 바뀌면 `ops`도 같은 변경에서 갱신한다. 문서와 실행 파일이 다르면 현재 실행 파일을 근거로 차이를 보고하고 문서를 바로잡는다.

## 표준 배포 흐름

```text
main push/tag
  → CI 검증
  → Docker image build
  → registry push (:sha-xxxxxxx, 필요 시 :latest/:1.2.3)
  → production 수동 승인·태그 선택
  → 서버 pull·기동
  → 로컬 healthcheck
  → nginx/ingress 전환·검증
  → 공개 URL과 실제 버전 확인
  → 이전 인스턴스/미사용 이미지 정리
```

권장 파일 배치는 다음과 같다. 프로젝트 구조가 다르면 역할은 유지하되 경로를 `ops`에 적는다.

```text
.github/workflows/
  build-image.yml          # 검증된 소스로 image build/push만 수행
  deploy.yml               # production 배포, 태그 입력과 승인 경계
deploy/
  docker-compose.prod.yml
  nginx/
  scripts/
    deploy.sh
    healthcheck.sh
DEPLOY.md                  # 프로젝트별 운영 SSOT (= `ops` 기본값)
```

## 프로젝트별로 명시할 선택

배포 컨벤션은 아래 선택 중 하나를 몰래 기본값으로 정하지 않는다. 프로젝트를 시작하거나 배포 구조를 바꿀 때 결정과 이유를 `ops`(와 `decisions`)에 남긴다.

### 배포 실행 위치

| 방식 | 적합한 경우 | 필수 주의점 |
|---|---|---|
| 운영 서버의 self-hosted runner | 단일 신뢰 서버에서 SSH 전송 없이 로컬 배포할 때 | runner 접근 주체 제한, production Environment 승인, 전용 사용자·작업 경로, 동시 배포 잠금 |
| GitHub-hosted runner → SSH/SCP | 운영 서버와 CI 실행 환경을 분리할 때 | SSH key 최소 권한, host key 검증, 임시 업로드 정리, 네트워크 접근 제한 |
| 별도 CD/오케스트레이터 | 여러 서버·클러스터·자동 확장이 필요할 때 | 선언적 상태, rollout/rollback timeout, 플랫폼 health probe |

`self-hosted` 라벨이나 `LIGHTSAIL_HOST` 같은 변수 이름만으로 실제 서버 위치를 추측하지 않는다. 실제 runner 설정과 workflow 실행 로그로 확인한다.

### 컨테이너 교체 전략

| 방식 | 선택 기준 | 실패 시 복구 |
|---|---|---|
| 단순 recreate | 단일 인스턴스, 짧은 중단 허용, 낮은 트래픽·복잡도 | 직전 정상 태그로 다시 pull/up |
| blue/green | 중단 최소화, 여러 서비스, 빠른 트래픽 복귀 필요 | 새 색상 health 실패 시 전환 금지, 전환 후 실패 시 이전 upstream 복구 |
| rolling/canary | 여러 replica, 점진적 노출과 관찰 필요 | 자동 rollback 조건과 관찰 지표를 배포 전에 정의 |

blue/green은 새 인스턴스를 먼저 띄우고 healthcheck를 통과한 뒤 nginx/ingress를 전환한다. 전환 확인 전에는 이전 인스턴스를 제거하지 않는다.

### repo와 서비스 경계

- 단일 서비스 repo는 같은 repo가 이미지 빌드와 해당 서비스 배포 workflow를 소유할 수 있다.
- web/app/api처럼 독립 이미지가 여러 개인 제품은 각 코드 repo가 자기 이미지를 만들고, 별도 infra repo가 compose·nginx·서비스별 태그·전체 배포 순서를 소유하는 방식을 우선 검토한다.
- 여러 repo가 같은 서버를 쓰면 서비스별 루트 디렉터리와 loopback 포트를 분리한다. nginx의 `default_server`, 공용 `map`, 인증서·ACME 경로의 소유자를 한 곳으로 정한다.
- 서비스마다 독립 배포가 가능하더라도 계약 변경, DB 스키마, 공용 nginx 변경처럼 함께 움직여야 하는 경계를 릴리스 문서에 표시한다.

## 이미지 버전과 릴리스

- 모든 `main` 이미지에 `sha-<short-sha>` 태그를 만든다. 가능하면 OCI label에도 전체 Git SHA, 애플리케이션 버전, 빌드 시각을 넣는다.
- 기본 브랜치의 `latest`는 개발 편의를 위해 둘 수 있지만 운영 배포·롤백 기록에는 불변 태그 또는 digest를 사용한다.
- `v1.2.3` Git tag를 쓰면 image는 `1.2.3`처럼 일관된 규칙으로 생성한다. repo별 독립 버전이면 서비스별 태그를 따로 선택할 수 있어야 한다.
- 배포 로그에는 요청한 태그와 실제 pull된 digest 또는 런타임 version을 남긴다. 태그 문자열만 같다고 동일 이미지라고 가정하지 않는다.
- 이미지 build job과 deploy job은 각각 최소 권한을 사용한다. 일반적으로 build는 `contents: read`, `packages: write`, deploy는 `contents: read`, `packages: read`면 충분하다.

## 설정과 secret

### 빌드 시점 값

- 브라우저 번들, sitemap, canonical, OG, 공개 API URL처럼 이미지에 박히는 값은 build arg 또는 CI variable로 전달한다.
- `NEXT_PUBLIC_*`, `VITE_*`는 이름에 secret처럼 보이는 단어가 있어도 최종 번들에서 공개될 수 있다. 민감 값을 넣지 않는다.
- 빌드 시점 값이 바뀌면 이미지를 다시 빌드해야 반영된다는 사실을 `ops`에 적는다.

### 런타임 값

- DB URL, API secret, service-role key, 암호화 키는 GitHub production Environment 또는 동등한 secret store에서 서버 env로 주입한다.
- 배포마다 env 파일을 재생성하는 방식이면 권한을 `600`으로 제한하고 필수 값이 비었는지 확인한 후 컨테이너를 교체한다.
- secret 값 자체는 workflow log, `ops`, compose, 예제 env에 남기지 않는다. 문서에는 필요한 이름과 발급 위치만 기록한다.
- public/default env와 secret env의 갱신 정책을 구분한다. 기존 파일을 보존하는지, 매 배포 재생성하는지 불분명하게 두지 않는다.

## 배포 안전장치

- production job은 GitHub `environment: production` 또는 동등한 승인·secret 경계를 사용한다.
- 같은 서비스의 동시 배포를 막는 concurrency 정책이나 서버측 잠금을 둔다.
- 배포 시작 전에 대상 태그가 registry에 존재하고 CI 검증을 통과했는지 확인한다.
- 컨테이너는 가능하면 `127.0.0.1`에만 bind하고 외부 트래픽은 nginx/ingress를 통한다.
- nginx 변경은 `nginx -t` 성공 후 reload한다. 새 설정이 실패하면 기존 링크/config로 복구하고 기존 정상 컨테이너를 유지한다.
- healthcheck는 최소한 서버 내부 endpoint와 공개 도메인을 나눠 확인한다. 인증이 필요한 서비스는 공개되지 않은 전용 health endpoint 또는 TCP check를 쓴다.
- 공개 healthcheck 실패를 DNS/TLS 초기 셋업 때문에 허용한다면 그 조건을 최초 배포 절차에만 한정한다. 일상 배포에서 무조건 무시하지 않는다.
- 배포가 끝나기 전에 이전 이미지를 지우지 않는다. 새 버전과 공개 경로가 확인된 뒤 보존 정책에 따라 정리한다.

## DB 마이그레이션과 롤백

- 이미지 롤백은 코드만 되돌리며 데이터와 스키마를 자동으로 되돌리지 않는다.
- 기본 원칙은 **DB forward-only, 코드는 롤백 가능**이다. 컬럼 추가·nullable·새 테이블 같은 하위호환 변경을 우선한다.
- 컬럼 삭제·이름 변경·NOT NULL 강제·타입 변경은 확장 → 양쪽 호환 → 제거의 여러 배포로 나눈다.
- migration 실행 시점, 승인 주체, 백업, 실패 복구, 이전 코드 호환 범위를 `ops` 또는 별도 runbook에 적는다.
- 운영 migration은 일반 이미지 배포에 암묵적으로 섞지 않는다. 자동화한다면 별도 단계와 명확한 실패 정책을 둔다.

## 배포 검증과 보고

배포 완료 보고 전에 해당되는 경계를 실제로 확인한다.

1. **소스:** 배포 대상 commit과 원격 브랜치 SHA가 일치하는가.
2. **이미지:** build workflow가 성공했고 해당 `sha-*` 태그 또는 digest가 존재하는가.
3. **배포 job:** production workflow가 성공했고 요청한 태그를 사용했는가.
4. **서버 내부:** 컨테이너 상태, 실제 image digest/version, 내부 healthcheck가 정상인가.
5. **프록시:** nginx/ingress 설정 검증과 reload가 성공했는가.
6. **공개 서비스:** HTTPS URL, 핵심 endpoint/page, 필요 시 sitemap·정적 자산이 정상인가.
7. **롤백 가능성:** 직전 정상 태그와 실행 절차가 남아 있는가.

확인하지 못한 경계는 `미확인` 또는 `차단`으로 적는다. 로컬 build 성공을 배포 성공이라고 하거나, workflow 성공만으로 공개 서비스까지 정상이라고 보고하지 않는다.

## `ops`에 반드시 기록할 항목

- build workflow와 deploy workflow의 트리거
- image registry/name/tag 규칙과 특정 버전 배포 방법
- 배포 실행 위치(self-hosted/SSH/CD)와 production root
- 서비스별 loopback 포트, 공개 도메인, nginx/ingress 소유권
- 필요한 GitHub Variables/Secrets의 **이름과 용도**(실제 값 제외)
- build-time 값과 runtime 값의 구분
- 최초 서버·DNS·TLS 준비 절차
- 일반 배포, healthcheck, 로그 확인, 롤백 명령
- recreate/blue-green/rolling 선택과 허용 중단 시간
- DB migration 정책과 자동화 여부
- 알려진 운영 제약과 아직 자동화되지 않은 단계

## 필요한 프로젝트 파라미터

- `ops` — 운영 SSOT 문서/디렉터리(기본 `DEPLOY.md`). 이 문서가 "적는다"고 하는 곳은 전부 여기다.
- `verify` — 배포 전에 통과해야 하는 검증 진입점.
- workflow·compose·배포 script는 파라미터가 아니라 그 프로젝트에 **실제로 존재하는 파일**이다. 없는 배포 파일을 관성적으로 만들지 않는다 — 서비스 형태와 운영 토폴로지를 먼저 정한 뒤 필요한 것만 추가한다.
- 기존 배포가 이 규칙과 다르면 즉시 일괄 변경하지 않는다. 현재 차이와 위험을 `ops`에 기록하고, 가역적인 항목부터 별도 작업으로 정렬한다.
