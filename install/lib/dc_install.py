#!/usr/bin/env python3
"""dev-conventions 설치기 — `bootstrap.sh`가 호출한다. 직접 실행하지 않는다.

계약(설계 §7.3·§7.8):
  - 가리킬 수 있으면 가리킨다(skills·hook = 심링크/절대경로), 못 가리키면 구역을 정해 복사한다(always-on).
  - settings는 키 단위 병합. 추가한 항목만 lock에 기록하고 그 항목만 갱신·제거한다.
  - 모든 동작은 멱등. 두 번 실행해도 결과가 같고 두 번째 실행은 변경 0.
  - 덮어쓰기 전 `<file>.bak-<timestamp>` 백업. 실제로 바뀔 때만 백업한다.
  - config 디렉터리가 없는 에이전트는 건너뛰고 보고한다. 새로 만들지 않는다.
"""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

BEGIN = "<!-- BEGIN dev-conventions -->"
END = "<!-- END dev-conventions -->"
LOCK_VERSION = 1


# ---------------------------------------------------------------- 유틸

class Reporter:
    """무엇을 바꿨는지 에이전트별로 모아 마지막에 표로 찍는다."""

    def __init__(self, dry: bool):
        self.dry = dry
        self.rows: list[tuple[str, str, str]] = []   # (agent, item, detail)
        self.changed = 0

    def act(self, agent: str, item: str, detail: str, changed: bool = True):
        self.rows.append((agent, item, detail))
        if changed:
            self.changed += 1

    def skip(self, agent: str, item: str, detail: str):
        self.act(agent, item, detail, changed=False)

    def dump(self):
        if not self.rows:
            print("변경 없음 (이미 최신)")
            return
        width = max(len(r[1]) for r in self.rows)
        agent = None
        for a, item, detail in self.rows:
            if a != agent:
                print(f"\n[{a}]")
                agent = a
            print(f"  {item.ljust(width)}  {detail}")


def expand(value: str) -> str:
    """`${VAR:-default}`와 `$HOME`만 전개한다. 셸을 부르지 않는다."""
    def repl(m: re.Match) -> str:
        name, default = m.group(1), m.group(2)
        return os.environ.get(name) or default
    value = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}", repl, value)
    return os.path.expandvars(value)


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def backup(path: Path, rep: Reporter, agent: str):
    if rep.dry or not path.exists():
        return
    dest = path.with_name(f"{path.name}.bak-{now_stamp()}")
    shutil.copy2(path, dest)
    rep.act(agent, "backup", str(dest))


SURFACE = ("global/always-on.md", "global/skills", "global/enforcement",
           "install/targets", "install/apply-conventions.md")


