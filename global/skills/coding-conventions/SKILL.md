---
name: coding-conventions
description: 코드를 쓰거나(로그 레벨·테스트 격리 포함) lint·포맷·tsconfig·커밋·스테이징·버전 고정 등 스택 기본값을 정할 때
---

# 코딩 컨벤션

프로젝트에서 코드를 어떻게 쓰는가에 대한 규칙. (도메인/제품 로직 규칙은 여기 넣지 않는다.)
아래 **공통 규칙**은 모든 프로젝트에 그대로 적용되고, **스택별 기본값**은 dev-conventions `project/stacks/<stack>/`의 실제 config 파일을 프로젝트에 두고 시작한다(→ `stack` 파라미터).
스택별 값은 각 스택 폴더 README에 출처와 기준 버전을 기록한다. NestJS는 공식 starter를 기준으로 팀 타입 안전성·포맷 규칙을 더하고, Vite/React·Next.js는 실 프로젝트 config를 기준으로 한다.

## 공통 규칙 (모든 프로젝트에 적용)

### 패키지 매니저 · 워크스페이스
- 패키지 매니저는 `package-manager` 파라미터의 값을 쓴다(node 프로젝트 기본 제안값은 pnpm). `package.json`의 `packageManager` 필드로 버전을 고정한다. 아래 명령 예시의 `pnpm`은 이 파라미터 값으로 바꿔 읽는다.
- 여러 repo를 한 워크스페이스에 둘 때: 각 repo는 독립 Git repo로 취급, 코드 변경은 해당 repo로 `cd` 한 뒤 그 안에서 Git 실행. 루트에서 하위 repo 파일을 `git add` 하지 않는다.
- 도구 버전을 **검사만 하는** 고정값(uv `required-version`, `engines` 등 — 어긋나면 실패할 뿐 설치해 주지 않는 것)은 **모든 개발 장비가 실제 설치 경로로 받을 수 있는 버전**에 맞춘다. 지금 이 장비에 깔린 버전을 기준으로 삼지 않는다. Homebrew처럼 최신 안정판만 주는 경로면 그 안정판이 기준이고, 안정판이 올라가 검사가 깨지면 고정값과 lock을 함께 올린 뒤 모든 장비를 같은 명령(`brew upgrade <도구>`)으로 맞춘다. 정확한 버전을 직접 받아 주는 고정(corepack의 `packageManager`, uv가 내려받는 Python)은 해당하지 않는다. 왜: PC A의 uv 0.10에 맞춰 고정했더니 PC B의 Homebrew uv는 0.12였고, Homebrew로는 둘 다 0.13만 받을 수 있었다(dub, 2026-10-17).
- 새 의존성의 라이선스를 확인하는 프로젝트는 **lock의 전이 의존성까지** 본다. lock을 갱신한 뒤 설치된 배포판의 라이선스 메타데이터(License-Expression·License·classifier)를 전부 훑고, 비어 있거나 `Other`·`UNKNOWN`이면 저장소의 LICENSE 원문을 읽는다. 왜: Apache-2.0 모델 패키지가 의존하는 `kaldiio`의 유일한 LICENSE가 내부 평가 전용 약관이었다. PyPI 필드는 비어 있었고, 모델 카드만 봤으면 놓쳤다(dub, 2026-10-18).

### 커밋 메시지 — Conventional Commits
- 형식: `type(scope): 설명`.
- type: `commit-types` 파라미터의 목록. 기본 제안값은 `feat`, `fix`, `chore`, `refactor`, `style`, `docs`, `wip`.
- `wip`은 **세션 중단 커밋 전용**이다(작업 브랜치에 남기고, 짝이 되는 handoff는 `docs-branch`에 따로 올린다) → [작업 인계](../handoff/SKILL.md). 브랜치를 병합할 땐 squash하거나 정식 type으로 다시 쓴다.
- scope는 모듈/기능명 (`feat(notification):`, `fix(auth):`, `refactor(db):`).
- 설명은 한국어 허용. 이슈 참조는 `(#12)` 형태로 뒤에 붙임.
- commitlint로 강제하지 않고 **관례로 유지**한다 (툴 미설치가 기본).

