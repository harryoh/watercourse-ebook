# -*- coding: utf-8 -*-
"""원고 검토 — 자동 점검(문제를 '보고만' 한다. 자동 수정하지 않는다).
사용법: python3 shared/lib/review.py books/<slug>
출판 전, manuscript.md/book.env를 사람이 검토할 때 함께 돌려 의심 항목을 잡는다."""
import sys, os, re

def load_env(p):
    env = {}
    for ln in open(p, encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln:
            continue
        k, v = ln.split('=', 1); v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
            v = v[1:-1]
        env[k.strip()] = v
    return env

def main(book_dir):
    warns, infos = [], []
    W = warns.append; I = infos.append
    envp = os.path.join(book_dir, 'book.env')
    env = load_env(envp) if os.path.exists(envp) else {}

    # 1) book.env 필수 필드
    required = ['TITLE','BOOK_NAME','AUTHORS','PUBLISHER','EDITION','VERSION',
                'RELEASE_DATE','HWP_SOURCE','BIBLE_REF']
    for k in required:
        v = env.get(k, '')
        if not v or '○' in v:
            W(f"book.env: {k} 비어있거나 미작성 ({v!r})")
    if env.get('RELEASE_DATE') and not re.match(r'^\d{4}-\d{2}(-\d{2})?$', env['RELEASE_DATE']):
        W(f"book.env: RELEASE_DATE 형식 확인 ({env['RELEASE_DATE']!r})")

    # 2) manuscript.md
    mp = os.path.join(book_dir, 'manuscript.md')
    if not os.path.exists(mp):
        W("manuscript.md 없음 — 추출 먼저"); return report(book_dir, warns, infos)
    md = open(mp, encoding='utf-8').read()
    if '�' in md:
        W(f"깨진 문자(U+FFFD) {md.count(chr(0xfffd))}개")
    heads = re.findall(r'^#\s+(.+?)\s*$', md, re.M)
    chaps = [h for h in heads if re.match(r'^\d+\.\s', h)]
    I(f"섹션 {len(heads)}개 / 본문 장 {len(chaps)}개")
    if '이 책을 읽는 분들께' not in md: W("머리말('이 책을 읽는 분들께') 누락 의심")
    if '# 판권' not in md: W("판권(# 판권) 섹션 누락 의심")
    nums = [int(re.match(r'^(\d+)\.', h).group(1)) for h in chaps]
    if nums and nums != list(range(1, len(nums) + 1)):
        W(f"장 번호 불연속/누락 의심: {nums}")
    for h in heads:
        if '  ' in h: W(f"제목 이중 공백: '{h}'")
        if h != h.strip(): W(f"제목 앞뒤 공백: '{h}'")
    # 잘림 의심: 아주 짧은 일반 문단
    for ln in md.splitlines():
        s = ln.strip()
        if s and s[0] not in '#<>-*' and 0 < len(s) < 6:
            I(f"짧은 문단 확인: '{s}'")

    # 3) 이미지 참조 존재
    for img in re.findall(r'src="(images/[^"]+)"', md):
        if not os.path.exists(os.path.join(book_dir, img)):
            W(f"참조 이미지 없음: {img}")

    # 4) 표지
    if not os.path.exists(os.path.join(book_dir, 'cover.jpg')):
        W("cover.jpg 없음 — make_cover.py 실행 또는 표지 배치 필요")

    # 5) 검토 완료 표시
    if env.get('REVIEWED', '').lower() not in ('yes', 'y', 'true', '1'):
        I('검토 완료 표시 없음 — 사람 검토 후 book.env에 REVIEWED="yes" 권장')

    return report(book_dir, warns, infos)

def report(book_dir, warns, infos):
    print(f"\n=== 원고 검토 리포트: {book_dir} ===")
    for m in infos: print("  ·", m)
    if warns:
        print(f"\n  ⚠ 확인 필요 {len(warns)}건:")
        for m in warns: print("   -", m)
        print("\n  → manuscript.md / book.env 에서 직접 고친 뒤 다시 점검 (빌드가 자동 수정하지 않음).")
        print("  → 사람 눈 체크리스트: docs/검토체크리스트.md")
        sys.exit(1)
    print("\n  ✓ 자동 점검 통과. 사람 눈 체크리스트도 확인: docs/검토체크리스트.md\n")

if __name__ == '__main__':
    main(sys.argv[1])