def surface_digest(repo: Path) -> str:
    """실제로 설치되는 파일들만의 해시. repo에 다른 커밋이 쌓여도 낡음으로 보지 않는다."""
    h = hashlib.sha256()
    for rel in SURFACE:
        path = repo / rel
        files = sorted(path.rglob("*")) if path.is_dir() else [path]
        for f in files:
            if not f.is_file():
                continue
            h.update(str(f.relative_to(repo)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def sibling_profiles(raw_config_dir: str, installed: Path, lock_name: str) -> list[tuple[Path, str]]:
    """같은 에이전트의 다른 계정 프로필(예: ~/.claude-personal)을 찾아 돌려준다.

    한 머신에 계정을 나눠 쓰면 설정 디렉터리도 나뉜다. 그 목록은 머신 고유 값이라 저장소에 적지 않는다(§7.7).
    대신 **설치되지 않은 프로필이 있으면 보이게** 만든다 — 조용히 빠지는 것이 제일 나쁘다.
    """
    m = re.search(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}", raw_config_dir)
    env_var = m.group(1) if m else None
    # 프로필 이름은 기본 디렉터리에서 파생된다(~/.claude → ~/.claude*), 지금 설치한 곳이 아니라.
    default_dir = Path(expand(m.group(2))) if m else installed
    found = []
    for cand in sorted(default_dir.parent.glob(default_dir.name + "*")):
        if cand == installed or not cand.is_dir() or (cand / lock_name).exists():
            continue
        found.append((cand, env_var))
    return found


def repo_commit(repo: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- targets

def parse_targets(path: Path) -> dict[str, dict[str, str]]:
    cp = configparser.ConfigParser(inline_comment_prefixes=("#",), allow_no_value=True)
    cp.read_string(path.read_text())
    out: dict[str, dict[str, str]] = {}
    for section in cp.sections():
        vals = {}
        for k, v in cp.items(section):
            v = (v or "").strip()
            if len(v) >= 2 and v[0] == v[-1] == '"':
                v = v[1:-1]            # `#`으로 시작하는 값은 따옴표로 감싼다(인라인 주석과 구분)
            vals[k] = v
        out[section] = vals
    return out


# ---------------------------------------------------------------- always-on 구역

def read_skills(repo: Path) -> list[tuple[str, str, Path]]:
    """`global/skills/<name>/SKILL.md`의 frontmatter에서 name·description을 읽는다."""
    skills = []
    root = repo / "global" / "skills"
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        head = f.read_text().split("---")
        name, desc = d.name, ""
        if len(head) >= 3:
            for line in head[1].splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
        skills.append((name, desc, d))
    return skills


def build_block(repo: Path, pointer_index: bool) -> str:
    body = (repo / "global" / "always-on.md").read_text().rstrip("\n")
    parts = [BEGIN, f"<!-- 원본: {repo}/global/always-on.md · 직접 고치지 말고 원본을 고치고 재설치한다 -->", body]
    if pointer_index:
        lines = ["", "## 규칙 문서 (아래 상황이면 해당 파일을 읽는다)", ""]
        for name, desc, path in read_skills(repo):
            lines.append(f"- {desc}: `{path / 'SKILL.md'}`")
        parts.append("\n".join(lines))
    parts.append(END)
    return "\n".join(parts) + "\n"


def apply_region(path: Path, block: str, legacy_section: str, rep: Reporter, agent: str) -> bool:
    """대상 파일의 관리 구역만 교체한다. 구역 밖 내용은 보존한다."""
    old = path.read_text() if path.exists() else ""
    if BEGIN in old and END in old:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", block, old, count=1, flags=re.S)
    elif legacy_section and legacy_section in old:
        # 1회 이관: 옛 수기 섹션을 관리 구역으로 대체한다(다음 `##`까지, 없으면 끝까지).
        pattern = re.escape(legacy_section) + r".*?(?=\n## |\Z)"
        new = re.sub(pattern, block.rstrip("\n"), old, count=1, flags=re.S)
        rep.act(agent, "always-on", f"기존 '{legacy_section}' 섹션을 관리 구역으로 대체")
    elif old.strip():
        new = old.rstrip("\n") + "\n\n" + block
    else:
        new = block
    if not new.endswith("\n"):
        new += "\n"
    if new == old:
        rep.skip(agent, "always-on", f"최신 ({path})")
        return False
    backup(path, rep, agent)
    if not rep.dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new)
    rep.act(agent, "always-on", f"{'구역 갱신' if BEGIN in old else '구역 설치'} → {path}")
    return True


def remove_region(path: Path, rep: Reporter, agent: str):
    if not path.exists():
        return
    old = path.read_text()
    if BEGIN not in old:
        return
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", old, flags=re.S).strip()
    backup(path, rep, agent)
    if not rep.dry:
        if new:
            path.write_text(new + "\n")
        else:
            path.unlink()
    rep.act(agent, "always-on", f"구역 제거 → {path}")


# ---------------------------------------------------------------- skills

def tree_digest(root: Path) -> str:
    """디렉터리 내용의 해시. 복사 모드에서 갱신이 필요한지 판단한다."""
    h = hashlib.sha256()
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(root)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def link_skills(dest_root: Path, repo: Path, mode: str, rep: Reporter, agent: str,
                known: set[str]) -> list[str]:
    """`known` = lock에 기록된 우리 설치분. 그 밖의 같은 이름 항목은 남의 것으로 보고 건드리지 않는다."""
    managed: list[str] = []
    for name, _desc, src in read_skills(repo):
        dest = dest_root / name
        if dest.is_symlink():
            if os.readlink(dest) == str(src):
                managed.append(name)
                rep.skip(agent, f"skill:{name}", "최신 (심링크)")
                continue
            if mode == "link":
                backup_note = f"다른 대상({os.readlink(dest)}) → 교체"
                if not rep.dry:
                    dest.unlink()
                rep.act(agent, f"skill:{name}", backup_note)
        elif dest.exists():
            if name not in known:
                rep.skip(agent, f"skill:{name}", f"건너뜀 — 우리 설치분이 아닌 항목이 이미 있다 ({dest})")
                continue
            if mode == "copy" and tree_digest(src) == tree_digest(dest):
                managed.append(name)
                rep.skip(agent, f"skill:{name}", "최신 (복사본)")
                continue
            if not rep.dry:                # 우리가 넣은 복사본 → 최신 내용으로 교체
                shutil.rmtree(dest)
        if not rep.dry:
            dest_root.mkdir(parents=True, exist_ok=True)
            if mode == "copy":
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                dest.symlink_to(src, target_is_directory=True)
        managed.append(name)
        rep.act(agent, f"skill:{name}", f"{'복사' if mode == 'copy' else '심링크'} → {dest}")
    return managed


def unlink_skills(dest_root: Path, names: list[str], rep: Reporter, agent: str):
    for name in names:
        dest = dest_root / name
        if dest.is_symlink() or dest.is_dir():
            if not rep.dry:
                if dest.is_symlink():
                    dest.unlink()
                else:
                    shutil.rmtree(dest)
            rep.act(agent, f"skill:{name}", f"제거 → {dest}")
    if dest_root.is_dir() and not rep.dry and not any(dest_root.iterdir()):
        dest_root.rmdir()                  # 우리가 만든 빈 디렉터리만 정리한다
        rep.act(agent, "skills", f"빈 디렉터리 제거 → {dest_root}")


# ---------------------------------------------------------------- settings (JSON)

def merge_json(target: Path, fragment: Path, repo: Path, rep: Reporter, agent: str) -> dict:
    frag = json.loads(fragment.read_text().replace("{{DEV_CONVENTIONS_DIR}}", str(repo)))
    cur = json.loads(target.read_text()) if target.exists() else {}
    before = json.dumps(cur, sort_keys=True)
    managed: dict = {"permissions": {}, "hooks": {}}

    perms = cur.setdefault("permissions", {})
    for key, items in frag.get("permissions", {}).items():
        have = perms.setdefault(key, [])
        added = [i for i in items if i not in have]
        have.extend(added)
        if added:
            managed["permissions"][key] = added
            rep.act(agent, f"settings:{key}", f"{len(added)}개 추가")
        else:
            rep.skip(agent, f"settings:{key}", "이미 전부 있음")

    hooks = cur.setdefault("hooks", {})
    for event, entries in frag.get("hooks", {}).items():
        have = hooks.setdefault(event, [])
        existing_cmds = {h.get("command")
                         for entry in have for h in entry.get("hooks", [])}
        added_cmds = []
        for entry in entries:
            cmds = [h.get("command") for h in entry.get("hooks", [])]
            if all(c in existing_cmds for c in cmds):
                continue
            have.append(entry)             # 배열을 교체하지 않고 항목만 append
            added_cmds.extend(cmds)
        if added_cmds:
            managed["hooks"][event] = added_cmds
            rep.act(agent, f"settings:hooks.{event}", f"{len(added_cmds)}개 append (기존 항목 보존)")
        else:
            rep.skip(agent, f"settings:hooks.{event}", "이미 있음")

    if json.dumps(cur, sort_keys=True) == before:
        return managed
    backup(target, rep, agent)
    if not rep.dry:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n")
    return managed


def unmerge_json(target: Path, managed: dict, rep: Reporter, agent: str):
    if not target.exists() or not managed:
        return
    cur = json.loads(target.read_text())
    before = json.dumps(cur, sort_keys=True)
    for key, items in managed.get("permissions", {}).items():
        have = cur.get("permissions", {}).get(key, [])
        cur["permissions"][key] = [i for i in have if i not in items]
    for event, cmds in managed.get("hooks", {}).items():
        entries = cur.get("hooks", {}).get(event, [])
        kept = []
        for entry in entries:
            inner = [h for h in entry.get("hooks", []) if h.get("command") not in cmds]
            if inner:
                entry["hooks"] = inner
                kept.append(entry)
        cur["hooks"][event] = kept
    if json.dumps(cur, sort_keys=True) == before:
        return
    backup(target, rep, agent)
    if not rep.dry:
        target.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n")
    rep.act(agent, "settings", f"설치분 제거 → {target}")


# ---------------------------------------------------------------- settings (TOML)

def merge_toml(target: Path, fragment: Path, rep: Reporter, agent: str) -> list[str]:
    """TOML은 최상위 키가 테이블보다 앞에 와야 하므로 관리 구역을 **파일 맨 앞**에 둔다."""
    frag_text = fragment.read_text()
    frag = tomllib.loads(frag_text)
    cur = tomllib.loads(target.read_text()) if target.exists() else {}
    old = target.read_text() if target.exists() else ""

    body, managed = [], []
    for key, val in frag.items():
        if isinstance(val, dict):
            continue                      # 테이블은 병합하지 않는다
        if key in cur and f"{BEGIN}" not in old:
            rep.skip(agent, f"config:{key}", f"이미 있음(건드리지 않음): {key} = {cur[key]!r}")
            continue
        body.append(f"{key} = {json.dumps(val)}")
        managed.append(key)
    if not managed:
        rep.skip(agent, "config.toml", "추가할 키 없음")
        return []

    block = "\n".join([f"# {BEGIN}",
                       "# dev-conventions 설치분. 직접 고치지 말고 원본을 고치고 재설치한다.",
                       *body,
                       f"# {END}", ""])
    if f"# {BEGIN}" in old:
        new = re.sub(re.escape(f"# {BEGIN}") + r".*?" + re.escape(f"# {END}") + r"\n?", block, old, count=1, flags=re.S)
    else:
        new = block + "\n" + old
    if new == old:
        rep.skip(agent, "config.toml", "최신")
        return managed
    backup(target, rep, agent)
    if not rep.dry:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new)
    rep.act(agent, "config.toml", f"관리 구역 {'갱신' if BEGIN in old else '설치'}({', '.join(managed)}) → {target}")
    return managed


def unmerge_toml(target: Path, rep: Reporter, agent: str):
    if not target.exists():
        return
    old = target.read_text()
    if f"# {BEGIN}" not in old:
        return
    new = re.sub(re.escape(f"# {BEGIN}") + r".*?" + re.escape(f"# {END}") + r"\n?", "", old, flags=re.S).lstrip("\n")
    backup(target, rep, agent)
    if not rep.dry:
        target.write_text(new)
    rep.act(agent, "config.toml", f"관리 구역 제거 → {target}")


# ---------------------------------------------------------------- commands

def install_commands(dest_dir: Path, repo: Path, rep: Reporter, agent: str) -> list[str]:
    src = repo / "install" / "apply-conventions.md"
    dest = dest_dir / "apply-conventions.md"
    content = src.read_text().replace("{{DEV_CONVENTIONS_DIR}}", str(repo))
    if dest.exists() and dest.read_text() == content:
        rep.skip(agent, "command", "최신 (apply-conventions)")
        return ["apply-conventions.md"]
    backup(dest, rep, agent)
    if not rep.dry:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
    rep.act(agent, "command", f"설치 → {dest}")
    return ["apply-conventions.md"]


# ---------------------------------------------------------------- lock

def lock_path(config_dir: Path, name: str) -> Path:
    return config_dir / name


def read_lock(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def write_lock(path: Path, data: dict, rep: Reporter, agent: str):
    if rep.dry:
        rep.act(agent, "lock", f"(dry-run) {path}", changed=False)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    rep.act(agent, "lock", f"기록 → {path}", changed=False)


# ---------------------------------------------------------------- 명령

def agents_to_do(targets: dict, only: str | None) -> list[str]:
    names = list(targets)
    if only:
        if only not in targets:
            sys.exit(f"error: 모르는 에이전트 '{only}' (있는 것: {', '.join(names)})")
        return [only]
    return names


def cmd_install(repo: Path, targets: dict, args, rep: Reporter) -> int:
    commit = repo_commit(repo)
    for agent in agents_to_do(targets, args.agent):
        t = targets[agent]
        config_dir = Path(expand(t["config_dir"]))
        if not config_dir.is_dir():
            rep.skip(agent, "건너뜀", f"설정 디렉터리 없음 ({config_dir})")
            continue
        lock_file = lock_path(config_dir, t.get("lock", ".dev-conventions.lock"))
        lock = read_lock(lock_file)
        managed = {"skills": [], "settings": {}, "toml_keys": [], "commands": [], "always_on": ""}

        if t.get("always_on"):
            block = build_block(repo, t.get("pointer_index", "no") == "yes")
            target = config_dir / t["always_on"]
            apply_region(target, block, t.get("legacy_section", ""), rep, agent)
            managed["always_on"] = t["always_on"]

        if t.get("skills"):
            known = set(lock.get("managed", {}).get("skills", []))
            managed["skills"] = link_skills(config_dir / t["skills"], repo, args.mode, rep, agent, known)

        if t.get("settings") and t.get("settings_src"):
            target = config_dir / t["settings"]
            src = repo / t["settings_src"]
            if target.suffix == ".json":
                managed["settings"] = merge_json(target, src, repo, rep, agent)
            elif target.suffix == ".toml":
                managed["toml_keys"] = merge_toml(target, src, rep, agent)

        if t.get("commands"):
            managed["commands"] = install_commands(config_dir / t["commands"], repo, rep, agent)

        for cand, env_var in sibling_profiles(t["config_dir"], config_dir, t.get("lock", ".dev-conventions.lock")):
            hint = f"{env_var}={cand} ./bootstrap.sh --agent {agent}" if env_var else f"(설치 방법: {agent}의 설정 디렉터리를 그 경로로 두고 재실행)"
            rep.skip(agent, "다른 프로필", f"{cand} — 설치 안 됨. 쓰는 프로필이면: {hint}")

        write_lock(lock_file, {
            "version": LOCK_VERSION,
            "repo": str(repo),
            "commit": commit,
            "surface": surface_digest(repo),
            "installed_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "mode": args.mode,
            "managed": merge_managed(lock.get("managed", {}), managed),
        }, rep, agent)
    return 0


def merge_managed(old: dict, new: dict) -> dict:
    """이번에 추가한 것 + 이전에 추가해 아직 남아 있는 것."""
    out = dict(new)
    for key in ("skills", "commands", "toml_keys"):
        out[key] = sorted(set(old.get(key, [])) | set(new.get(key, [])))
    merged_settings = {"permissions": {}, "hooks": {}}
    for group in ("permissions", "hooks"):
        keys = set(old.get("settings", {}).get(group, {})) | set(new.get("settings", {}).get(group, {}))
        for k in keys:
            items = list(dict.fromkeys(old.get("settings", {}).get(group, {}).get(k, [])
                                       + new.get("settings", {}).get(group, {}).get(k, [])))
            if items:
                merged_settings[group][k] = items
    merged_settings = {g: v for g, v in merged_settings.items() if v}
    out["settings"] = merged_settings        # 비어 있으면 {} — uninstall이 헛돌지 않게
    return out


def cmd_check(repo: Path, targets: dict, args, rep: Reporter) -> int:
    stale = 0
    commit = repo_commit(repo)
    surface = surface_digest(repo)
    for agent in agents_to_do(targets, args.agent):
        t = targets[agent]
        config_dir = Path(expand(t["config_dir"]))
        lock = read_lock(lock_path(config_dir, t.get("lock", ".dev-conventions.lock")))
        if not lock:
            continue                       # 설치되지 않은 에이전트는 낡음 판정 대상이 아니다
        if lock.get("surface") != surface:
            print(f"낡음: {agent} — 설치된 규칙이 repo와 다르다 "
                  f"(설치 {lock.get('commit', '?')[:7]} · {lock.get('installed_at', '?')}, repo HEAD {commit[:7]}) "
                  f"→ ./bootstrap.sh")
            stale = 1
    return stale


def cmd_uninstall(repo: Path, targets: dict, args, rep: Reporter) -> int:
    for agent in agents_to_do(targets, args.agent):
        t = targets[agent]
        config_dir = Path(expand(t["config_dir"]))
        lock_file = lock_path(config_dir, t.get("lock", ".dev-conventions.lock"))
        lock = read_lock(lock_file)
        if not lock:
            rep.skip(agent, "건너뜀", "설치 기록 없음")
            continue
        managed = lock.get("managed", {})
        if managed.get("always_on"):
            remove_region(config_dir / managed["always_on"], rep, agent)
        if managed.get("skills") and t.get("skills"):
            unlink_skills(config_dir / t["skills"], managed["skills"], rep, agent)
        if t.get("settings"):
            target = config_dir / t["settings"]
            if target.suffix == ".json" and managed.get("settings"):
                unmerge_json(target, managed["settings"], rep, agent)
            elif target.suffix == ".toml" and managed.get("toml_keys"):
                unmerge_toml(target, rep, agent)
        for name in managed.get("commands", []):
            f = config_dir / t.get("commands", "commands") / name
            if f.exists():
                if not rep.dry:
                    f.unlink()
                rep.act(agent, "command", f"제거 → {f}")
        if not rep.dry:
            lock_file.unlink(missing_ok=True)
        rep.act(agent, "lock", f"제거 → {lock_file}", changed=False)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--command", default="install", choices=["install", "check", "uninstall"])
    ap.add_argument("--mode", default="link", choices=["link", "copy"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--agent")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    targets = parse_targets(repo / "install" / "targets")
    rep = Reporter(args.dry_run)

    if args.command == "check":
        return cmd_check(repo, targets, args, rep)

    fn = cmd_install if args.command == "install" else cmd_uninstall
    rc = fn(repo, targets, args, rep)
    print(f"\n=== {'바뀔 내용 (dry-run)' if args.dry_run else '결과'} · repo {repo} · mode {args.mode}")
    rep.dump()
    print(f"\n변경 {rep.changed}건" + (" (아무것도 쓰지 않았다)" if args.dry_run else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
