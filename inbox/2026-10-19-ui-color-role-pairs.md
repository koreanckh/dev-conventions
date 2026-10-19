# 후보: UI 색은 처음부터 역할 토큰 짝으로 쓰고, 짝을 테스트로 지킨다

- **출처:** nskg(releasenotes.me) `#039` 블로그 우선 UI 개편 — 다크 모드를 붙이는 브랜치(2026-09-04~07)
- **재료:** nskg `content/drafts/dev/design-fundamentals/experiments/c6-dark/results-dark.md` (커밋 시점마다 다시 띄워 잰 대비),
  글 초안 `content/posts/dev/dark-mode-contrast-bugs/` (2026-10-19, 발행 전)
- **환경:** Next.js 15.5.20, Tailwind CSS 3.4.19, shadcn/ui 프리미티브 + `cva` + `cn`(clsx + tailwind-merge 3.6)
- **dev-conventions에 지금 있는 것:** UI 색·다크 모드·대비·클래스 묶음 규칙은 없다. `coding-conventions`는 lint·포맷·폴더(`components/ui/`)까지,
  `project/stacks/next`·`vite-react`는 설정 스냅샷과 shadcn 별칭뿐이다.

## 관찰된 실패

규칙이 없어 컴포넌트가 `bg-white`, `text-slate-900` 같은 팔레트 이름을 직접 썼고 그런 클래스가 약 1,300개 쌓였다(`dark:` 0개).
다크 모드를 붙이며 43개 파일을 한 번에 못 옮겨 Tailwind 설정에서 `slate`·`indigo` 일부 단계를 CSS 변수에 이었다(「이주 다리」).
그 커밋 하나에서 아래 결함이 한꺼번에 생겼고, 리뷰가 한 종류씩 나눠 찾아 여섯 번에 걸쳐 고쳤다. 대비는 다크 값.

| 깨진 모양 | 예 | 대비 |
|---|---|---|
| 바탕은 테마를 타고 글자는 고정 | `bg-indigo-600 text-white` 버튼 | 1.69:1 |
| 바탕은 테마를 타고 글자는 다리에 빠진 단계(`indigo-900`) | 옅은 강조 안내 상자 | 1.37:1 |
| 바탕은 고정(`bg-white/80`), 글자는 테마를 탐 | 헤더 | 1.28:1 |
| `@apply` 묶음이 바탕(`bg-white`)만 정하고 글자는 호출부에 맡김 | 전역 `.card` | 1.20:1 |
| 배경 클래스 없는 폼 칸 + `color-scheme` 미선언 | 선택칸·입력칸 | 1.20:1 |
| `ring-offset-2`만 주고 색 없음 → Tailwind 기본 `#fff` | 포커스 링 흰 테 | — |
| 빠진 단계(`slate-950`)를 글자 역할에 잇자, 같은 이름을 바탕으로 쓰던 자리가 뒤집힘 | 코드 출력창 | 1.27:1 |

상태 짝도 깨졌다. 버튼 글자를 역할 색으로 바꾸면서 `disabled:bg-slate-300`을 두자 다크 비활성이 1.68:1이 될 뻔했고,
막으려고 따로 만든 비활성 짝(`disabled:text-white`)은 라이트에서 1.44:1이다(아직 남아 있음).
`cn`으로 `className="bg-white"`를 넘기면 바탕만 바뀌고 `text-accent-fg`는 남아 라이트에서 흰 바탕에 흰 글자가 된다(직접 실행해 확인).

## 승격안 (`coding-conventions`의 UI 절 또는 별도 UI 스킬 후보 — always-on은 아님)

1. **색은 역할 토큰으로만 쓴다.** CSS 변수로 역할(페이지 바탕, 카드 바탕, 글자, 강조, 강조 위 글자 …)을 정의하고 Tailwind에는 역할 이름만 노출한다.
   바탕 역할마다 그 위 글자 역할을 짝으로 둔다(M3 `X` / `on-X`). 컴포넌트에서 팔레트 이름(`slate-900`, `white`)을 직접 쓰지 않는다.
   다크 모드를 당장 안 붙여도 처음부터 이렇게 둔다 — 나중에 붙일 때 이주 다리가 필요 없다.
2. **짝 대비 테스트를 둔다.** 토큰 파일을 읽어 짝마다 라이트·다크 대비를 계산하고 글자 4.5:1 미만이면 실패시킨다.
3. **섞임 검사를 둔다.** 한 요소의 색 클래스(bg·text·border·ring·ring-offset·outline …)에 테마를 타는 색과 고정 색이 같이 있으면 실패시킨다.
   「테마를 타는가」는 색 이름 목록이 아니라 설정이 CSS 변수를 가리키는지와 그 변수의 라이트·다크 값 비교로 판정한다. 전역 CSS의 `@apply`도 읽는다.
4. **묶음은 짝을 통째로 담는다.** `@apply` 클래스와 `cva` 변형은 바탕·글자·호버를 함께 정의한다. 바탕만 두고 글자를 상속에 맡기려면 바탕은 역할 색이어야 한다.
   상태는 새 색 짝을 만들지 말고 같은 짝에 투명도로(`disabled:opacity-40`). 색은 변형으로만 고르게 하고 `className`으로 덮어쓰지 않는다.
5. **빈 자리를 남기지 않는다.** `color-scheme`을 테마 규칙마다 선언한다. 링 여백처럼 크기만 주는 유틸리티에는 색을 같이 준다(`ring-offset-2 ring-offset-bg`).
6. **팔레트 이름을 막는 검사는 빠짐없이.** 금지 정규식에 `950` 같은 끝 단계와 `white`·`black`을 넣는다. nskg의 `token-adoption.test.ts`는 50~900만 잡아
   이 구멍이 남아 있다(2026-10-19 확인).

## 참고 구현 (nskg)

- 토큰: `lib/design/tokens.ts`, `app/globals.css` 상단 변수 블록
- 대비 테스트: `lib/design/__tests__/contrast.test.ts`
- 섞임·링 여백 검사: `app/__tests__/theme-bridge.test.ts`
- 옛 색 이름 금지: `app/__tests__/token-adoption.test.ts`
- 짝을 묶은 버튼: `components/ui/button.tsx`
