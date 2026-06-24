# -*- coding: utf-8 -*-
"""원문을 '있는 그대로' 덤프 — AI가 읽고 구조를 판단하기 위한 용도. (.hwp / .docx)
사용법:
  python3 shared/lib/dump.py <파일.hwp|.docx>
  python3 shared/lib/dump.py <파일> --images <출력폴더>
구버전 .doc → 먼저 변환:  soffice --headless --convert-to docx 파일.doc
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _mod(path):
    ext = path.lower().rsplit('.', 1)[-1]
    if ext == 'hwp':
        import hwp5 as m; return m
    if ext == 'docx':
        import docx as m; return m
    if ext == 'doc':
        raise SystemExit("구버전 .doc 입니다. 먼저 변환하세요:\n"
                         "  soffice --headless --convert-to docx \"%s\"" % path)
    raise SystemExit("지원하지 않는 형식(.%s). .hwp 또는 .docx 사용." % ext)

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    path = args[0]; m = _mod(path)
    if '--images' in args:
        outdir = args[args.index('--images') + 1]
        saved = m.extract_images(path, outdir)
        print("[이미지 %d개 → %s] %s" % (len(saved), outdir, ', '.join(saved)))
        return
    paras = m.extract_paragraphs(path)
    for i, p in enumerate(paras):
        if p.strip():
            print("[%04d] %s" % (i, p.rstrip()))
    print("\n--- 총 %d문단 ---" % len(paras))

if __name__ == '__main__':
    main()
