# -*- coding: utf-8 -*-
"""EPUB 각 콘텐츠 문서의 <title>을 그 문서의 첫 <h1>(없으면 책 제목)으로 설정.
Calibre가 md/txt 입력에서 <title>을 '알 수 없음'으로 두는 문제를 보정한다(전 책 공통).
사용법: python3 fix_titles.py <epub> ["책 제목"]
"""
import sys, re, os, html, zipfile, tempfile, shutil

def main():
    epub = sys.argv[1]
    book_title = sys.argv[2] if len(sys.argv) > 2 else ''
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(epub) as z:
        names = z.namelist()
        z.extractall(tmp)
    changed = 0
    for n in names:
        if not n.lower().endswith(('.xhtml', '.html', '.htm')):
            continue
        p = os.path.join(tmp, n)
        s = open(p, encoding='utf-8').read()
        m = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S | re.I)
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else book_title
        if not title:
            continue
        esc = html.escape(title, quote=False)
        new, c = re.subn(r'<title>.*?</title>', lambda _: '<title>' + esc + '</title>',
                         s, count=1, flags=re.S | re.I)
        if c == 0:
            new, c = re.subn(r'(<head[^>]*>)', lambda mm: mm.group(1) + '<title>' + esc + '</title>',
                             s, count=1, flags=re.I)
        if c and new != s:
            open(p, 'w', encoding='utf-8').write(new)
            changed += 1
    # mimetype 먼저(STORED), 나머지 DEFLATED로 재압축
    tmpf = epub + '.tmp'
    with zipfile.ZipFile(tmpf, 'w') as z:
        mt = os.path.join(tmp, 'mimetype')
        if os.path.exists(mt):
            z.write(mt, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for n in names:
            if n == 'mimetype':
                continue
            z.write(os.path.join(tmp, n), n, compress_type=zipfile.ZIP_DEFLATED)
    os.replace(tmpf, epub)
    shutil.rmtree(tmp)
    print(f"<title> 정리: {changed}개 문서 ({os.path.basename(epub)})")

if __name__ == '__main__':
    main()