### 스테이징
- **바꾼 경로를 하나씩** 적는다. `git add -A`·`git add .`를 쓰지 않는다 — 검증·빌드가 만든 산출물과 사용자가 두고 간 미추적 파일이 함께 실린다.
- **검증을 돌린 뒤에는 커밋 전에 `git status`를 다시 본다.** 검증 도구가 추적 파일을 고치기도 한다. 내가 바꾸지 않은 변경이 보이면 싣지 말고 원인을 확인한다.
- 왜: 사용자의 미추적 `scratchpad/*.sql`이 `-A`에 쓸려 들어갔고(nowhere), 검증이 새로 만든 `ios/Podfile`과 다시 쓴 추적 파일 `ios/Flutter/*.xcconfig`가 딸려 왔다(mulzipsa). 셋 다 우연히 `git status`를 봐서 잡았다(2026-09-18). 권한 `ask`로 올리면 사람이 직접 쓸 때까지 묻게 되므로, 또 새면 그때 올린다.

### pre-commit 훅 — husky + lint-staged
- `.husky/pre-commit`은 `pnpm exec lint-staged` 한 줄.
- 훅 설치는 `package.json`의 `"prepare": "husky"` 스크립트로.
- lint-staged는 변경된 파일에만 `eslint --fix` (+ prettier 있으면 `prettier --write`).
- 코드 편집 **전에** 대상 repo의 `eslint.config.*`/`.prettierrc`를 확인하고 그 포맷 규칙을 따른다(예: `tabWidth`). 설정을 무시하고 커밋하면 리뷰/머지 때 재정렬 diff가 생긴다.
- 훅을 도입한 repo에서 훅 우회(`--no-verify`)는 **금지**.

### 검증 게이트 (코드 변경 시)
- "통과"를 보고하기 전에 `verify`(작은 변경은 `verify-quick`) 파라미터의 명령을 **실제로 실행**하고 결과를 남긴다. 실행 없이 완료 주장 금지.
- TDD 가능한 로직: failing test → 최소 구현 → pass 순서.
- 검사(가드·검증 스크립트의 실패 분기)를 추가하면 **한 번은 일부러 실패시켜** 실패 메시지까지 나오는지 본다. 정상 경로만 돌리면 실패를 알려야 할 코드가 실패할 때만 깨지는 버그가 남는다 — failing test를 먼저 보는 것과 같은 이유다.
- 완료를 판단하는 명령의 출력을 **파이프 끝에서 거르지 않는다.** 파이프의 종료 코드는 마지막 명령(`grep` 등)의 것이라, 검사가 실패해도 `| grep … && git commit`이 그대로 돈다. 출력은 파일로 받아 종료 코드로 판단한 뒤 필요한 줄만 보거나(`./scripts/check > <로그> 2>&1 && grep … <로그>`), `set -o pipefail`을 쓴다. 실행은 했는데 결과를 잘못 읽는 경우다(dub, 2026-10-18 — 실패한 검사 뒤에 커밋이 됐다).
- **문서만 바꿨어도 검증을 건너뛰지 않는다.** 문서도 lint·format 대상일 수 있다 — ruff 0.17은 Markdown 안의 Python 코드 블록도 포맷 검사해서, 계획 문서만 바꾼 커밋이 `./scripts/check`를 두 번 깨뜨렸다(dub, 2026-10-18·19). 코드 블록을 넣은 문서엔 포맷터를 돌려 두거나, docs를 검사 대상에서 뺄지 프로젝트가 정한다.
- 변경은 작고 검증 가능한 단위로 유지.

