# 코딩 컨벤션

> 원본(SSOT): dev-conventions. 대상 repo로 복사할 땐 이 줄을 `> 출처: dev-conventions · 복사 YYYY-MM-DD`로 바꿔 남긴다(복사본이 낡았는지 판단용).

프로젝트에서 코드를 어떻게 쓰는가에 대한 규칙. (도메인/제품 로직 규칙은 여기 넣지 않는다.)
아래 **공통 규칙**은 새 프로젝트에도 그대로 가져가고, **스택별 기본값**은 `templates/<stack>/`의 실제 config 파일을 복사해 시작한다.
스택별 값의 근거는 SuperMarkit(api=NestJS, app=Vite/React, web=Next.js) 기준.

## 공통 규칙 (모든 프로젝트에 적용)

### 패키지 매니저 · 워크스페이스
- 패키지 매니저는 **pnpm**으로 통일. `package.json`의 `packageManager` 필드로 버전 고정.
- 여러 repo를 한 워크스페이스에 둘 때: 각 repo는 독립 Git repo로 취급, 코드 변경은 해당 repo로 `cd` 한 뒤 그 안에서 Git 실행. 루트에서 하위 repo 파일을 `git add` 하지 않는다.

### 커밋 메시지 — Conventional Commits
- 형식: `type(scope): 설명`.
- type: `feat`, `fix`, `chore`, `refactor`, `style`, `docs`.
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
- "통과"를 보고하기 전에 `build` / `typecheck` / `lint`를 **실제로 실행**하고 결과를 남긴다. 실행 없이 완료 주장 금지.
- TDD 가능한 로직: failing test → 최소 구현 → pass 순서.
- 변경은 작고 검증 가능한 단위로 유지.

### 주석
- 비즈니스 의도, 불변식(invariant), 큐/멱등성, 결제 시맨틱, 통합 제약 등 **자명하지 않은 부분**에 주석을 단다.
- **남겨둔 주석은 함부로 삭제하지 않는다.**

### 자동 생성물
- 자동 생성 파일(예: 라우트 트리, 스키마 gen 산출물)은 **직접 수정하지 않는다.**

## 스택별 기본값 (해당 스택 쓸 때 `templates/<stack>/` 복사)

실제 config는 산문이 아니라 **파일**로 둔다. 아래는 "무엇을/왜"만 요약하고, 값은 링크한 템플릿 파일이 정본이다.
> 템플릿은 SuperMarkit 실 config 스냅샷(2026-07-13)이다. 복사 후 설치된 버전에 맞춰 조정하고 `pnpm lint`/`pnpm build`로 한 번 확인한다.

### TypeScript / NestJS (백엔드) → `templates/nestjs/`
- Node 22.x / TS ~5.7 / `module: commonjs`(`moduleResolution: node`) / `target: ES2023` / 데코레이터 메타데이터 on. 경로 alias `src/*`. NestJS 11.
- tsconfig strict 포인트: `strictNullChecks`·`noImplicitAny`·`forceConsistentCasingInFileNames` on. (`strictBindCallApply`·`noFallthroughCasesInSwitch`는 off.)
- ESLint(flat): `eslint.recommended` + `tseslint.recommendedTypeChecked`(`projectService: true`) + `prettier/recommended`. `no-explicit-any`·`no-unsafe-enum-comparison`·`require-await` off, `no-floating-promises`·`no-unsafe-*` warn, `no-unused-vars` error(`^_` 무시), `prettier/prettier` error.
- Prettier: 4-space, `singleQuote`, `trailingComma: all`, `printWidth: 200`.
- 폴더 구조: 기능별 모듈 `src/<feature>/`에 `.controller.ts`/`.service.ts`/`.module.ts` + `dto/`. 테스트 `.service.spec.ts`/`.unit.spec.ts`.
- 모듈 간 결합은 직접 import보다 이벤트버스 선호(`@EventHandler(EventName)`).
- 응답 envelope 통일(`TransformInterceptor`), 전역 `ValidationPipe(whitelist)`, 전역 `HttpExceptionFilter`, 에러 코드 enum 일원화, 인증 가드 전역 + `@Public()` 예외.
- 명령어: `pnpm build`(nest build), `pnpm lint`(`eslint --fix`), `pnpm format`, `pnpm test`(jest). DB(Drizzle): `schema.ts 수정 → db:generate → db:migrate`.

