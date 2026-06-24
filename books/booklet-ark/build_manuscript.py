# -*- coding: utf-8 -*-
import sys,os,re,shutil,unicodedata,glob
ROOT='/sessions/vibrant-wizardly-cerf/mnt/harry/watercourse-ebook'
sys.path.insert(0,ROOT+'/shared/lib')
import hwp5, extract_hwp as E
def nfc(s): return unicodedata.normalize('NFC',s)
d=glob.glob('/sessions/vibrant-wizardly-cerf/mnt/water--*')[0]
src=None
for r,_,fs in os.walk(d):
    for f in fs:
        if '방주' in nfc(f) and f.lower().endswith('.hwp'): src=os.path.join(r,f)
P=hwp5.extract_paragraphs(src)
bdir=os.path.join(ROOT,'books','booklet-ark')
os.makedirs(os.path.join(bdir,'original'),exist_ok=True); os.makedirs(os.path.join(bdir,'images'),exist_ok=True)
shutil.copyfile(src, os.path.join(bdir,'original',os.path.basename(src)))
NOISE_RE=re.compile(r'^생명을 살리는 방주')
def blockify(body,title):
    out=[];expect=True;first=True
    for p in body:
        t=E.norm(p)
        if not t: continue
        if re.fullmatch(r'\d{1,3}',t): continue
        if NOISE_RE.match(t): continue
        if t in ('물줄기교회 조춘숙 목사','조춘숙 목사','물줄기교회'): continue
        if E.REF_RE.match(t): out.append(('ref',t)); expect=True; continue
        if expect: out.append(('quote_lead' if first else 'quote',t)); expect=False; first=False; continue
        out.append(('p',t))
    return out
# 섹션 헤더 위치
hdr=[i for i,p in enumerate(P) if re.fullmatch(r'생명을 살리는 방주[ⅠⅡ]',p.strip())]
# 첫 occurrence of Ⅰ and Ⅱ
import unicodedata as U
def roman(p): 
    m=re.search(r'([ⅠⅡ])',p); return m.group(1) if m else ''
secs=[]
seen=set()
for i in hdr:
    rmn=roman(P[i].strip())
    if rmn not in seen: secs.append((i,rmn)); seen.add(rmn)
# colophon end
end_all=len(P)
for i in range(len(P)):
    if P[i].strip().startswith('초판'): end_all=i; break
chapters=[]
for n,(si,rmn) in enumerate(secs):
    s_end = secs[n+1][0] if n+1<len(secs) else end_all
    seg=P[si:s_end]
    op=next((j for j,p in enumerate(seg) if re.match(r'^출애굽기\s*\d+장',p.strip())),1)
    passage=E.norm(seg[op]) if op<len(seg) else ''
    chapters.append((n+1, f'생명을 살리는 방주 ({rmn})', passage, blockify(seg[op+1:], '')))
# images
hwp5.extract_images(src, os.path.join(bdir,'images','_extracted'))
shutil.copyfile(os.path.join(ROOT,'books/17-amos/images/logo.png'), os.path.join(bdir,'images','logo.png'))
env=f'''TITLE="생명을 살리는 방주"
BOOK_NAME="방주"
AUTHORS="조춘숙"
AUTHOR_TITLE="목사"
PUBLISHER="물줄기교회 출판부"
LANGUAGE="ko"
OUTPUT_NAME="생명을 살리는 방주"
TAGS="기독교,설교,출애굽기,소책자"
COMMENTS="물줄기교회 조춘숙 목사의 소책자 '생명을 살리는 방주' (출애굽기 2장)."
EDITION="제1판"
VERSION="1.0.0"
RELEASE_DATE="2017-11"
REVIEWED=""
REVIEW_DATE=""
HWP_SOURCE="original/{os.path.basename(src)}"
BIBLE_REF="출애굽기"
VIDEO="동영상 설교는 https://vimeo.com/watercourse 또는 YouTube에서 “물줄기교회”를 검색해 주세요."
PREFACE_SIGN=""
COLOPHON="지은이  조춘숙 목사|제작·편집  물줄기교회 출판부|주소  서울 강서구 수명로 68-27 웨스트엔드 2차 문화센터 4층|전화  02-6403-3221|홈페이지  https://vimeo.com/watercourse"
COVER_VERSE="그 아기를 위하여|울거늘|출애굽기 2장 6절"
COVER_BG="2f4a3a"
COVER_ACCENT="c9a25a"
'''
open(os.path.join(bdir,'book.env'),'w',encoding='utf-8').write(env)
E.write_md(bdir, E.load_env(os.path.join(bdir,'book.env')), [], chapters)
print("방주: 섹션", [r for _,r in secs], "장수", len(chapters))
for k,t,ps,bl in chapters: print(" ",k,t,"| passage",ps,"| blocks",len(bl))