### 테스트 격리
- 테스트는 앱의 **기본 state·로그 경로(운영 파일)를 쓰지 않는다.** 테스트 설정(pytest면 autouse fixture)에서 기본 경로를 임시 디렉터리로 돌리고, 테스트가 붙인 로그 핸들러는 끝날 때 닫고 뗀다. 회귀 테스트로 「인자 없이 실행해도 파일 핸들러가 저장소 state 아래를 가리키지 않는다」를 두고, 빈 checkout에서 전체 스위트를 돌린 뒤 운영 디렉터리(`state/` 등)가 생기지 않는지 한 번 본다.
- 왜: 배포 절차가 운영 checkout에서 테스트를 돌리는데, 경로 인자 없이 CLI `main()`을 부른 테스트 하나가 운영 로그에 파일 핸들러를 붙였다. 배포 직후 운영 로그에 가짜 `ERROR`가 찍혀 장애로 오인할 뻔했고, 이전 배포 때도 같은 줄이 10건 있었는데 아무도 몰랐다(news-compare, 2026-11-09).

### 로그 레벨
- 레벨은 **그 줄을 쓰는 시점의 사건**으로 정한다. 요청의 최종 결과로 정하지 않는다 — 접수 시점엔 결과를 모르고, 실패는 실패한 지점에서 따로 남긴다. 줄끼리는 요청 식별자(trace_id 등)로 잇는다.
- **ERROR** = 우리 시스템이나 외부 의존성이 실패해 사람이 조치해야 하는 일. **WARNING** = 규칙대로 거절한 요청(4xx), 실패했지만 대체 처리로 넘어간 일. **INFO** = 정상 흐름의 주요 사건(요청 접수·상태 변경·완료). **DEBUG** = 항목별 세부(운영에서 꺼진다).
- 클라이언트 입력을 규칙대로 거절한 것은 ERROR가 아니다. 검증 API가 찾아낸 문제(중복 등)는 그 API의 정상 결과라 INFO다.
- 실패를 `print`로 남기지 않는다 — 레벨이 없어 오류 패널·오류 로그 어디에도 안 잡힌다. 예외를 잡고 응답만 돌려주는 곳에는 반드시 로그를 남긴다.
- 운영에서 재현에 필요한 입력값(요청 본문 등)은 DEBUG가 아니라 INFO로 남긴다(비밀값·개인정보는 가린다).
- 레벨을 내리기 전에 **그 레벨을 실제로 누가 보는지** 확인한다. WARNING을 보는 곳이 없으면 조치가 필요한 외부 의존성 실패는 ERROR에 두고, WARNING을 볼 곳을 만드는 일을 to-do로 남긴다 — 기준대로 내렸다가 외부 API 장애를 알아챈 유일한 신호를 잃을 뻔했다.
- 왜: 오류 패널이 규칙대로 한 4xx 거절로 차서 진짜 오류가 묻혔고, 정작 Slack 전송·스케줄러 시작 실패는 `print`라 어디에도 안 잡혔다(회사 Django API, 2026-11-09 — 로그 호출 약 300곳 정리).

### 주석
- 비즈니스 의도, 불변식(invariant), 큐/멱등성, 결제 시맨틱, 통합 제약 등 **자명하지 않은 부분**에 주석을 단다.
- **남겨둔 주석은 함부로 삭제하지 않는다.**

### 자동 생성물
- `generated` 파라미터에 해당하는 자동 생성 파일(예: 라우트 트리, 스키마 gen 산출물)은 **직접 수정하지 않는다.**

### 들여쓰기 (indent)
- **백엔드는 언어/프레임워크 무관하게 indent 4-space로 통일한다** (Nest/TS든 다른 언어든 백엔드 레이어는 4-space 고정). 포맷터가 있으면 그 값으로 강제한다(예: Prettier `tabWidth: 4`).
- 프론트엔드는 2-space (관례). 왜: 백엔드는 스택이 바뀌어도 코드베이스 전반의 들여쓰기를 한 값으로 유지해 diff·리뷰 노이즈를 없앤다.

