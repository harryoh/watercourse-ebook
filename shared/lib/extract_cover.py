#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""원본 표지(펼침 PDF/AI 또는 단독 이미지)에서 **앞표지만** 추출해 cover.jpg 생성.

book.env 설정:
  COVER_SRC   = 원본 표지 파일(소스 루트 기준 상대경로). 예) 표지/아가서_표지_cre.ai
  COVER_CROP  = x0,x1,y0,y1  (0~1 비율, 앞표지 영역). 단독 앞표지 이미지면 생략.
  COVER_PAGE  = 변환할 페이지(기본 1)  ※ PDF/AI 펼침일 때

사용법:
  python3 shared/lib/extract_cover.py "books/03. 아름다운 노래(아가)" --src-root "/원본/물줄기 좋은 씨앗/03. 아름다운 노래(아가)"

의존성: Ghostscript(gs), Pillow.  PDF/AI는 gs로 300dpi 변환 후 비율로 잘라 폭 1400px JPEG(품질 90) 저장.
"""
import os, sys, subprocess, argparse
from PIL import Image

TARGET_W = 1400

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

def render_spread(src, page, out_png):
    subprocess.run(
        ["gs", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m", "-r300",
         f"-dFirstPage={page}", f"-dLastPage={page}", f"-sOutputFile={out_png}", src],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book_dir")
    ap.add_argument("--src-root", required=True, help="원본 표지가 들어있는 소스 폴더")
    args = ap.parse_args()

    env = load_env(args.book_dir)
    src_rel = env.get("COVER_SRC")
    if not src_rel:
        print("COVER_SRC 미설정 — book.env에 COVER_SRC를 추가하세요.", file=sys.stderr)
        sys.exit(1)
    src = os.path.join(args.src_root, src_rel)
    if not os.path.exists(src):
        print(f"원본 표지 없음: {src}", file=sys.stderr); sys.exit(1)

    ext = os.path.splitext(src)[1].lower()
    if ext in (".pdf", ".ai", ".eps"):
        page = int(env.get("COVER_PAGE", "1"))
        tmp = "/tmp/_cover_spread.png"
        render_spread(src, page, tmp)
        im = Image.open(tmp).convert("RGB")
    else:
        im = Image.open(src).convert("RGB")

    crop = env.get("COVER_CROP")
    if crop:
        x0, x1, y0, y1 = [float(x) for x in crop.split(",")]
        w, h = im.size
        im = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))

    cw, ch = im.size
    if cw > TARGET_W:
        im = im.resize((TARGET_W, int(ch * TARGET_W / cw)), Image.LANCZOS)
    out = os.path.join(args.book_dir, "cover.jpg")
    im.save(out, "JPEG", quality=90)
    print(f"cover.jpg 생성: {out}  {im.size}")

if __name__ == "__main__":
    main()
