# -*- coding: utf-8 -*-
"""HWP(.hwp 5.0) -> manuscript.md (+ 이미지 추출).
사용법:  python3 extract_hwp.py <book_dir>
<book_dir>/book.env 의 설정을 읽어 <book_dir>/manuscript.md 를 생성한다.
결정론적: 같은 HWP면 항상 같은 결과. (이 파일이 '변환 가정'의 기록이다.)"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hwp5, docx

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

# 성경 66권 이름 (성경 참조 라벨 인식용)
BIBLE_BOOKS = [
 '창세기','출애굽기','레위기','민수기','신명기','여호수아','사사기','룻기',
 '사무엘상','사무엘하','열왕기상','열왕기하','역대상','역대하','에스라','느헤미야',
 '에스더','욥기','시편','잠언','전도서','아가','이사야','예레미야애가','예레미야',
 '에스겔','다니엘','호세아','요엘','아모스','오바댜','요나','미가','나훔','하박국',
 '스바냐','학개','스가랴','말라기',
 '마태복음','마가복음','누가복음','요한복음','사도행전','로마서',
 '고린도전서','고린도후서','갈라디아서','에베소서','빌립보서','골로새서',
 '데살로니가전서','데살로니가후서','디모데전서','디모데후서','디도서','빌레몬서',
 '히브리서','야고보서','베드로전서','베드로후서','요한일서','요한이서','요한삼서',
 '유다서','요한계시록',
]
# 한 문단 전체가 '책이름 N장 [M~K절]' / '시편 N편' 형태인 성경 참조 라벨
REF_RE = re.compile(
    r'^(?:' + '|'.join(BIBLE_BOOKS) + r')\s*\d+\s*(?:장|편)'
    r'(?:\s*\d+(?:\s*[~∼\-,]\s*\d+)?\s*절)?\s*$')

def _format_date_kr(d):
    """'2024-02' -> '2024년 2월', '2024-02-15' -> '2024년 2월 15일'. 그 외는 원문 반환."""
    m=re.match(r'^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?$', d or '')
    if not m: return d or ''
    y,mo,da=m.group(1),int(m.group(2)),m.group(3)
    return f'{y}년 {mo}월' + (f' {int(da)}일' if da else '')

def _parse_toc(paras):
    """차례 영역에서 (장번호→제목) 추출. 점선형 'N. 제목 --- 쪽' / 공백형 'N  제목   쪽' 모두 지원."""
    start = 0
    for i, p in enumerate(paras):
        if re.sub(r'[\s·]', '', p) == '차례':
            start = i; break
    end = len(paras)
    for i in range(start + 1, len(paras)):
        if paras[i].strip() == '이 책을 읽는 분들께':
            end = i; break
    toc = {}
    for p in paras[start:end]:
        s = p.strip()
        m = re.match(r'^(\d+)\.\s*(.+?)\s*-{2,}\s*\d+\s*$', s)   # 점선형
        if not m:
            m = re.match(r'^(\d+)\s+(.+?)\s+\d+\s*$', s)          # 공백형
        if m:
            toc[int(m.group(1))] = norm(m.group(2))
    return toc

def main(book_dir):
    env=load_env(os.path.join(book_dir,'book.env'))
    src=os.path.join(book_dir, env['HWP_SOURCE'])
    bible=env.get('BIBLE_REF', env.get('BOOK_NAME',''))
    reader = docx if src.lower().endswith('.docx') else hwp5
    paras=reader.extract_paragraphs(src)
    # 이미지 추출
    imgdir=os.path.join(book_dir,'images','_extracted')
    reader.extract_images(src, imgdir)
    opener=re.compile(r'^'+re.escape(bible)+r'\s*\d+\s*장')
    # 1) 차례에서 장 제목 수집 (차례 영역 한정, 점선형/공백형 모두 지원)
    toc=_parse_toc(paras)
    N=max(toc) if toc else 0
    # 2) 본문 장 시작 인덱스 (숫자 단독 문단 + 이후 곧 성경구절)
    starts={}
    for k in range(1,N+1):
        for i,p in enumerate(paras):
            if p.strip()==str(k):
                nb=[paras[j].strip() for j in range(i+1,min(i+10,len(paras))) if paras[j].strip()]
                if any(opener.match(x) for x in nb):
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
        # 첫 인용(챕터 도입 성경)=quote_lead(박스), 본문 중간 성경 참조 뒤 인용=quote(배경 없음)
        out=[]; expect_quote=True; first=True
        for p in rng:
            t=norm(p)
            if not t: continue
            if REF_RE.match(t): out.append(('ref',t)); expect_quote=True; continue
            if expect_quote:
                out.append(('quote_lead' if first else 'quote', t))
                expect_quote=False; first=False; continue
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
    def img_ref(name):
        for ext in ('png','jpg','jpeg'):
            if os.path.exists(os.path.join(book_dir,'images',f'{name}.{ext}')):
                return f'images/{name}.{ext}'
        return None
    logo=img_ref('logo'); church=img_ref('church-info')
    # 표제지
    ap('<div class="title-page">')
    if logo: ap(f'<p class="logo"><img src="{logo}" alt="물줄기교회"/></p>')
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
            elif typ=='quote_lead':
                ap(f'<blockquote class="scripture-lead"><p>{html.escape(t, quote=False)}</p></blockquote>'); ap('')
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
    if church:
        ap('# 교회 안내'); ap('')
        ap(f'<p class="church-info"><img src="{church}" alt="예배안내 및 오시는 길"/></p>'); ap('')
    open(os.path.join(book_dir,'manuscript.md'),'w',encoding='utf-8').write('\n'.join(L))

if __name__=='__main__':
    main(sys.argv[1])
