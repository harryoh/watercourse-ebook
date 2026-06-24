# -*- coding: utf-8 -*-
"""HWP(.hwp 5.0) -> manuscript.md (+ 이미지 추출).
사용법:  python3 extract_hwp.py <book_dir>
<book_dir>/book.env 의 설정을 읽어 <book_dir>/manuscript.md 를 생성한다.
결정론적: 같은 HWP면 항상 같은 결과. (이 파일이 '변환 가정'의 기록이다.)"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hwp5

def load_env(p):
    env={}
    for line in open(p, encoding='utf-8'):
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k,v=line.split('=',1); v=v.strip()
        if len(v)>=2 and v[0]==v[-1] and v[0] in '"\'' : v=v[1:-1]
        env[k.strip()]=v
    return env

def norm(s): return re.sub(r'\s+',' ',s).strip()

def _format_date_kr(d):
    """'2024-02' -> '2024년 2월', '2024-02-15' -> '2024년 2월 15일'. 그 외는 원문 반환."""
    m=re.match(r'^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?$', d or '')
    if not m: return d or ''
    y,mo,da=m.group(1),int(m.group(2)),m.group(3)
    return f'{y}년 {mo}월' + (f' {int(da)}일' if da else '')

def main(book_dir):
    env=load_env(os.path.join(book_dir,'book.env'))
    hwp=os.path.join(book_dir, env['HWP_SOURCE'])
    bible=env.get('BIBLE_REF', env.get('BOOK_NAME',''))
    paras=hwp5.extract_paragraphs(hwp)
    # 이미지 추출
    imgdir=os.path.join(book_dir,'images','_extracted')
    hwp5.extract_images(hwp, imgdir)
    opener=re.compile(r'^'+re.escape(bible)+r'\s*\d+장')
    # 1) 차례에서 장 제목 수집
    toc={}
    for p in paras:
        m=re.match(r'^(\d+)\.\s*(.+?)\s*-{3,}\s*\d+\s*$', p)
        if m: toc[int(m.group(1))]=norm(m.group(2))
    N=len(toc)
    # 2) 본문 장 시작 인덱스 (숫자 단독 문단 + 제목 + 성경구절)
    starts={}
    for k in range(1,N+1):
        for i,p in enumerate(paras):
            if p.strip()==str(k):
                nb=[paras[j].strip() for j in range(i+1,min(i+6,len(paras))) if paras[j].strip()]
                if len(nb)>=2 and opener.match(nb[1]):
                    starts[k]=i; break
    order=sorted(starts.items(), key=lambda x:x[1])
    # 3) 머리말
    pidx=[i for i,p in enumerate(paras) if p.strip()=='이 책을 읽는 분들께']
    first_start=order[0][1]
    preface=[]
    if pidx:
        for i in range(pidx[-1]+1, first_start):
            t=norm(paras[i])
            if not t: continue
            if re.match(r'^\d{4}\s*\.', t): break   # 발행일 서명부 시작 → 머리말 끝
            preface.append(t)
    # 4) 본문 블록 만들기
    def blocks_of(rng):
        out=[]; expect_quote=True
        for p in rng:
            t=norm(p)
            if not t: continue
            if opener.match(t): out.append(('ref',t)); expect_quote=True; continue
            if expect_quote: out.append(('quote',t)); expect_quote=False; continue
            out.append(('p',t))
        return out
    chapters=[]
    for idx,(k,st) in enumerate(order):
        if idx+1<len(order): end=order[idx+1][1]
        else:
            end=len(paras)
            for i in range(st,len(paras)):
                tt=paras[i].strip()
                if tt.startswith('초판') or tt=='지은이': end=i; break
        seg=paras[st:end]
        op=next((i for i,p in enumerate(seg) if opener.match(p.strip())), 1)
        title=toc.get(k, norm(seg[1]) if len(seg)>1 else f'{k}장')
        passage=norm(seg[op]) if op<len(seg) else ''
        chapters.append((k,title,passage,blocks_of(seg[op+1:])))
    write_md(book_dir, env, preface, chapters)
    print(f"manuscript.md 생성 완료 — 장 {len(chapters)}개, 머리말 {len(preface)}문단")
    print("이미지:", ', '.join(sorted(os.listdir(imgdir))) or '(없음)')

def write_md(book_dir, env, preface, chapters):
    L=[]; ap=L.append
    has=lambda f: os.path.exists(os.path.join(book_dir,'images',f))
    # 표제지
    ap('<div class="title-page">')
    if has('logo.png'): ap('<p class="logo"><img src="images/logo.png" alt="물줄기교회"/></p>')
    ap(f'<p class="bk">{env.get("BOOK_NAME","")}</p>')
    ap(f'<p class="sub">{env.get("TITLE","")}</p>')
    ap(f'<p class="au">{env.get("AUTHORS","")} {env.get("AUTHOR_TITLE","목사")}</p>')
    ap(f'<p class="pub">{env.get("PUBLISHER","")}</p>')
    if env.get('VIDEO'): ap(f'<p class="vid">{env["VIDEO"]}</p>')
    ap('</div>'); ap('')
    # 머리말
    ap('# 이 책을 읽는 분들께'); ap('')
    for p in preface: ap(p); ap('')
    sign=env.get('PREFACE_SIGN','').split('|')
    if any(sign): ap('<p class="sign">'+'<br/>'.join(s for s in sign if s)+'</p>'); ap('')
    # 본문
    for (k,title,passage,blocks) in chapters:
        ap(f'# {k}. {title}'); ap('')
        if passage: ap(f'<p class="passage">{passage}</p>'); ap('')
        for typ,t in blocks:
            if typ=='ref': ap(f'<p class="ref">{t}</p>'); ap('')
            elif typ=='quote': ap('> '+t); ap('')
            else: ap(t); ap('')
    # 판권 — 판/발행일/버전은 book.env(EDITION·RELEASE_DATE·VERSION)에서 자동 생성
    ap('# 판권'); ap('')
    ap('<div class="colophon">')
    ap(f'<p class="bk">{env.get("BOOK_NAME","")}</p>')
    ap(f'<p class="subk">{env.get("TITLE","")}</p>')
    edition = env.get('EDITION', '').strip()
    date_kr = _format_date_kr(env.get('RELEASE_DATE', '').strip())
    if edition or date_kr:
        ap(f'<p class="pubinfo">{edition}{(" " if edition and date_kr else "")}발행  {date_kr}</p>')
    for line in env.get('COLOPHON', '').split('|'):
        if line.strip(): ap(f'<p>{line.strip()}</p>')
    version = env.get('VERSION', '').strip()
    if version: ap(f'<p class="ver">전자책 버전 {version}</p>')
    ap('</div>'); ap('')
    # 교회 안내(예배/오시는 길) 이미지가 있으면 뒤에 추가
    if has('church-info.png'):
        ap('# 교회 안내'); ap('')
        ap('<p class="church-info"><img src="images/church-info.png" alt="예배안내 및 오시는 길"/></p>'); ap('')
    open(os.path.join(book_dir,'manuscript.md'),'w',encoding='utf-8').write('\n'.join(L))

if __name__=='__main__':
    main(sys.argv[1])