### 셸 스크립트
- 변수 바로 뒤에 ASCII가 아닌 글자(한글 등)가 오면 `${var}`로 감싼다(`"${pin}이 없다"`, `$pin이` 금지). 헷갈리면 항상 `${var}`. 왜: macOS 기본 `/bin/bash`(3.2)는 UTF-8 로케일에서 한글 첫 바이트까지 변수 이름으로 읽는다. `set -u`면 `unbound variable`로 죽고, 아니면 값이 빠지고 글자가 깨진 문자열이 조용히 나간다. Linux bash(5.3에서 확인)에선 재현되지 않아 CI는 통과하고 로컬에서만 깨진다. 실패 메시지 줄에 잘 숨는다(dub, 2026-10-16).
- 개발 서버 같은 프로세스를 끌 때 `pkill -f '<패턴>'`을 쓰지 않는다. 포트로 PID를 찾아(`ss -ltnp 'sport = :<포트>'`) 내 uid 프로세스만 끈다. 왜: 에이전트가 도구 셸로 보내면 그 명령줄 자체가 패턴에 맞아 도구 셸이 같이 죽는다(출력 없이 끝난다). 같은 호스트에 다른 uid로 도는 운영 프로세스도 패턴에 걸릴 수 있다(sonmat-lab, 2026-11-03).

## 스택별 기본값 (`stack` 파라미터에 해당하는 `project/stacks/<stack>/`)

실제 config는 산문이 아니라 **파일**로 둔다. 아래는 "무엇을/왜"만 요약하고, 값은 링크한 템플릿 파일이 정본이다.
> 출처·기준 날짜·버전은 각 `project/stacks/<stack>/README.md`에 기록한다. 복사 후 설치된 버전에 맞춰 조정하고 `pnpm lint`/`pnpm build`로 한 번 확인한다.

### TypeScript / NestJS (백엔드) → `project/stacks/nestjs/`
- Nest 공식 `typescript-starter` 기준 Node 22.x / TS 5.7.x / `module: nodenext`(`moduleResolution: nodenext`) / `target: ES2023` / `isolatedModules` / 데코레이터 메타데이터 on. 범용 경로 alias는 미지정. NestJS 11.
- tsconfig strict 포인트: `strictNullChecks`·`noImplicitAny`·`forceConsistentCasingInFileNames` on. (`strictBindCallApply`·`noFallthroughCasesInSwitch`는 off.)
- ESLint(flat): `eslint.recommended` + `tseslint.recommendedTypeChecked`(`projectService: true`) + `prettier/recommended`. `no-explicit-any`·`no-unsafe-enum-comparison`·`require-await` off, `no-floating-promises`·`no-unsafe-*` warn, `no-unused-vars` error(`^_` 무시), `prettier/prettier` error.
- Prettier: 4-space(백엔드 공통 규칙 — 위 "들여쓰기" 참조), `singleQuote`, `trailingComma: all`, `printWidth: 200`.
- 모듈 분기: 기본은 공식 스타터처럼 `nodenext`. 순수 ESM 프로젝트만 `package.json`의 `"type": "module"`과 import/라이브러리 호환성을 함께 검토한다. 전체 `strict: true`와 경로 alias도 프로젝트 단위로 결정한다.
- 폴더 구조: 기능별 모듈 `src/<feature>/`에 `.controller.ts`/`.service.ts`/`.module.ts` + `dto/`. 테스트 `.service.spec.ts`/`.unit.spec.ts`.
- 크로스커팅·인프라는 서비스(기능) 모듈과 분리해 `src/common/`에 묶는다: `config/`·`db/`·`storage/`·`interceptors/`·`filters/`·`guards/`·`decorators/`·`errors/`. `AppModule`의 import도 `[공통/인프라]`와 `[서비스]`로 그룹을 구분한다.
- 모듈 간 결합은 직접 import보다 이벤트버스 선호(`@EventHandler(EventName)`).
- 응답 envelope 통일(`TransformInterceptor`), 전역 `ValidationPipe(whitelist)`, 전역 `HttpExceptionFilter`, 에러 코드 enum 일원화, 인증 가드 전역 + `@Public()` 예외. 이 전역들은 `main.ts`에서 수동 등록하지 말고 **`@Global CommonModule`에서 `APP_PIPE`/`APP_INTERCEPTOR`/`APP_FILTER`/`APP_GUARD` provider로 등록**한다. CommonModule은 인프라 모듈(DB·Storage)을 import/export하는 단일 진입점 역할을 한다.
- 명령어: `pnpm build`(nest build), `pnpm lint`(`eslint --fix`), `pnpm format`, `pnpm test`(jest). DB(Drizzle): `schema.ts 수정 → db:generate → db:migrate`.
- 큰 JSON 본문을 받는 서버(로컬 우선 앱의 동기화 서버 등)는 본문 한도를 명시한다(`app.useBodyParser('json', { limit: … })`) — Express 기본값 100KB에서 오프라인에 쌓인 기록의 첫 push가 413으로 막힌다. 작은 본문만 쓰는 단위 테스트로는 못 잡으니 「큰 첫 push」 테스트를 둔다(sonmat-lab, 2026-11-03).

