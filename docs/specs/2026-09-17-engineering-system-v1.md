# Personal Engineering System
## LLM-Independent Engineering Memory & Harness Design

- Status: Draft v1
- Purpose: 개인 개발 역량, 판단 기준, 컨벤션, 워크플로우를 지속적으로 학습·축적하고 어떤 LLM/코딩 에이전트에서도 재사용할 수 있는 개발 시스템 설계
- Primary consumer: Developer + LLM/Coding Agent
- Design principle: Engineering System is the source of truth. LLMs are consumers.

---

## 1. 배경

LLM 기반 개발에서는 직접 코드를 작성하는 시간보다 요구사항을 정의하고, 필요한 컨텍스트를 제공하고, 구현 규칙을 명시하고, 결과를 검증하는 시간이 점점 중요해진다.

따라서 목표는 단순히 좋은 프롬프트를 작성하는 것이 아니라 다음을 설계하는 것이다.

- LLM이 안정적으로 개발할 수 있는 환경
- 개발자가 축적해온 지식과 판단 기준
- 프로젝트별 사실과 제약사항
- 반복 가능한 개발 워크플로우
- 자동화된 검증 체계
- 특정 LLM에 종속되지 않는 공통 인터페이스

이 시스템은 개인 개발자의 지식을 외장화한 **Personal Engineering System**이며, Harness는 이 지식을 실제 개발 과정에 적용하는 실행 계층이다.

---

## 2. 목표

### 2.1 Primary Goals

1. 개발자가 공부하거나 경험한 내용을 분야별 Skill로 축적한다.
2. 반복적으로 적용할 개발 원칙과 규칙을 Convention으로 관리한다.
3. 프로젝트 고유 정보는 Project Context로 분리한다.
4. 현재 작업의 목적과 범위는 Task Intent로 분리한다.
5. 기술별 구현 지식은 Stack Knowledge로 관리한다.
6. Feature, Bugfix, Refactor 등 반복 작업은 Workflow로 관리한다.
7. 품질은 프롬프트가 아니라 테스트·린트·빌드·검증 스크립트 등 Evaluation으로 강제한다.
8. 특정 LLM/Coding Agent에 종속되지 않는다.
9. 프로젝트에서 얻은 경험을 검토 후 개인 Engineering Memory로 승격시킬 수 있어야 한다.
10. 모든 프로젝트에서 동일한 개인 개발 철학을 재사용할 수 있어야 한다.

### 2.2 Non-Goals

- 특정 LLM을 위한 거대한 시스템 프롬프트를 만드는 것
- 프로젝트마다 동일한 지식과 규칙을 복사하는 것
- 모든 개발 지식을 처음부터 완성하는 것
- LLM이 자동으로 전역 규칙을 무제한 수정하도록 허용하는 것
- 특정 프레임워크 사용법만 모아놓은 기술 매뉴얼을 만드는 것

---

## 3. 핵심 개념

시스템은 다음 계층으로 구분한다.

```text
Personal Engineering Memory
        ↓
Stack Knowledge
        ↓
Project Context
        ↓
Task Intent
        ↓
Harness / Workflow
        ↓
LLM / Coding Agent
        ↓
Evaluation
```

각 계층은 서로 다른 수명과 책임을 가진다.

### 3.1 Personal Engineering Memory

개발자가 장기간 축적하는 개인 지식과 판단 체계다.

예:

- API를 설계할 때 고려해야 하는 것
- 트랜잭션 경계를 정하는 기준
- 캐시를 도입하는 조건
- 장애 대응 시 확인 순서
- 좋은 로그가 가져야 할 속성
- 인덱스를 만들지 말아야 하는 경우

수명: 수년 이상

### 3.2 Stack Knowledge

일반적인 Engineering Skill을 특정 기술에서 어떻게 구현하는지 설명한다.

예:

- Spring `@Transactional` 사용 기준
- PostgreSQL 인덱스 설계
- Docker bind mount 권한 관리
- Next.js cache 정책
- AWS 배포 패턴

수명: 기술을 사용하는 동안

### 3.3 Project Context

