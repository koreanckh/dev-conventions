---
name: coding-conventions
description: 코드를 쓰거나 lint·포맷·tsconfig·커밋 규칙 등 스택 기본값을 정할 때
---

# 코딩 컨벤션

프로젝트에서 코드를 어떻게 쓰는가에 대한 규칙. (도메인/제품 로직 규칙은 여기 넣지 않는다.)
아래 **공통 규칙**은 모든 프로젝트에 그대로 적용되고, **스택별 기본값**은 dev-conventions `project/stacks/<stack>/`의 실제 config 파일을 프로젝트에 두고 시작한다(→ `stack` 파라미터).
스택별 값은 각 스택 폴더 README에 출처와 기준 버전을 기록한다. NestJS는 공식 starter를 기준으로 팀 타입 안전성·포맷 규칙을 더하고, Vite/React·Next.js는 실 프로젝트 config를 기준으로 한다.

## 공통 규칙 (모든 프로젝트에 적용)

### 패키지 매니저 · 워크스페이스
- 패키지 매니저는 `package-manager` 파라미터의 값을 쓴다(node 프로젝트 기본 제안값은 pnpm). `package.json`의 `packageManager` 필드로 버전을 고정한다. 아래 명령 예시의 `pnpm`은 이 파라미터 값으로 바꿔 읽는다.
- 여러 repo를 한 워크스페이스에 둘 때: 각 repo는 독립 Git repo로 취급, 코드 변경은 해당 repo로 `cd` 한 뒤 그 안에서 Git 실행. 루트에서 하위 repo 파일을 `git add` 하지 않는다.

### 커밋 메시지 — Conventional Commits
- 형식: `type(scope): 설명`.
- type: `commit-types` 파라미터의 목록. 기본 제안값은 `feat`, `fix`, `chore`, `refactor`, `style`, `docs`, `wip`.
- `wip`은 **handoff를 동반한 세션 중단 커밋 전용**이다 → [작업 인계](../handoff/SKILL.md). 브랜치를 병합할 땐 squash하거나 정식 type으로 다시 쓴다.
- scope는 모듈/기능명 (`feat(notification):`, `fix(auth):`, `refactor(db):`).
- 설명은 한국어 허용. 이슈 참조는 `(#12)` 형태로 뒤에 붙임.
- commitlint로 강제하지 않고 **관례로 유지**한다 (툴 미설치가 기본).

### pre-commit 훅 — husky + lint-staged
- `.husky/pre-commit`은 `pnpm exec lint-staged` 한 줄.
- 훅 설치는 `package.json`의 `"prepare": "husky"` 스크립트로.
- lint-staged는 변경된 파일에만 `eslint --fix` (+ prettier 있으면 `prettier --write`).
- 코드 편집 **전에** 대상 repo의 `eslint.config.*`/`.prettierrc`를 확인하고 그 포맷 규칙을 따른다(예: `tabWidth`). 설정을 무시하고 커밋하면 리뷰/머지 때 재정렬 diff가 생긴다.
- 훅을 도입한 repo에서 훅 우회(`--no-verify`)는 **금지**.

### 검증 게이트 (코드 변경 시)
- "통과"를 보고하기 전에 `verify`(작은 변경은 `verify-quick`) 파라미터의 명령을 **실제로 실행**하고 결과를 남긴다. 실행 없이 완료 주장 금지.
- TDD 가능한 로직: failing test → 최소 구현 → pass 순서.
- 변경은 작고 검증 가능한 단위로 유지.

### 주석
- 비즈니스 의도, 불변식(invariant), 큐/멱등성, 결제 시맨틱, 통합 제약 등 **자명하지 않은 부분**에 주석을 단다.
- **남겨둔 주석은 함부로 삭제하지 않는다.**

### 자동 생성물
- `generated` 파라미터에 해당하는 자동 생성 파일(예: 라우트 트리, 스키마 gen 산출물)은 **직접 수정하지 않는다.**

### 들여쓰기 (indent)
- **백엔드는 언어/프레임워크 무관하게 indent 4-space로 통일한다** (Nest/TS든 다른 언어든 백엔드 레이어는 4-space 고정). 포맷터가 있으면 그 값으로 강제한다(예: Prettier `tabWidth: 4`).
- 프론트엔드는 2-space (관례). 왜: 백엔드는 스택이 바뀌어도 코드베이스 전반의 들여쓰기를 한 값으로 유지해 diff·리뷰 노이즈를 없앤다.

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