### React / Vite (프론트 앱) → `project/stacks/vite-react/`
- React 19 / Vite 5 / TS ~5.6. `target: ES2020` / `module: ESNext` / `moduleResolution: Bundler` / `jsx: react-jsx`. project references(`tsconfig.app.json`/`tsconfig.node.json`).
- strict 세트: `strict`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, `noUncheckedSideEffectImports`.
- 경로 alias `@/*` → `./src/*` (tsconfig + `vite.config` + `components.json` 일치).
- ESLint(flat): `js.recommended` + `tseslint.recommended` + `react-hooks` + `react-refresh`(`only-export-components: warn`, `allowConstantExport: true`).
- 네이밍/구조: 컴포넌트 파일 **PascalCase.tsx**. 공유 `components/shared/`, UI 프리미티브 `components/ui/`. 스토어 `<name>.store.ts`, API `api/<resource>.ts` + 공유 `api/client.ts`.
- 서버 상태 TanStack Query, `queryKey` = `['리소스명', '필터/액션']`. 폼 `react-hook-form` + `zod`.
- API 응답 `{ success: boolean, data: T }`. axios interceptor로 토큰 주입 + 401 처리.
- 명령어: `pnpm build`(`tsc -b && vite build`), `pnpm lint`(`eslint .`), `pnpm dev`.

### Next.js (공개 사이트) → `project/stacks/next/`
- Next 16 / React 19 / TS 5.x. `target: ES2017` / `module: esnext` / `moduleResolution: bundler` / `jsx: react-jsx` / `strict` / `noEmit` / `isolatedModules` / next plugin. alias `@/*`.
- ESLint(flat `eslint.config.mjs`): `eslint-config-next/core-web-vitals` + `/typescript`. ignore: `.next/**`, `out/**`, `build/**`, `next-env.d.ts`.
- **주의:** Next.js는 버전마다 스캐폴딩이 크게 바뀐다(이 스냅샷은 Next 16 · flat config 기준) → 코드 전에 설치된 버전 문서/deprecation 확인. 가능하면 `create-next-app` 산출물에 이 값들을 병합.

### Flutter (스택 config 스냅샷은 아직 없다)
- drift를 쓰는 위젯 테스트는 기본 설정이면 끝나지 않는다 — drift 스트림이 닫힐 때 쓰는 타이머가 위젯 테스트의 가짜 시계에서 돌지 않아 `flutter test`가 멈춘다. 테스트 DB를 여는 공용 도우미에 기본값으로 둔다(sonmat-lab, Flutter 3.47.9, 2026-11-03):
  - `DatabaseConnection(NativeDatabase.memory(), closeStreamsSynchronously: true)`로 열고, 끝에 위젯을 내린 뒤 `tester.runAsync(db.close)`.
  - 스트림이 살아 있을 때 `runAsync` 하나에 DB 쓰기는 한 번만(여러 행은 `batch`). 두 번이면 첫 쓰기로 깨어난 화면 쪽 조회가 잠금을 쥔 채 가짜 시계를 기다려 교착한다.