특정 프로젝트에서만 유효한 사실, 구조, 제약사항, 결정사항을 저장한다.

예:

- 프로젝트 목적
- 도메인 구조
- 실제 기술 스택
- 주요 서비스 구성
- backward compatibility 요구
- 배포 방식
- 특정 설계 결정을 내린 이유

수명: 프로젝트 수명

### 3.4 Task Intent

현재 수행하려는 작업의 목적, 범위, 완료 조건을 정의한다.

예:

- Refresh Token Rotation 추가
- 결제 API timeout 문제 수정
- Loki query 성능 개선

수명: 며칠 ~ 몇 주

### 3.5 Harness

Memory, Context, Intent, Tool, Workflow, Evaluation을 조합하여 LLM이 안정적으로 작업하도록 만드는 실행 계층이다.

Harness 자체가 지식의 Source of Truth가 되어서는 안 된다. Harness는 필요한 정보를 연결하고 적용하는 역할을 한다.

---

## 4. 핵심 설계 원칙

### 4.1 Model Independence

Engineering knowledge는 특정 LLM이나 Agent에 종속되지 않는다.

잘못된 예:

```text
Claude는 구현 전에 파일을 읽는다.
GPT에게 architecture.md를 먼저 전달한다.
```

권장 예:

```text
구현 전에 관련 프로젝트 컨텍스트와 기존 코드 패턴을 확인한다.
```

LLM별 차이는 Adapter 계층에서만 처리한다.

### 4.2 Engineering System is the Source of Truth

```text
Engineering System = Source of Truth
LLM / Agent         = Consumer
```

LLM을 변경해도 개발자의 원칙과 지식은 그대로 유지되어야 한다.

### 4.3 Knowledge and Convention Separation

Skill과 Convention은 명확히 구분한다.

```text
Skill
= 어떻게 생각하고 판단해야 하는가

Convention
= 실제 개발에서 반드시 어떤 규칙을 따를 것인가
```

예:

Skill:

```text
외부 API 호출을 긴 DB transaction 내부에서 수행하지 않는다.
```

Convention:

```text
Spring 프로젝트에서는 transaction boundary를 Service/Application layer에 둔다.
```

### 4.4 Domain before Technology

최상위 분류는 기술이 아니라 Engineering Domain을 기준으로 한다.

권장:

```text
backend/
frontend/
database/
infrastructure/
security/
```

기술별 구현은 별도의 `stacks/` 아래에 둔다.

```text
stacks/
  spring/
  nextjs/
  postgresql/
  docker/
  aws/
```

### 4.5 Progressive Learning

모든 내용을 처음부터 완성하지 않는다.

```text
목차 생성
→ 기본 판단 기준 작성
→ 실제 개발
→ 경험 발생
→ Learning Candidate 생성
→ 검토
→ Skill / Convention 보강
```

시스템은 정적인 문서집이 아니라 지속적으로 성장하는 개인 Engineering Memory다.

### 4.6 Project Override

프로젝트 규칙은 전역 개인 규칙보다 우선할 수 있다.

기본 우선순위:

```text
Task-specific Rule
    >
Project Rule
    >
Stack Rule
    >
Global Convention
    >
General Engineering Principle
```

단, 하위 규칙이 상위 규칙을 override하는 경우 이유가 Project Context 또는 Decision에 남아 있어야 한다.

### 4.7 Environment-driven Quality

품질은 가능한 한 프롬프트가 아니라 실행 가능한 검증으로 보장한다.

약한 방식:

```text
잘 구현했는지 확인해.
```

강한 방식:

```text
./scripts/check
./scripts/test
./scripts/lint
./scripts/build
```

LLM이 결과를 스스로 주장하는 것이 아니라 시스템이 검증하도록 한다.

---

## 5. 전체 디렉터리 설계

전역 개인 저장소 예시:

```text
engineering-system/
│
├── README.md
│
├── core/
│   ├── principles/
│   │   ├── engineering.md
│   │   ├── simplicity.md
│   │   └── decision-making.md
│   │
│   ├── conventions/
│   │   ├── general/
│   │   ├── naming/
│   │   ├── git/
│   │   ├── documentation/
│   │   └── security/
│   │
│   ├── workflows/
│   │   ├── feature.md
│   │   ├── bugfix.md
│   │   ├── refactor.md
│   │   ├── investigation.md
│   │   ├── migration.md
│   │   └── incident.md
│   │
│   └── evaluations/
│       ├── implementation.md
│       ├── code-review.md
│       └── production-readiness.md
│
├── skills/
│   ├── requirements/
│   ├── architecture/
│   ├── backend/
│   ├── frontend/
│   ├── database/
│   ├── infrastructure/
│   ├── security/
│   ├── testing/
│   ├── observability/
│   ├── performance/
│   ├── debugging/
│   └── ai-engineering/
│
├── stacks/
│   ├── spring/
│   ├── nextjs/
│   ├── postgresql/
│   ├── redis/
│   ├── docker/
│   ├── aws/
│   ├── grafana/
│   └── loki/
│
├── learnings/
│   ├── inbox/
│   ├── accepted/
│   └── rejected/
│
├── templates/
│   ├── skill.md
│   ├── convention.md
│   ├── workflow.md
│   ├── learning.md
│   ├── project-context.md
│   ├── task-intent.md
│   └── decision.md
│
└── adapters/
    ├── codex/
    ├── claude-code/
    ├── cursor/
    └── generic/
```

`adapters/`의 실제 이름은 사용하는 도구에 맞춰 변경할 수 있다. 핵심은 Adapter가 전역 지식과 분리되어 있다는 점이다.

---

## 6. 분야별 Skill 구조

초기 Skill 분류는 다음처럼 시작한다.

### 6.1 Requirements

- Requirement Clarification
- Acceptance Criteria
- Constraints
- Edge Cases
- Scope Definition
- Non-functional Requirements

### 6.2 Architecture

- System Decomposition
- Boundary Definition
- Coupling / Cohesion
- Data Flow
- Failure Domain
- Scalability
- Availability
- Trade-off Analysis
- Architecture Decision

### 6.3 Backend

- API Design
- Domain Modeling
- Transaction
- Concurrency
- Error Handling
- Caching
- Async Processing
- Idempotency
- Retry
- Rate Limiting
- External API Integration

### 6.4 Frontend

- Component Design
- State Management
- API Integration
- Form Handling
- Error State
- Accessibility
- Performance
- Client Cache
- UX Consistency

### 6.5 Database

- Data Modeling
- Indexing
- Query Optimization
- Transaction
- Locking
- Migration
- Backup / Restore
- Replication
- Retention

### 6.6 Infrastructure

- Linux
- Networking
- Docker
- Deployment
- CI/CD
- Cloud
- DNS
- Load Balancing
- Storage
- Backup

### 6.7 Security

- Authentication
- Authorization
- Secret Management
- Input Validation
- Dependency Security
- Network Security
- Data Protection
- Threat Modeling

### 6.8 Testing

- Unit Test
- Integration Test
- E2E
- Regression Test
- Contract Test
- Load Test
- Failure Test

### 6.9 Observability

- Logging
- Metrics
- Tracing
- Alerting
- Dashboard
- Incident Investigation
- SLI / SLO

### 6.10 Performance

- Profiling
- Bottleneck Analysis
- Query Performance
- Cache Strategy
- Network Performance
- Capacity Planning

### 6.11 Debugging

- Reproduction
- Hypothesis-driven Investigation
- Log Analysis
- Binary Search
- Change Isolation
- Root Cause Analysis

### 6.12 AI Engineering

- Prompt Design
- Context Engineering
- Harness Engineering
- Agent Workflow
- Tool Design
- Evaluation
- Retrieval Strategy
- Context Budget
- Failure Recovery

---

## 7. Project Context 설계

각 프로젝트에는 전역 지식을 복사하지 않는다.

권장 구조:

```text
project/
│
├── AGENTS.md
│
├── .ai/
│   ├── project.md
│   ├── architecture.md
│   ├── stack.md
│   ├── constraints.md
│   ├── conventions.md
│   │
│   ├── domains/
│   │   ├── user.md
│   │   ├── order.md
│   │   └── payment.md
│   │
│   ├── decisions/
│   │   ├── 001-example.md
│   │   └── 002-example.md
│   │
│   ├── tasks/
│   └── learnings/
│
└── scripts/
    ├── check
    ├── test
    ├── lint
    └── build
```

### 7.1 project.md

프로젝트의 목적과 주요 기능을 설명한다.

### 7.2 architecture.md

현재 구조와 주요 component 관계를 설명한다.

### 7.3 stack.md

사용 중인 기술과 중요한 버전/제약을 기록한다.

### 7.4 constraints.md

변경 시 반드시 고려해야 하는 제약사항을 기록한다.

예:

- API backward compatibility 유지
- 특정 DB version 유지
- 무중단 migration 필요
- 외부 파트너 protocol 변경 불가

### 7.5 decisions/

코드가 왜 현재 형태가 되었는지를 기록한다.

```text
Code     = 현재 결과
Decision = 왜 그렇게 했는가
```

LLM이 기존 코드를 단순히 “개선”한다는 이유로 과거의 의도된 결정을 제거하지 못하도록 한다.

---

## 8. AGENTS.md 역할

`AGENTS.md`는 거대한 지식 저장소가 아니라 **Router** 역할을 한다.

권장 책임:

1. 작업 전에 어떤 Project Context를 읽어야 하는지 안내
2. 관련 Personal Skill을 선택하도록 안내
3. 관련 Stack Knowledge를 선택하도록 안내
4. Project Rule이 전역 규칙보다 우선함을 명시
5. 구현 전 기존 코드 패턴 조사 요구
6. 완료 후 Evaluation 실행 요구
7. 재사용 가능한 Learning Candidate 추출 요구

예:

```text
Before implementation:

1. Read `.ai/project.md`.
2. Read `.ai/architecture.md` and relevant domain documents.
3. Read relevant decisions and project constraints.
4. Load relevant engineering skills and stack knowledge.
5. Inspect existing code patterns before making changes.
6. Create or update Task Intent for non-trivial work.
7. Run project validation after implementation.
8. Propose reusable learnings separately from implementation.

Project-specific rules override personal conventions.
Do not modify global engineering memory automatically.
```

---

## 9. Task Intent 설계

복잡한 작업은 짧은 Task Intent 문서로 정의한다.

예:

```text
.ai/tasks/2026-09-refresh-token-rotation.md
```

구조:

```markdown
# Intent

무엇을 왜 변경하는가.

# Requirements

필수 요구사항.

# Constraints

이번 작업에서 지켜야 하는 제약사항.

# Out of Scope

이번 작업에서 변경하지 않는 것.

# Acceptance Criteria

완료 여부를 판단할 수 있는 검증 기준.

# Related Context

관련 architecture, decision, skill, stack 문서.
```

Task Intent는 작업이 끝난 후 삭제하거나 history로 이동할 수 있다.

---

## 10. Learning Lifecycle

프로젝트 경험이 바로 전역 규칙이 되면 안 된다.

권장 흐름:

```text
Development
    ↓
Observation
    ↓
Learning Candidate
    ↓
Classification
    ↓
Review
    ↓
Promotion
```

### 10.1 Classification

Learning Candidate는 다음 중 하나로 분류한다.

#### Project-specific

해당 프로젝트에만 적용된다.

예:

```text
이 프로젝트의 주문 lock은 PostgreSQL advisory lock을 사용한다.
```

저장 위치:

```text
project/.ai/
```

#### Stack-specific

특정 기술을 사용할 때 반복적으로 적용된다.

예:

```text
Docker bind mount에서 host UID/GID와 container user를 맞추는 것을 우선 검토한다.
```

저장 위치:

```text
engineering-system/stacks/docker/
```

#### Universal

기술과 프로젝트를 넘어 재사용할 수 있는 판단 기준이다.

예:

```text
장시간 외부 네트워크 호출을 DB transaction 내부에서 유지하지 않는다.
```

