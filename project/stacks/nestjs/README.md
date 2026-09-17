# NestJS 백엔드 config 스캐폴딩

> 기준: Nest 공식 [`nestjs/typescript-starter`](https://github.com/nestjs/typescript-starter) `master` (2026-07-29 확인) + dev-conventions 타입 안전성·포맷 규칙.

이 폴더 파일을 새 NestJS repo 루트에 복사해 시작점으로 쓴다. 공식 스타터를 우선하되, `strictNullChecks`·`noImplicitAny`와 백엔드 4-space 등 팀 공통 규칙을 더한 템플릿이다.

- `tsconfig.json` — 공식 스타터 기준 `nodenext` / ES2023 / `isolatedModules` / 데코레이터 메타데이터. 팀 규칙으로 `strictNullChecks`·`noImplicitAny` on, `strictBindCallApply`·`noFallthroughCasesInSwitch`는 off.
- `tsconfig.build.json` — 공식 스타터와 동일하게 `tsconfig.json` extends + 테스트/spec 제외 (nest build용).
- `eslint.config.mjs` — 공식 flat config(`recommendedTypeChecked` + prettier)를 바탕으로 `no-explicit-any`/`no-unsafe-enum-comparison`/`require-await` off, `no-unsafe-*` warn, 미사용 인자 규칙을 추가.
- `.prettierrc` — 4-space, singleQuote, printWidth 200.

## 프로젝트별로 결정할 것

- 기본 템플릿은 `package.json`에 `"type": "module"`이 없는 일반 Nest 앱을 가정한다. 순수 ESM으로 운영할 프로젝트만 `"type": "module"`과 import 확장자·라이브러리 호환성을 함께 검토한다.
- 전체 `strict: true`는 기존 코드와 라이브러리 타입에 미치는 영향이 크므로 자동 활성화하지 않는다. 필요하면 프로젝트 단위로 켜고 빌드·테스트 오류를 해소한다.
- 경로 별칭은 공식 스타터 기본값이 아니므로 템플릿에 미리 넣지 않는다. 모노레포나 alias가 필요한 프로젝트에서 `paths`와 런타임 해석 설정을 함께 추가한다.

기준 버전: TypeScript 5.7.x, `@types/node` 22.x, NestJS 11.x, eslint 9.x, typescript-eslint 8.x. 복사 후 설치 버전에 맞춰 `pnpm lint`와 `pnpm build`로 확인한다.
