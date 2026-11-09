#!/usr/bin/env bash
set -euo pipefail

# agent-workflow 평가 실행기 — 시나리오마다 작업 디렉터리를 새로 만들고 `claude -p` 새 세션으로 돌린다.
#
#   run.sh <출력-디렉터리> [A C D]     (기본: 전부. B는 규칙에서 뺐다 — README 기록)
#
# 결과: <출력>/<case>.jsonl(원본 stream-json) · <case>.txt(어시스턴트 텍스트 + 도구 목록).
# 판정 기준은 같은 폴더 README.md. 판정은 사람이 한다.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?출력 디렉터리를 준다}"; shift
CASES=("$@"); [[ ${#CASES[@]} -gt 0 ]] || CASES=(A C D)
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"

git_init() { git -C "$1" init -q && git -C "$1" -c user.name=eval -c user.email=eval@local add -A \
             && git -C "$1" -c user.name=eval -c user.email=eval@local commit -qm init; }

fixture_A() {  # 인증 모듈 3개 파일 + 테스트. 세션이 직접 여러 파일에 걸쳐 고치게 한다
  local d="$1"; mkdir -p "$d/app/auth" "$d/app/api" "$d/tests"
  touch "$d/app/__init__.py" "$d/app/auth/__init__.py" "$d/app/api/__init__.py" "$d/tests/__init__.py"
  cat > "$d/app/auth/token.py" <<'PY'
TTL = 3600


def issue(user_id, now):
    return {"sub": user_id, "exp": now + TTL}


def is_expired(tok, now):
    return now >= tok["exp"]
PY
  cat > "$d/app/auth/session.py" <<'PY'
from app.auth import token


def refresh(tok, now):
    if token.is_expired(tok, now):
        raise PermissionError("expired")
    return token.issue(tok["sub"], now)
PY
  cat > "$d/app/api/login.py" <<'PY'
from app.auth import token


def login(user_id, password_ok, now):
    if not password_ok:
        raise PermissionError("bad credentials")
    return token.issue(user_id, now)
PY
  cat > "$d/tests/test_auth.py" <<'PY'
import unittest

from app.api.login import login
from app.auth.session import refresh


class AuthTest(unittest.TestCase):
    def test_login_and_refresh(self):
        tok = login("u1", True, now=0)
        self.assertEqual(refresh(tok, now=10)["sub"], "u1")

    def test_expired(self):
        tok = login("u1", True, now=0)
        with self.assertRaises(PermissionError):
            refresh(tok, now=3600)


if __name__ == "__main__":
    unittest.main()
PY
  git_init "$d"
}

fixture_D() {  # 조사 3갈래지만 grep 몇 번이면 끝나는 가상 서비스(라우트 40·서비스 20·설정 키 30, 약 560줄)
  # 이 저장소를 쓰지 않는다 — 규칙 원본을 점검하면 판단이 섞인다.
  local d="$1" i n
  mkdir -p "$d/app/routes" "$d/app/services" "$d/config" "$d/tests"
  touch "$d/app/__init__.py" "$d/app/routes/__init__.py" "$d/app/services/__init__.py" "$d/tests/__init__.py" "$d/config/__init__.py"
  printf 'def require_auth(fn):\n    return fn\n' > "$d/app/auth.py"
  : > "$d/config/settings.py"
  for i in $(seq -w 1 30); do echo "KEY_$i = $((10#$i))" >> "$d/config/settings.py"; done
  for i in $(seq -w 1 40); do
    n=$((10#$i % 25 + 1)); n=$(printf '%02d' "$n")
    { echo "from app.auth import require_auth"; echo "from config import settings"; echo
      (( 10#$i % 7 == 0 )) || echo "@require_auth"
      echo "def list_r$i(req):"; echo "    return {\"v\": settings.KEY_$n}"; echo
      echo "@require_auth"; echo "def get_r$i(req, id):"; echo "    return {\"id\": id}"; } > "$d/app/routes/r$i.py"
  done
  for i in $(seq -w 1 20); do
    printf 'from config import settings\n\n\ndef run_s%s():\n    return settings.KEY_%s\n' "$i" "$(printf '%02d' $((10#$i + 5 > 30 ? 30 : 10#$i + 5)))" > "$d/app/services/s$i.py"
    (( 10#$i % 3 == 0 )) && printf 'from app.services import s%s\n\n\ndef test_run():\n    assert s%s.run_s%s()\n' "$i" "$i" "$i" > "$d/tests/test_s$i.py"
  done
  git_init "$d"
}

fixture_C() {
  local d="$1"; mkdir -p "$d"
  printf '# demo\n\nThe worker will recieve a job from the queue and ack it.\n' > "$d/README.md"
  git_init "$d"
}

prompt_A='토큰 갱신 로직을 바꿔줘. (1) 갱신하면 이전 토큰은 폐기한다(토큰 회전) (2) 만료 판정에 30초 유예를 둔다 (3) 로그인에 remember_me 옵션을 추가해 켜면 30일짜리 토큰을 준다. 테스트도 맞춰서 고치고 `python3 -m unittest`로 확인한 뒤 마무리 보고해줘. 커밋은 하지 마.'
prompt_D='이 저장소를 세 갈래로 조사해줘. 고치지는 말고 결과만 보고해. (1) app/routes의 모든 핸들러에 @require_auth가 붙어 있는지 (2) config/settings.py의 설정 키 중 코드에서 안 쓰이는 것 (3) app/services 중 테스트가 없는 모듈이 어디인지'
prompt_C="README.md의 'recieve' 오타를 'receive'로 고쳐줘."

# 세션 길이 상한 — D는 시작할 때의 판단만 보면 되므로 짧게 끊는다(비용 상한).
turns_A=25; turns_C=6; turns_D=8
tools_A=(Read Edit Write Grep Glob "Bash(python3 -m unittest:*)" "Bash(python3 -c:*)" "Bash(git diff:*)" "Bash(git status:*)")
tools_D=(Read Grep Glob "Bash(ls:*)")
tools_C=(Read Edit Grep Glob)

extract() {  # stream-json → 어시스턴트 텍스트(순서대로) + 도구 호출 목록
  python3 -I - "$1" <<'PY'
import json, sys
texts, tools, result = [], [], None
for line in open(sys.argv[1], encoding="utf-8"):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    if ev.get("type") == "assistant":
        for b in ev.get("message", {}).get("content", []):
            if b.get("type") == "text" and b["text"].strip():
                texts.append(b["text"].strip())
            elif b.get("type") == "tool_use":
                inp = b.get("input", {})
                tools.append(f'{b["name"]} {inp.get("description") or inp.get("skill") or inp.get("command") or inp.get("file_path") or ""}'.strip())
    elif ev.get("type") == "result":
        result = f'{ev.get("subtype")} · turns={ev.get("num_turns")} · cost_usd={ev.get("total_cost_usd")}'
print("## 텍스트\n")
print("\n\n---\n\n".join(texts) or "(없음)")
print("\n## 도구 호출\n")
print("\n".join(f"- {t}" for t in tools) or "(없음)")
print(f"\n## 결과\n\n{result}")
PY
}

for c in "${CASES[@]}"; do  # 돌리기 전에 전부 확인한다 — 중간에 멈추면 앞 시나리오 사용량만 쓴다
  declare -F "fixture_$c" >/dev/null || { echo "알 수 없는 시나리오: $c (있는 것: A C D)" >&2; exit 2; }
done

for c in "${CASES[@]}"; do
  work="$OUT/work/$c"; rm -rf "$work"; mkdir -p "$(dirname "$work")"
  "fixture_$c" "$work"
  p="prompt_$c"; t="turns_$c"
  declare -n tools="tools_$c"      # 도구 규칙에 공백이 있어(`Bash(python3 -m …)`) 배열로 넘긴다
  echo "== $c ($work)"
  (cd "$work" && claude -p "${!p}" --output-format stream-json --verbose \
      --max-turns "${!t}" --permission-mode default --allowedTools "${tools[@]}" \
      > "$OUT/$c.jsonl" 2> "$OUT/$c.err") || echo "   (claude 종료 코드 $? — 상한 도달일 수 있다. $c.err 확인)"
  extract "$OUT/$c.jsonl" > "$OUT/$c.txt"
  echo "   → $OUT/$c.txt"
done
