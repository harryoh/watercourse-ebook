# -*- coding: utf-8 -*-
"""DOCX(.docx) 문단 추출 — stdlib만. HWP와 동일하게 '원문 문단'을 그대로 뽑는다.
(.doc 구버전은 먼저 .docx로 변환: soffice --headless --convert-to docx 파일.doc)"""
import zipfile, os
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def _para_text(p):
    buf = []
    for node in p.iter():
        t = node.tag
        if t == W + 't':
            buf.append(node.text or '')
        elif t == W + 'tab':
            buf.append('\t')
        elif t in (W + 'br', W + 'cr'):
            buf.append('\n')
    return ''.join(buf)

def extract_paragraphs(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    body = root.find(W + 'body')
    if body is None:
        return []
    paras = []
    # 표 안의 문단까지 문서 순서대로. (드물게 중첩 문단은 중복될 수 있으나 검토 단계에서 확인)
    for p in body.iter(W + 'p'):
        paras.append(_para_text(p))
    return paras

def extract_images(path, outdir):
    saved = []
    os.makedirs(outdir, exist_ok=True)
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.lower().startswith('word/media/') and n.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                data = z.read(n)
                fn = os.path.basename(n)
                open(os.path.join(outdir, fn), 'wb').write(data)
                saved.append(fn)
    return saved

if __name__ == '__main__':
    import sys
    for p in extract_paragraphs(sys.argv[1])[:40]:
        if p.strip():
            print(repr(p[:90]))