### Python (스택 config 스냅샷은 아직 없다)
uv·ruff·mypy 기본값은 dev-conventions `inbox/held-python-stack-template.md`에 보류 후보로 있다. 승격되면 이 절이 `project/stacks/python/`을 가리킨다. 아래는 언어·라이브러리 함정이다(전부 dub에서 밟았다).
- 시각·샘플·프레임 경계 변환에 `round()`를 쓰지 않는다 — Python `round()`는 짝수 쪽으로 반올림해서(45ms → 4, 55ms → 6 프레임) 같은 길이 구간의 프레임 수가 달라진다. 정수 half-up(`(x + d // 2) // d`)으로 쓰고, 정확히 절반인 경계값 테스트를 하나 둔다(2026-10-18, 같은 저장소에서 두 번째).
- pytest에서 마커로 테스트를 고를 때는 `item.get_closest_marker("<이름>") is not None`을 쓴다. `item.keywords`엔 노드·디렉터리·클래스 이름이 섞여 있어서, 마커 이름과 같은 디렉터리(`llm/`)가 생기는 순간 그 아래 테스트가 마커 없이도 걸려 조용히 전부 건너뛰어졌다(2026-10-19).
- pydantic 필드 이름이 `BaseModel`의 속성(`model_*`, `register`, `copy`, `json`, `dict` 등)과 겹치면 경고만 나고 그 필드의 기본값이 부모의 메서드로 바뀐다. pytest `filterwarnings = ["error::UserWarning:pydantic.*"]`로 그 경고를 오류로 올리거나, 필드 이름을 정할 때 겹치는지 본다(2026-10-19).
- torch 모델의 dtype·장치를 일괄로 바꾸는 코드는 `named_buffers(remove_duplicate=False)`나 모듈마다 `_buffers`를 돈다. 기본 `named_buffers()`는 여러 모듈이 공유하는 텐서를 한 번만 돌려줘서 나머지 모듈엔 옛 dtype이 남는다(MPS에 float64가 남아 `model.to("mps")` 실패, 2026-10-19). 더 나은 길은 텐서를 만드는 원천에서 dtype을 정하는 것이고, 바꾼 뒤엔 「모델 텐서의 dtype 집합」을 확인하는 테스트를 둔다(가중치 없이 모델만 만들어 검사할 수 있다).

### 무빌드 프로젝트 (예: Chrome Extension MV3)
- lint/format/husky 없이 소스 직접 로드도 허용. 대신 환경 전환은 스크립트로(`config.<env>.js` 복사 등), 하드코딩 편집 금지.

## 알려진 불일치 (정리하면 좋은 것)
- Prettier 설정 파일은 백엔드(api)에만 있음. 프론트(app/web)는 ESLint에만 의존 → repo 간 포맷 규칙 미통일.
- 들여쓰기: 백엔드 4-space는 공통 규칙으로 확정(위 "들여쓰기" 참조, Prettier 강제). 프론트 2-space는 관례일 뿐 포맷터로 강제하지 않음 → 프론트 포맷 강제 여부는 미정.
- commitlint 미설치라 커밋 컨벤션은 관례 의존. 도입한다면 허용 type에 `wip`을 반드시 포함한다 — 빠뜨리면 세션 중단 커밋이 훅에 막히는데 `--no-verify`도 금지라 빠져나갈 길이 없다.

## 필요한 프로젝트 파라미터

- `package-manager` — 커맨드·lockfile·`packageManager` 필드가 전부 이 값에서 나온다. node 프로젝트의 기본 제안값은 pnpm이다.
- `stack` — 어느 `project/stacks/<stack>/` config로 시작했는지. 위 "스택별 기본값"에서 읽을 줄을 고르는 값이다.
- `commit-types` — 이 저장소에서 쓰는 Conventional Commits type 목록. `wip`이 없으면 세션 중단 커밋도 정식 type으로 쓴다.
- `generated` — 직접 수정하지 않는 자동 생성물 목록.
- `verify` / `verify-quick` — 검증 게이트에서 실제로 실행하는 명령.