저장 위치:

```text
engineering-system/skills/
```

### 10.2 Promotion Policy

LLM은 전역 Skill/Convention을 직접 수정하지 않는다.

```text
Project Work
    ↓
Learning Candidate
    ↓
Developer Review
    ↓
Accept / Modify / Reject
    ↓
Global Memory Update
```

이 정책은 LLM의 일회성 판단이 장기적인 개인 개발 규칙을 오염시키는 것을 방지한다.

---

## 11. Learning Candidate Template

```markdown
# Observation

무슨 일이 있었는가.

# Problem

어떤 문제가 있었는가.

# Resolution

어떻게 해결했는가.

# Proposed Learning

다음 개발에서도 재사용할 수 있는 판단 기준은 무엇인가.

# Scope

- Project-specific
- Stack-specific
- Universal

# Evidence

왜 이 규칙이 필요한가.

# Proposed Destination

어느 Skill / Stack / Convention 문서에 반영할 것인가.
```

---

## 12. Skill 문서 설계

Skill은 설명서보다 **판단 기준** 중심으로 작성한다.

권장 템플릿:

```markdown
# <Skill Name>

## Purpose

이 Skill이 해결하려는 Engineering Problem.

## Default Position

기본적으로 어떤 선택을 하는가.

## Decision Criteria

어떤 조건에서 선택을 변경하는가.

## Questions to Ask

설계 전에 확인해야 하는 질문.

## Failure Modes

자주 발생하는 잘못된 선택.

## Validation

선택이 적절했는지 확인하는 방법.

## Related Skills

관련 Skill.

## Learnings

실제 경험에서 추가된 규칙.
```

---

## 13. Convention 문서 설계

Convention은 반드시 지켜야 하는 규칙을 정의한다.

권장 템플릿:

```markdown
# <Convention Name>

## Scope

적용 범위.

## Rules

반드시 지켜야 하는 규칙.

## Exceptions

예외가 허용되는 조건.

## Rationale

왜 이 규칙을 사용하는가.

## Verification

어떻게 확인할 수 있는가.
```

가능하면 Convention은 자동 검증 가능한 형태로 발전시킨다.

예:

```text
문서 규칙
→ lint rule
→ test
→ CI check
```

---

## 14. Workflow 설계

Prompt보다 Workflow를 주요 자산으로 본다.

### 14.1 Feature Workflow

```text
Requirement
    ↓
Task Intent
    ↓
Project Context Load
    ↓
Relevant Skill / Stack Load
    ↓
Existing Code Investigation
    ↓
Implementation Plan
    ↓
Implementation
    ↓
Test / Lint / Build
    ↓
Diff Review
    ↓
Learning Extraction
```

### 14.2 Bugfix Workflow

```text
Symptom
    ↓
Reproduction
    ↓
Evidence Collection
    ↓
Hypothesis
    ↓
Root Cause
    ↓
Minimal Fix
    ↓
Regression Test
    ↓
Validation
    ↓
Learning Extraction
```

### 14.3 Refactor Workflow

```text
Reason
    ↓
Current Behavior Lock
    ↓
Test Coverage Check
    ↓
Refactor Boundary
    ↓
Incremental Change
    ↓
Behavior Verification
    ↓
Diff Review
```

---

## 15. Evaluation 설계

LLM의 자기평가를 최소화하고 실행 가능한 검증을 최대화한다.

프로젝트마다 가능한 한 공통 검증 인터페이스를 제공한다.

```text
scripts/
├── check
├── test
├── lint
├── typecheck
├── build
└── security-check
```

이상적인 형태:

```text
LLM Implementation
      ↓
./scripts/check
      ↓
PASS / FAIL
```

`check`는 프로젝트에 따라 다음을 묶을 수 있다.

- Formatting
- Lint
- Type Check
- Unit Test
- Integration Test
- Build
- Static Analysis
- Security Scan

---

## 16. Adapter Layer

Adapter는 특정 LLM/Coding Agent와 Engineering System 사이의 얇은 연결 계층이다.

Adapter의 책임:

- 도구가 읽는 instruction file 형식에 맞춤
- 필요한 Global Memory 위치 안내
- Project Context 로딩 방식 정의
- Skill 선택 방식 정의
- Validation 실행 방식 연결

Adapter가 가져서는 안 되는 책임:

- 핵심 Engineering Rule
- 프로젝트의 Source of Truth
- 특정 기술에 대한 지식 본문
- 장기 Learning 저장

즉:

```text
Core
= What / Why

Adapter
= How to consume
```

Codex, 다른 CLI Agent, IDE Agent로 변경해도 Core는 바뀌지 않는다.

---

## 17. Context Loading Strategy

모든 문서를 항상 LLM에 넣지 않는다.

권장 방식:

```text
Always Loaded
- Core principles
- Project summary
- Critical project constraints

Task-selected
- Relevant domain context
- Relevant skills
- Relevant stack knowledge
- Relevant decisions

On-demand
- Detailed historical learnings
- Rare operational procedures
```

목표는 **Context의 양이 아니라 관련성**을 높이는 것이다.

---

## 18. 프로젝트 작업 예시

예: Spring Boot 프로젝트에서 Redis cache를 추가하는 작업

### Step 1. Task Intent

```text
상품 조회 API의 DB 부하를 줄이기 위해 cache 도입을 검토한다.
```

### Step 2. Project Context

읽을 항목:

- architecture.md
- constraints.md
- 상품 domain 문서
- 기존 cache 관련 decision

### Step 3. Personal Skill

```text
skills/backend/caching.md
skills/database/query-performance.md
skills/observability/metrics.md
```

### Step 4. Stack Knowledge

```text
stacks/spring/cache.md
stacks/redis/key-design.md
```

### Step 5. Implementation

기존 코드 패턴을 확인한 후 변경한다.

### Step 6. Evaluation

```text
./scripts/check
```

### Step 7. Learning Candidate

예:

```text
상품 cache invalidation이 예상보다 복잡하여 TTL-only 전략이 더 적합했다.
```

이후 Project / Stack / Universal 중 어디에 해당하는지 검토한다.

---

## 19. 초기 MVP 범위

처음부터 모든 구조를 완성하지 않는다.

### Phase 1 — Foundation

우선 다음만 만든다.

```text
engineering-system/
├── README.md
├── core/
│   ├── principles/
│   ├── workflows/
│   └── evaluations/
├── skills/
├── stacks/
├── learnings/inbox/
├── templates/
└── adapters/codex/
```

### Phase 2 — Initial Skills

실제 자주 사용하는 분야부터 작성한다.

추천 초기 Skill:

```text
architecture/system-design.md
backend/api-design.md
backend/transaction.md
backend/error-handling.md
database/indexing.md
database/query-performance.md
infrastructure/docker.md
infrastructure/networking.md
observability/logging.md
debugging/root-cause-analysis.md
ai-engineering/context-engineering.md
ai-engineering/harness-engineering.md
```

### Phase 3 — Project Integration

실제 프로젝트 1개에 적용한다.

```text
AGENTS.md
.ai/project.md
.ai/architecture.md
.ai/constraints.md
.ai/decisions/
.ai/tasks/
scripts/check
```

### Phase 4 — Learning Loop

작업 종료 시 Learning Candidate를 생성하고 직접 검토하여 전역 Memory에 승격한다.

---

## 20. 운영 규칙

### Rule 1

전역 Memory를 프로젝트에 복사하지 않는다.

### Rule 2

프로젝트 특수 규칙을 전역 Skill에 넣지 않는다.

### Rule 3

LLM은 전역 Skill/Convention을 직접 수정하지 않는다.

### Rule 4

새로운 지식은 Learning Candidate를 거친다.

### Rule 5

프로젝트 규칙이 전역 규칙과 충돌하면 프로젝트 규칙을 우선하되 이유를 기록한다.

### Rule 6

Skill은 기술 설명보다 판단 기준을 중심으로 작성한다.

### Rule 7

Convention은 가능한 한 자동 Evaluation으로 발전시킨다.

### Rule 8

