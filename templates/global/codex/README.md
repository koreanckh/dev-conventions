# Codex 개인 전역 지침

이 폴더는 특정 프로젝트가 아니라 사용자의 모든 Codex 작업에 적용할 지침 템플릿을 보관한다.

## 적용 대상

- 원본: `AGENTS.superpowers.snippet.md`
- 대상: `~/.codex/AGENTS.md`
- 병합 키: `## Superpowers policy`

에이전트에게 원본을 읽고 대상 파일의 같은 섹션을 교체하거나, 섹션이 없으면 추가하도록 요청한다. 대상 파일의 다른 전역 지침은 보존한다. 변경된 전역 지침은 새 Codex 대화부터 확실하게 적용된다.

이 템플릿은 `/apply-conventions`로 프로젝트에 복사하지 않는다. 새 PC에서는 `dev-conventions`를 clone 또는 pull한 뒤 한 번 적용하고, 템플릿이 바뀌면 같은 방식으로 갱신한다.
