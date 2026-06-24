# -*- coding: utf-8 -*-
"""06 고린도전서 강해집 2 전용 추출기 (비표준 대응).

표준 추출기(shared/lib/extract_hwp.py)가 처리하지 못하는 부분을 보정한다:
  1) 목차 헤더가 'C.O.N.T.E.N.T.S' 라 표준 차례 파서가 못 잡음 → TOC 수동 주입(15~27강).
  2) 장 도입 성경구절이 '… 절 말씀' 접미사를 가짐 → opener(접두 일치)로 처리.
  3) 도입 성경/인용이 여러 문단으로 쪼개짐(절 번호로 시작) → 연속 절 문단을 하나로 병합.
  4) 머리말에 러닝헤더('이 책을 읽는 분들께','고린도전서강해집 2')가 샘 → 제거.

사용법(저장소 루트에서):
  python3 "books/06. 모든 사명을 사랑으로 감당하라(고린도전서)/tools/extract_06.py"
결과: 같은 폴더의 manuscript.md 를 생성/덮어쓴다. (결정론적)
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(BOOK_DIR))
sys.path.insert(0, os.path.join(ROOT, "shared", "lib"))
import hwp5, extract_hwp

TOC = {
 15: '하나님의 뜻을 먼저 생각하라',
 16: '나의 사도됨을 주 안에서 인친 것이 너희라',
 17: '순종하는 자가 받는 생명의 면류관',
 18: '우상숭배 하는 일을 피하라',
 19: '그리스도를 본받는 자',
 20: '그리스도 안에서 여성은 직분을 받을 수 없는가?',
 21: '그리스도 안에서 여성은 직분을 받을 수 없는가?',
 22: '자기를 버리지 못한 사람들',
 23: '성령의 은사를 받은 아름다운 지체들',
 24: '하나님만이 사랑이십니다',
 25: '교회에서 품위 있고 질서 있게 행동하라',
 26: '신령한 몸을 입는 성도들',
 27: '그리스도를 위한 성도들의 화합',
}

norm = extract_hwp.norm
REF_RE = extract_hwp.REF_RE
opener = re.compile(r'^고린도전서\s*\d+\s*장')


def is_verse(t):
    return bool(re.match(r'^\d+[가-힣]', t))


def load_env(p):
    env = {}
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1); v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
            v = v[1:-1]
        env[k.strip()] = v
    return env


def main():
    env = load_env(os.path.join(BOOK_DIR, 'book.env'))
    src = os.path.join(BOOK_DIR, env['HWP_SOURCE'])
    paras = hwp5.extract_paragraphs(src)

    _sq = lambda s: re.sub(r'\s', '', s)
    chap_titles = {_sq(v) for v in TOC.values()}
    booktitles = {_sq(env.get('BOOK_NAME', '')), _sq(env.get('TITLE', ''))} - {''}
    from collections import Counter
    freq = Counter(norm(p) for p in paras if p.strip())
    running = {t for t, c in freq.items() if c >= 4 and len(t) >= 4 and not REF_RE.match(t)}
    drop_exact = {'이 책을 읽는 분들께', '■이 책을 읽는 분들께', '■ 이 책을 읽는 분들께',
                  '고린도전서강해집 2', 'C.O.N.T.E.N.T.S', '조춘숙 목사', '조 춘 숙',
                  '물줄기교회', '대한예수교장로회', '물줄기 <좋은 씨앗>시리즈 ⑥',
                  '물줄기교회 담임목사'}

    def is_header(t):
        s = _sq(t)
        if s in booktitles or s in chap_titles:
            return True
        s2 = re.sub(r'^\d+\.?', '', s)
        return bool(s2) and s2 in chap_titles

    starts = {}
    for k in range(15, 28):
        tk = _sq(TOC[k])
        for i, p in enumerate(paras):
            if p.strip() == str(k):
                nb = [paras[j].strip() for j in range(i + 1, min(i + 10, len(paras))) if paras[j].strip()]
                if any(opener.match(x) for x in nb) or any(_sq(x) == tk for x in nb[:3]):
                    starts[k] = i; break
    order = sorted(starts.items(), key=lambda x: x[1])
    assert len(order) == 13, f"장 인식 실패: {sorted(starts)}"
    first_start = order[0][1]

    pstart = next(i for i, p in enumerate(paras)
                  if '이 책을 읽는 분들께' in p and not re.search(r'\d\s*$', p) and i < first_start)
    preface = []
    for i in range(pstart + 1, first_start):
        t = norm(paras[i])
        if not t:
            continue
        if re.match(r'^\d{4}\s*[.년]', t):
            break
        if t in drop_exact or t in running or '이 책을 읽는 분들께' in t:
            continue
        if _sq(t) == '고린도전서강해집2':
            continue
        preface.append(t)

    def blocks_of(rng, title):
        out = []; expect_quote = True; first = True
        for p in rng:
            t = norm(p)
            if not t:
                continue
            if re.fullmatch(r'\d{1,3}', t):
                continue
            if t in running or t in drop_exact or is_header(t):
                continue
            if title and _sq(t) == _sq(title):
                continue
            if REF_RE.match(t):
                out.append(['ref', t]); expect_quote = True; continue
            if expect_quote:
                out.append(['quote_lead' if first else 'quote', t]); expect_quote = False; first = False; continue
            if out and out[-1][0] in ('quote_lead', 'quote') and is_verse(t):
                out[-1][1] = out[-1][1] + ' ' + t; continue
            out.append(['p', t])
        return out

    chapters = []
    for idx, (k, st) in enumerate(order):
        end = order[idx + 1][1] if idx + 1 < len(order) else len(paras)
        seg = paras[st:end]
        opi = next((j for j, p in enumerate(seg) if opener.match(p.strip())), None)
        if opi is None:
            passage = ''; body = seg[1:]
        else:
            passage = norm(seg[opi]); body = seg[opi + 1:]
        chapters.append((k, TOC[k], passage, [tuple(b) for b in blocks_of(body, TOC[k])]))

    extract_hwp.write_md(BOOK_DIR, env, preface, chapters)
    print(f"생성 완료 — 장 {len(chapters)}, 머리말 {len(preface)}문단")


if __name__ == '__main__':
    main()
