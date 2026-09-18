# Next.js 공개 사이트 config 스캐폴딩

> 출처: SuperMarkit `supermarkit-web` 실 config 스냅샷 (2026-07-13). 복사 후 설치 버전에 맞춰 조정하고 `pnpm lint`/`pnpm build`로 확인한다.
> ⚠️ Next.js는 버전마다 스캐폴딩이 크게 바뀐다. 이 스냅샷은 **Next 16 기준(flat `eslint.config.mjs`)**. 다른 버전이면 `create-next-app` 산출물을 기준으로 이 값들을 병합한다.

- `tsconfig.json` — ES2017 / bundler / `jsx: react-jsx` / next plugin / `@/*` alias.
- `eslint.config.mjs` — flat. `eslint-config-next/core-web-vitals` + `/typescript`, `.next`/`out`/`build`/`next-env.d.ts` ignore.

스냅샷 기준 버전: pnpm 11.x, Next 16.2.6, React 19, TypeScript 5.x, eslint 9.x, `eslint-config-next` 16.2.6.
