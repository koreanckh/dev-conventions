# Handoff: restructure/es-v2-stage1

- **갱신:** 2026-09-18 08:55 · home
- **브랜치:** restructure/es-v2-stage1 (base: main) · 마지막 커밋: 이 브랜치 HEAD(단계 1 커밋 1개, main에서 분기)
- **워크트리:** 없음
- **TODO:** 없음 (이 repo는 to-do 체계 미적용)
- **먼저 읽을 것:** `docs/specs/2026-09-18-engineering-system-v2.md` §11(적용 단계) · §5(전역 3층) · §7(이식성)

## 다음 한 수

단계 2 — `bootstrap.sh`를 §7.8 계약(`--check`/`--dry-run`/`--copy`/`--uninstall` + lock)대로 구현하고 `--dry-run`으로 이 PC 설치 계획을 먼저 본다.

## 지금 상태

- 단계 1(원본 구성) 완료. `conventions/`·`templates/` → `global/`(always-on·skills·enforcement) + `project/`(템플릿·stacks)로 재배치, 7개 문서를 frontmatter + "필요한 프로젝트 파라미터" 형식의 skill로 변환.
- 전역 `~/.claude/settings.json`에서 이식 가능한 deny/ask/allow를 역수집해 `global/enforcement/claude/settings.fragment.json`에 넣었다. 무엇을 버렸고 무엇이 갈렸는지는 `global/enforcement/README.md`.
- **아직 어떤 환경에도 설치되지 않았다.** `global/`은 원본으로만 존재한다. `~/.claude`, `~/.codex`, `~/.gemini`는 손대지 않았다.
- `/apply-conventions`는 v1(문서 복사) 동작 그대로라 상단에 "단계 5까지 실행 금지" 배너만 달아뒀다.

## 이미 해봤고 안 된 것

- (없음)

## 대화에서만 나온 결정

- `install/targets`를 단계 1에 포함했다 — §7.4 표가 이미 값을 다 정해서 단계 2로 미룰 이유가 없었다.
- skill 저작 골격(`convention.template.md`)은 `project/`가 아니라 `global/skills/SKILL.template.md`로 뒀다. 프로젝트로 스캐폴딩되는 물건이 아니라 skill을 쓰는 골격이라서. 설치기는 `global/skills/` 아래 **디렉터리만** 링크한다는 전제가 붙는다(`install/targets`에 기록).
- `permissions.defaultMode`는 역수집에서 뺐다(이 PC `auto` vs 템플릿 `default` — 환경마다 고를 값).
- `.env` deny는 이 PC의 광범위 `Read(**/.env.*)` 대신 열거형으로 갔다(`.env.example`을 읽을 수 있어야 해서). 설치는 병합만 하므로 이 PC의 기존 광범위 deny는 남는다.
- `curl`/`wget`은 전역에서 판정하지 않기로 했다(이 PC는 allow, 옛 프로젝트 템플릿은 ask — 공통이라 볼 근거 없음).
- `pnpm add`/`pnpm remove` ask는 설계 §5.1대로 넣었다. **설치하면 이 PC에 없던 승인 프롬프트가 생긴다** — 단계 2에서 체감해보고 귀찮으면 뺀다.

## 검증 상태

- 마지막 실행: 변환 전후 본문 diff(출처 줄·"적용하기" 절 제외) → 7개 문서 전부 삭제/추가 1:1 대응, 유실 0. todo-workflow만 +16줄(적용하기 절에 있던 라벨 생성 명령을 "Project 셋업"으로 되살림).
- `python3 -m json.tool settings.fragment.json` 통과, `bash -n hooks/*.sh` 통과, guard 동작 확인(`rm -rf /` → 2, `--no-verify` → 2, `pnpm test` → 0).
- 아직 안 돌림: 실제 설치(단계 2). §13 가정 1~4(심링크 skill 인식, Codex skill 경로, Gemini 지원, 전역 hook 래퍼 보존)는 전부 미판정.

## 환경 (PC 간)

- 필요 도구: bash, git, python3. 외부 서비스·secret 없음.
- 이 repo는 아직 remote가 없다(로컬 전용). 다른 PC로 넘기려면 remote부터 붙여야 한다.
