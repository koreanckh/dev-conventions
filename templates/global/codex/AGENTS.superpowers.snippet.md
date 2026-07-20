## Superpowers policy

- 기본 동작은 lightweight mode다.
- lightweight mode에서는 Superpowers의 "1% chance" 규칙을 적용하지 않는다.
  단순히 관련될 가능성이 있다는 이유만으로 Superpowers 스킬을 호출하지 않는다.

- 범위와 완료 조건이 명확하고, 변경이 국소적이며 쉽게 되돌릴 수 있는 작업은
  현재 세션에서 직접 구현한다.
  이런 작업에는 using-superpowers, brainstorming, writing-plans,
  using-git-worktrees, subagent-driven-development,
  dispatching-parallel-agents, requesting-code-review를 사용하지 않는다.

- 사용자가 요청하지 않았다면 spec/plan 문서를 생성하거나 커밋하지 않고,
  브랜치·워크트리를 만들거나 서브에이전트를 호출하지 않는다.
  저장소의 명시적인 지침이 요구하는 경우는 예외다.

- systematic-debugging은 실제 오류, 실패한 테스트, 재현 가능한 버그,
  예상과 다른 동작이 있을 때만 사용한다.
  일반적인 코드 탐색, 설명, 단순 변경에는 사용하지 않는다.

- 테스트와 검증은 변경 위험에 비례해 수행한다.
  작은 변경은 관련 테스트, 타입 검사 또는 제한된 빌드만 실행한다.
  전체 테스트와 전체 빌드는 변경 범위가 넓거나 저장소 지침이 요구할 때 실행한다.

- 버그 수정이고 기존 테스트 환경이 있다면,
  실용적인 범위에서 먼저 실패하는 회귀 테스트를 추가한다.
  다만 엄격한 TDD 순서를 따르지 않았다는 이유만으로
  유효한 구현을 삭제하거나 처음부터 다시 시작하지 않는다.

- 구현 완료를 보고하기 전에는 최신 검증 결과를 확인한다.
  verification-before-completion은 구현이나 수정 작업에 사용하되,
  단순 질문, 설명, 읽기 전용 조사에는 호출하지 않는다.
  검증만을 위해 별도 리뷰 서브에이전트를 호출하지 않는다.

- 다음 조건에서는 full Superpowers workflow가 유용할 수 있다:
  요구사항이 모호함, 중요한 설계 선택이 필요함, 여러 컴포넌트에 걸친 변경,
  데이터 마이그레이션, 보안·권한 변경, 되돌리기 어려운 작업, 장기 실행 작업.
  에이전트가 full workflow가 필요하다고 판단하면 이유를 간단히 설명하고,
  시작하기 전에 사용자 승인을 한 번 받는다.

- executing-plans에서 subagent-driven-development로 자동 전환하지 않는다.
  두 방식의 비용과 장단점을 설명하고 사용자가 선택하게 한다.

- 사용자의 현재 요청과 더 가까운 저장소의 AGENTS.md 지침이
  이 전역 정책보다 우선한다.