AGENTS.md에 모든 정보를 넣지 않는다. Router로 사용한다.

### Rule 9

모든 Context를 로딩하지 않는다. 작업과 관련 있는 것만 선택한다.

### Rule 10

특정 LLM 이름이 Core Knowledge에 등장하지 않도록 한다.

---

## 21. 향후 발전 방향

### 21.1 Skill Index

Skill 간 관계를 graph 형태로 정의할 수 있다.

예:

```text
Caching
 ├── Query Performance
 ├── Consistency
 ├── Observability
 └── Failure Handling
```

### 21.2 Automatic Skill Selection

Task Intent를 분석하여 관련 Skill 후보를 자동 선택한다.

### 21.3 Learning Review Automation

작업 완료 후 Agent가 다음을 제안하도록 한다.

```text
이번 작업에서 재사용 가능한 Engineering Learning을 찾아라.
각 항목을 Project / Stack / Universal로 분류하고
기존 문서에 반영할 위치를 제안하라.
전역 문서는 직접 수정하지 마라.
```

### 21.4 Convention Validation

문서에 있는 Convention을 가능한 한 코드 검사로 전환한다.

```text
Convention
→ Rule
→ Script
→ CI
```

### 21.5 Search / Retrieval

Memory가 커지면 모든 파일을 읽지 않고 관련 내용을 검색해서 가져오는 Retrieval 계층을 추가한다.

### 21.6 Engineering Retrospective

월간 또는 분기별로 다음을 검토한다.

- 새로 추가된 Learnings
- 중복 Skill
- outdated Convention
- 프로젝트별 반복 규칙
- 자동화 가능한 검증
- 더 이상 사용하는 않는 Stack Knowledge

---

## 22. Codex에서 다음으로 발전시킬 항목

이 문서를 기반으로 Codex에서는 다음 순서로 구체화한다.

### 22.1 Repository Bootstrap

실제 `engineering-system` repository 구조 생성.

### 22.2 README / Index

전체 Skill과 Convention을 탐색할 수 있는 INDEX 작성.

### 22.3 Templates

다음 템플릿을 실제 파일로 작성.

- Skill
- Convention
- Workflow
- Learning Candidate
- Project Context
- Task Intent
- Decision

### 22.4 Codex Adapter

Codex가 다음 흐름을 따르도록 최소 instruction 설계.

```text
Project Context 확인
→ 관련 Skill 선택
→ 관련 Stack Knowledge 확인
→ 기존 코드 탐색
→ 구현
→ Evaluation
→ Learning Candidate 제안
```

### 22.5 First Skills

현재 실제 경험이 많은 분야부터 초안 작성.

추천:

- Backend API Design
- Transaction
- Database Indexing
- Docker
- Networking
- Logging / Loki / Grafana
- Debugging
- Context Engineering
- Harness Engineering

### 22.6 Pilot Project

실제 프로젝트 하나에 적용하고 불필요한 구조를 제거한다.

목표는 처음부터 완벽한 Framework를 만드는 것이 아니라 **실제 개발하면서 자연스럽게 성장하는 Engineering System을 만드는 것**이다.

---

## 23. 최종 개념 모델

```text
                    ┌──────────────────────────────┐
                    │ Personal Engineering System  │
                    │                              │
                    │ Principles                   │
                    │ Skills                       │
                    │ Conventions                  │
                    │ Workflows                    │
                    │ Evaluations                  │
                    └───────────────┬──────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ Stack Knowledge    │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ Project Context    │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ Task Intent        │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ Harness / Adapter  │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ LLM / Coding Agent │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ Evaluation         │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ Learning Candidate │
                          └─────────┬─────────┘
                                    │
                               Human Review
                                    │
                          ┌─────────▼─────────┐
                          │ Memory Promotion   │
                          └───────────────────┘
```

이 시스템의 목적은 특정 LLM을 잘 사용하는 것이 아니다.

**개발자의 지식, 판단 기준, 경험, 규칙을 지속적으로 축적하고 어떤 LLM에서도 동일한 개발 방식을 재현할 수 있게 만드는 것**이 최종 목표다.
