# -*- coding: utf-8 -*-
"""HWP 원문을 '있는 그대로' 덤프 — AI가 읽고 구조를 판단하기 위한 용도.
사용법:
  python3 shared/lib/dump_hwp.py books/<slug>/original/파일.hwp           # 문단 번호+본문 출력
  python3 shared/lib/dump_hwp.py books/<slug>/original/파일.hwp --images books/<slug>/images/_extracted
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hwp5

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    hwp = args[0]
    if '--images' in args:
        outdir = args[args.index('--images') + 1]
        saved = hwp5.extract_images(hwp, outdir)
        print(f"[이미지 {len(saved)}개 저장 → {outdir}] " + ', '.join(saved))
        return
    paras = hwp5.extract_paragraphs(hwp)
    for i, p in enumerate(paras):
        t = p.rstrip()
        if t.strip():
            print(f"[{i:04d}] {t}")
    print(f"\n--- 총 {len(paras)}문단 ---")

if __name__ == '__main__':
    main()
