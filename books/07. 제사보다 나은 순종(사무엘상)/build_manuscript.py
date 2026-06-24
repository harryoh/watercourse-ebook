# -*- coding: utf-8 -*-
import sys,os,re,shutil,unicodedata
ROOT='/sessions/vibrant-wizardly-cerf/mnt/harry/watercourse-ebook'
sys.path.insert(0,ROOT+'/shared/lib')
import hwp5, extract_hwp as E
from PIL import Image

def nfc(s): return unicodedata.normalize('NFC',s)
allf=[(l,nfc(l)) for l in open('/tmp/local_src.txt',encoding='utf-8').read().splitlines()]
def find(sub):
    for o,n in allf:
        if nfc(sub) in n: return o

bdir=os.path.join(ROOT,'books','07. 제사보다 나은 순종(사무엘상)')
os.makedirs(os.path.join(bdir,'original'),exist_ok=True)
os.makedirs(os.path.join(bdir,'images'),exist_ok=True)
NOISE={'제사보다 나은 순종','제사보다 나은 순종1','제사보다 나은 순종2',
       '물줄기교회 조춘숙 목사','조춘숙 목사','물줄기교회','물줄기교회를 검색해 주세요!'}
def blockify(body,title):
    out=[];expect=False
    for p in body:
        t=E.norm(p)
        if not t: continue
        if re.fullmatch(r'\d{1,3}',t): continue
        if re.match(r'^\d{1,2}_',t): continue        # 러닝 헤더/꼬리말 장머리
        if t in NOISE or t==title: continue
        if E.REF_RE.match(t): out.append(('ref',t)); expect=True; continue
        if expect: out.append(('quote',t)); expect=False; continue
        out.append(('p',t))
    return out

def starts_in(P,lo,hi):
    s={}
    for i,p in enumerate(P):
        m=re.match(r'^(\d{2})_(.+)$',p.strip())
        if m:
            k=int(m.group(1))
            if lo<=k<=hi and k not in s: s[k]=i
    return s

chapters=[]; preface=[]
for tag,sub,lo,hi in [("part1","사무엘상1_합본.hwp",1,16),("part2","사무엘상2_합본.hwp",17,33)]:
    src=find(sub); shutil.copyfile(src, os.path.join(bdir,'original',os.path.basename(src)))
    P=hwp5.extract_paragraphs(src)
    toc=E._parse_toc(P)
    st=starts_in(P,lo,hi); order=sorted(st.items(),key=lambda x:x[1])
    # 머리말은 part1에서만
    if tag=='part1' and order:
        pi=[i for i,p in enumerate(P) if '이 책을 읽는 분들께' in p and not re.search(r'\d\s*$',p) and i<order[0][1]]
        if pi:
            for i in range(pi[-1]+1, order[0][1]):
                t=E.norm(P[i])
                if t and t not in NOISE and not re.match(r'^\d{1,2}_',t) and len(t)>=25:
                    preface.append(t)
    for idx,(k,si) in enumerate(order):
        end = order[idx+1][1] if idx+1<len(order) else len(P)
        if idx+1==len(order):
            for j in range(si,len(P)):
                tt=P[j].strip()
                if tt.startswith('초판') or tt=='지은이': end=j; break
        title=toc.get(k, re.match(r'^\d{2}_(.+)$',P[si].strip()).group(1))
        chapters.append((k,title,'',blockify(P[si+1:end],title)))

chapters.sort(key=lambda c:c[0])
# 이미지: part1에서 추출
hwp5.extract_images(find("사무엘상1_합본.hwp"), os.path.join(bdir,'images','_extracted'))
shutil.copyfile(os.path.join(ROOT,'books/17. 아모스/images/logo.png'), os.path.join(bdir,'images','logo.png'))
# church-info: 1770x2600 류 찾기
exd=os.path.join(bdir,'images','_extracted')
for f in sorted(os.listdir(exd)):
    try: w,h=Image.open(os.path.join(exd,f)).size
    except: continue
    if h>w and h>=2000 and 0.5<w/h<0.85:
        ext='jpg' if f.lower().endswith(('jpg','jpeg')) else 'png'
        shutil.copyfile(os.path.join(exd,f), os.path.join(bdir,'images','church-info.'+ext)); break

env=f'''TITLE="사무엘상 강해"
BOOK_NAME="사무엘상"
AUTHORS="조춘숙"
AUTHOR_TITLE="목사"
PUBLISHER="물줄기교회 출판부"
LANGUAGE="ko"
OUTPUT_NAME="사무엘상 강해"
TAGS="기독교,설교,사무엘상,강해"
COMMENTS="물줄기교회 조춘숙 목사의 사무엘상 강해 설교집 (제7권)."

EDITION="제1판"
VERSION="1.0.0"
RELEASE_DATE="2015-11"

REVIEWED=""
REVIEW_DATE=""

HWP_SOURCE="original/{os.path.basename(find("사무엘상1_합본.hwp"))}"
BIBLE_REF="사무엘상"
VIDEO="동영상 설교는 https://vimeo.com/watercourse 또는 YouTube에서 “물줄기교회”를 검색해 주세요."
PREFACE_SIGN="2015년 11월|물줄기교회 목사 조춘숙"
COLOPHON="지은이  조춘숙 목사|제작·편집  물줄기교회 출판부|주소  서울 강서구 수명로 68-27 웨스트엔드 2차 문화센터 4층|전화  02-6403-3221|홈페이지  https://vimeo.com/watercourse"

COVER_VERSE="순종이 제사보다|낫고|사무엘상 15장 22절"
COVER_BG="22323a"
COVER_ACCENT="c9a25a"
'''
open(os.path.join(bdir,'book.env'),'w',encoding='utf-8').write(env)
env_d=E.load_env(os.path.join(bdir,'book.env'))
E.write_md(bdir, env_d, preface, chapters)
print("사무엘상: 장", len(chapters), "머리말", len(preface), "장범위", chapters[0][0], "~", chapters[-1][0])
print("장 누락:", [k for k in range(1,34) if k not in [c[0] for c in chapters]])