### React / Vite (프론트 앱) → `templates/vite-react/`
- React 19 / Vite 5 / TS ~5.6. `target: ES2020` / `module: ESNext` / `moduleResolution: Bundler` / `jsx: react-jsx`. project references(`tsconfig.app.json`/`tsconfig.node.json`).
- strict 세트: `strict`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, `noUncheckedSideEffectImports`.
- 경로 alias `@/*` → `./src/*` (tsconfig + `vite.config` + `components.json` 일치).
- ESLint(flat): `js.recommended` + `tseslint.recommended` + `react-hooks` + `react-refresh`(`only-export-components: warn`, `allowConstantExport: true`).
- 네이밍/구조: 컴포넌트 파일 **PascalCase.tsx**. 공유 `components/shared/`, UI 프리미티브 `components/ui/`. 스토어 `<name>.store.ts`, API `api/<resource>.ts` + 공유 `api/client.ts`.
- 서버 상태 TanStack Query, `queryKey` = `['리소스명', '필터/액션']`. 폼 `react-hook-form` + `zod`.
- API 응답 `{ success: boolean, data: T }`. axios interceptor로 토큰 주입 + 401 처리.
- 명령어: `pnpm build`(`tsc -b && vite build`), `pnpm lint`(`eslint .`), `pnpm dev`.

### Next.js (공개 사이트) → `templates/next/`
- Next 16 / React 19 / TS 5.x. `target: ES2017` / `module: esnext` / `moduleResolution: bundler` / `jsx: react-jsx` / `strict` / `noEmit` / `isolatedModules` / next plugin. alias `@/*`.
- ESLint(flat `eslint.config.mjs`): `eslint-config-next/core-web-vitals` + `/typescript`. ignore: `.next/**`, `out/**`, `build/**`, `next-env.d.ts`.
- **주의:** Next.js는 버전마다 스캐폴딩이 크게 바뀐다(이 스냅샷은 Next 16 · flat config 기준) → 코드 전에 설치된 버전 문서/deprecation 확인. 가능하면 `create-next-app` 산출물에 이 값들을 병합.

### 무빌드 프로젝트 (예: Chrome Extension MV3)
- lint/format/husky 없이 소스 직접 로드도 허용. 대신 환경 전환은 스크립트로(`config.<env>.js` 복사 등), 하드코딩 편집 금지.

## 알려진 불일치 (정리하면 좋은 것)
- Prettier 설정 파일은 백엔드(api)에만 있음. 프론트(app/web)는 ESLint에만 의존 → repo 간 포맷 규칙 미통일.
- 들여쓰기: 백엔드 4-space(Prettier 강제) vs 프론트 2-space(관례). 새 프로젝트는 하나로 통일 권장.
- commitlint 미설치라 커밋 컨벤션은 관례 의존.

## 이 규칙 적용하기
1. 이 문서를 대상 repo `docs/conventions/coding-conventions.md`로 복사하고, 상단 출처 줄을 복사일로 채운다.
2. **공통 규칙**은 그대로 채택. husky+lint-staged, Conventional Commits는 셋업 필요 시 위 값 사용.
3. 쓰는 스택의 `templates/<stack>/` config 파일을 대상 repo에 복사해 eslint/prettier/tsconfig 초기값으로 삼는다.
4. `AGENTS.md`의 `## 공통 규칙` 섹션에 포인터를 추가한다. 전체 블록은 `templates/AGENTS.snippet.md` 참고, 이 규칙 한 줄은:
   ```markdown
   - 코딩 컨벤션(lint·포맷·스택별 tsconfig 등): docs/conventions/coding-conventions.md
   ```
