# React / Vite 프론트 config 스캐폴딩

> 출처: SuperMarkit `supermarkit-app` 실 config 스냅샷 (2026-07-13). 복사 후 설치 버전에 맞춰 조정하고 `pnpm lint`/`pnpm build`로 확인한다.

- `tsconfig.json` — project references 루트.
- `tsconfig.app.json` / `tsconfig.node.json` — 앱/툴 분리, strict 세트, `@/*` alias.
- `eslint.config.js` — flat. tseslint + react-hooks + react-refresh.
- `components.json` — shadcn(new-york) alias 매핑. `@/*` alias는 tsconfig·`vite.config.ts`·이 파일 세 곳을 일치시킨다.

스냅샷 기준 버전: pnpm 10.26.x, TypeScript ~5.6, React 19, Vite 5.x, `@tanstack/react-query` 5.x + `@tanstack/react-router` 1.x, eslint 9.x, typescript-eslint 8.x.
