#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""원고 변경 감지 매니페스트.

각 책의 **원본(original/)·manuscript.md·cover.jpg·book.env** 해시(SHA-256)를 기록해 두고,
나중에 다시 계산해 **달라진 책 = EPUB 재제작 필요**를 가려낸다.
공통 디자인 `shared/style.css`가 바뀌면 모든 책을 다시 빌드해야 하므로 함께 기록한다.

산출물(저장소 루트):
  manifest.json      ← 전체 해시. 변경 감지의 단일 기준(사람·AI·CI 공용).
  (사람이 보는 책 목록은 루트 README.md 에 둔다.)

사용법:
  python3 shared/lib/manifest.py write     # 현재 상태를 매니페스트로 저장(빌드/검토 후 실행)
  python3 shared/lib/manifest.py check     # 매니페스트와 비교 → 변경된 책 출력(변경 있으면 종료코드 1)

CI/AI 흐름:
  check 에서 변경된 책이 나오면 그 책만 ./build.sh 로 다시 빌드한 뒤 write 로 매니페스트 갱신.
"""
import os, sys, json, hashlib, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = os.path.join(ROOT, "books")
MANIFEST = os.path.join(ROOT, "manifest.json")
STYLE = os.path.join(ROOT, "shared", "style.css")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def file_rec(path):
    return {"sha256": sha(path), "bytes": os.path.getsize(path)}


def load_env(book_dir):
    env = {}
    p = os.path.join(book_dir, "book.env")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def scan():
    books = []
    for folder in sorted(os.listdir(BOOKS)):
        bd = os.path.join(BOOKS, folder)
        if not os.path.isdir(bd):
            continue
        env = load_env(bd)
        rec = {
            "folder": folder,
            "title": env.get("TITLE", ""),
            "edition": env.get("EDITION", ""),
            "version": env.get("VERSION", ""),
            "release_date": env.get("RELEASE_DATE", ""),
            "reviewed": env.get("REVIEWED", "") or "no",
        }
        # 원본(original/) 전체
        srcs = []
        od = os.path.join(bd, "original")
        if os.path.isdir(od):
            for f in sorted(os.listdir(od)):
                fp = os.path.join(od, f)
                if os.path.isfile(fp):
                    srcs.append({"path": f"original/{f}", **file_rec(fp)})
        rec["sources"] = srcs
        # 입력물
        for key, rel in (("manuscript", "manuscript.md"),
                          ("cover", "cover.jpg"),
                          ("book_env", "book.env")):
            fp = os.path.join(bd, rel)
            rec[key] = file_rec(fp) if os.path.exists(fp) else None
        books.append(rec)
    return {
        "generated": datetime.date.today().isoformat(),
        "style_css": file_rec(STYLE) if os.path.exists(STYLE) else None,
        "books": books,
    }


def write():
    data = scan()
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"매니페스트 저장: manifest.json ({len(data['books'])}권)")


def check():
    if not os.path.exists(MANIFEST):
        print("manifest.json 없음 — 먼저 `manifest.py write` 실행.", file=sys.stderr)
        sys.exit(2)
    old = json.load(open(MANIFEST, encoding="utf-8"))
    new = scan()
    oldb = {b["folder"]: b for b in old["books"]}
    changed, added, removed = [], [], []

    def hashes(b):
        return {
            "sources": {s["path"]: s["sha256"] for s in b["sources"]},
            "manuscript": (b["manuscript"] or {}).get("sha256"),
            "cover": (b["cover"] or {}).get("sha256"),
            "book_env": (b["book_env"] or {}).get("sha256"),
        }

    style_changed = (old.get("style_css") or {}).get("sha256") != (new.get("style_css") or {}).get("sha256")
    for b in new["books"]:
        f = b["folder"]
        if f not in oldb:
            added.append(f); continue
        o, n = hashes(oldb[f]), hashes(b)
        why = []
        if o["sources"] != n["sources"]: why.append("원본")
        if o["manuscript"] != n["manuscript"]: why.append("원고")
        if o["cover"] != n["cover"]: why.append("표지")
        if o["book_env"] != n["book_env"]: why.append("설정")
        if why:
            changed.append((f, why))
    newf = {b["folder"] for b in new["books"]}
    removed = [f for f in oldb if f not in newf]

    print("=== 변경 감지 결과 ===")
    if style_changed:
        print("⚠ shared/style.css 변경 → 모든 책 재빌드 권장")
    for f, why in changed:
        print(f"  ✗ {f}  ({', '.join(why)} 변경) → 재빌드 필요")
    for f in added:
        print(f"  + {f}  (신규) → 빌드 필요")
    for f in removed:
        print(f"  - {f}  (매니페스트에 있었으나 사라짐)")
    if not (changed or added or removed or style_changed):
        print("  ✓ 모든 책이 마지막 기록과 동일 — 재제작 불필요.")
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "write":
        write()
    elif cmd == "check":
        check()
    else:
        print(__doc__); sys.exit(2)
