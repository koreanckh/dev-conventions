# NestJS 백엔드 config 스캐폴딩

> 출처: SuperMarkit `supermarkit-api` 실 config 스냅샷 (2026-07-13). 새 프로젝트에 복사 후 설치 버전에 맞춰 조정하고 `pnpm lint`/`pnpm build`로 확인한다.

이 폴더 파일을 새 NestJS repo 루트에 복사해 시작점으로 쓴다.

- `tsconfig.json` — commonjs / `moduleResolution: node` / ES2023 / 데코레이터 메타데이터. `strictNullChecks`·`noImplicitAny` on, `strictBindCallApply`·`noFallthroughCasesInSwitch`는 off.
- `tsconfig.build.json` — `tsconfig.json` extends + 테스트/spec 제외 (nest build용).
- `eslint.config.mjs` — flat. `recommendedTypeChecked` + prettier. `no-explicit-any`/`no-unsafe-enum-comparison`/`require-await` off, `no-unsafe-*` warn.
- `.prettierrc` — 4-space, singleQuote, printWidth 200.

스냅샷 기준 버전: pnpm 10.26.x, TypeScript ~5.7, `@types/node` 22.x, NestJS 11.x, eslint 9.x, typescript-eslint 8.x, husky 9.x, lint-staged 17.x.
