# -*- coding: utf-8 -*-
import os,re,html,shutil,sys,glob,unicodedata
ROOT='/sessions/vibrant-wizardly-cerf/mnt/harry/watercourse-ebook'
sys.path.insert(0,ROOT+'/shared/lib')
import extract_hwp as E
EX='/tmp/faith/ex/OPS'
def paras(fn):
    p=os.path.join(EX,fn)
    if not os.path.exists(p): return []
    t=open(p,encoding='utf-8').read()
    out=[]
    for x in re.findall(r'<p\b[^>]*>(.*?)</p>', t, re.S):
        v=html.unescape(re.sub(r'<[^>]+>','',x)).replace('​',' ')
        v=re.sub(r'\s+',' ',v).strip()
        if v: out.append(v)
    return out
# nav 순서로 계단 제목+본문파일 매핑
nav=open(os.path.join(EX,'nav.xhtml'),encoding='utf-8').read()
items=[(href,re.sub(r'<[^>]+>','',txt).strip()) for href,txt in re.findall(r'<a [^>]*href="([^"#]+)[^"]*"[^>]*>(.*?)</a>',nav,re.S)]
# 계단 페어
chapters=[]
i=0
order=[(h,t) for h,t in items]
for n,(h,t) in enumerate(order):
    if re.match(r'^[가-힣]+번째 계단$', t):
        sub=''
        if n+1<len(order) and order[n+1][1].startswith(':'):
            sub=order[n+1][1].lstrip(': ').strip()
            bodyfile=order[n+1][0]
        else:
            bodyfile=h
        title=f"{t} — {sub}" if sub else t
        chapters.append((title, bodyfile))
# 머리말
pref=[p for p in paras('content3.xhtml') if len(p)>=10 and '물줄기' not in p]
refpre=re.compile(r'^([가-힣]{2,}\s*\d+\s*장\s*\d+(?:\s*[~∼\-]\s*\d+)?\s*절)\s*(.+)$')
def build_blocks(ps):
    out=[]; first=True
    for p in ps:
        if '물줄기교회' in p or p in ('소개','Untitled'): continue
        m=refpre.match(p)
        if m:
            ref,rest=m.group(1),m.group(2).strip()
            out.append(('ref_or_passage', ref, rest, first)); first=False
        else:
            out.append(('p',p,'',False))
    return out
# manuscript 작성
L=[];ap=L.append
shutil.os.makedirs(os.path.join(ROOT,'books/02. 믿음의 계단/images'),exist_ok=True)
shutil.copyfile(os.path.join(ROOT,'books/17. 아모스/images/logo.png'), os.path.join(ROOT,'books/02. 믿음의 계단/images/logo.png'))
def esc(s): return html.escape(s,quote=False)
ap('<div class="title-page">')
ap('<p class="logo"><img src="images/logo.png" alt="물줄기교회"/></p>')
ap('<p class="bk">믿음의 계단</p>')
ap('<p class="au">조춘숙 목사</p>')
ap('<p class="pub">물줄기교회 출판부</p>')
ap('<p class="vid">동영상 설교는 https://vimeo.com/watercourse 또는 YouTube에서 “물줄기교회”를 검색해 주세요.</p>')
ap('</div>');ap('')
ap('# 이 책을 읽는 분들께');ap('')
for p in pref: ap(esc(p)); ap('')
for title,bf in chapters:
    ap(f'# {esc(title)}');ap('')
    for typ,a,b,is_first in build_blocks(paras(bf)):
        if typ=='ref_or_passage':
            if is_first:
                ap(f'<p class="passage">{esc(a)}</p>');ap('')
                if b: ap(f'<blockquote class="scripture-lead"><p>{esc(b)}</p></blockquote>');ap('')
            else:
                ap(f'<p class="ref">{esc(a)}</p>');ap('')
                if b: ap('> '+esc(b));ap('')
        else:
            ap(esc(a));ap('')
ap('# 판권');ap('')
ap('<div class="colophon"><p class="bk">믿음의 계단</p>')
ap('<p class="pubinfo">제1판 발행  2020년 10월</p>')
for line in ['지은이  조춘숙 목사','제작·편집  물줄기교회 출판부','주소  서울 강서구 수명로 68-27 웨스트엔드 2차 문화센터 4층','전화  02-6403-3221','홈페이지  https://vimeo.com/watercourse']:
    ap(f'<p>{line}</p>')
ap('<p class="ver">전자책 버전 1.0.0</p></div>');ap('')
bdir=os.path.join(ROOT,'books/02. 믿음의 계단')
open(os.path.join(bdir,'manuscript.md'),'w',encoding='utf-8').write('\n'.join(L))
env='''TITLE="믿음의 계단"
BOOK_NAME="믿음의 계단"
AUTHORS="조춘숙"
AUTHOR_TITLE="목사"
PUBLISHER="물줄기교회 출판부"
LANGUAGE="ko"
OUTPUT_NAME="믿음의 계단"
TAGS="기독교,설교,신앙"
COMMENTS="물줄기교회 조춘숙 목사의 '믿음의 계단' 설교집."
EDITION="제1판"
VERSION="1.0.0"
RELEASE_DATE="2020-10"
REVIEWED=""
REVIEW_DATE=""
HWP_SOURCE=""
BIBLE_REF=""
VIDEO="동영상 설교는 https://vimeo.com/watercourse 또는 YouTube에서 “물줄기교회”를 검색해 주세요."
PREFACE_SIGN=""
COLOPHON=""
COVER_VERSE="이 강물이 이르는 곳마다|모든 것이 살리라|에스겔 47장 9절"
COVER_BG="2a3a45"
COVER_ACCENT="c9a25a"
'''
open(os.path.join(bdir,'book.env'),'w',encoding='utf-8').write(env)
print("믿음의 계단: 계단", len(chapters), "머리말", len(pref))
for t,bf in chapters: print("  -",t,"<-",bf)
