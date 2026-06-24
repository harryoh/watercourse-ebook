# -*- coding: utf-8 -*-
import sys,os,re,shutil,unicodedata,glob,html
ROOT='/sessions/vibrant-wizardly-cerf/mnt/harry/watercourse-ebook'
sys.path.insert(0,ROOT+'/shared/lib')
import hwp5, extract_hwp as E
def nfc(s): return unicodedata.normalize('NFC',s)
def esc(s): return html.escape(s,quote=False)
d=glob.glob('/sessions/vibrant-wizardly-cerf/mnt/water--*')[0]
src=[os.path.join(r,f) for r,_,fs in os.walk(d) for f in fs if '자야' in nfc(f) and f.endswith('.hwp') and '2019' in r][0]
P=hwp5.extract_paragraphs(src)
bdir=os.path.join(ROOT,'books','08. 내가 사랑하는 자야(기도문)')
# 본문 이미지 앵커(문단번호) → 사진 파일 (차례 자음아이콘 제외, 본문 6곳)
anchors={481:'photo1.jpg',642:'photo2.jpg',758:'photo3.jpg',1049:'photo4.jpg',1537:'photo5.jpg'}  # 1950=교회안내(뒤)
# TOC 항목
toc=[]
for p in P:
    m=re.match(r'^(.+?)\s*●\s*\d+\s*$',p.strip())
    if m:
        t=m.group(1).strip()
        if t and t!='이 책을 읽는 분들께' and t not in toc: toc.append(t)
titleset=set(toc); CONS=set('ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ')
NOISE={'물줄기교회 조춘숙 목사','조춘숙 목사','물줄기교회','내가 사랑하는 자야','물줄기교회를 검색해 주세요!'}
def body_title_idx(t,start):
    for i in range(start,len(P)):
        if P[i].strip()==t: return i
    return -1
first_entry_idx=min([body_title_idx(t,0) for t in toc if body_title_idx(t,0)>0])
pref_idx=[i for i,p in enumerate(P) if '이 책을 읽는 분들께' in p.strip() and '●' not in p]
preface=[]
if pref_idx:
    for i in range(pref_idx[-1]+1, first_entry_idx):
        t=E.norm(P[i])
        if t and t not in NOISE and t not in CONS and not re.fullmatch(r'\d{1,3}',t) and '●' not in t and len(t)>=10:
            preface.append(t)
entry_pos=sorted([(body_title_idx(t,first_entry_idx),t) for t in toc if body_title_idx(t,first_entry_idx)>0])
end_all=len(P)
for i in range(first_entry_idx,len(P)):
    if P[i].strip().startswith('초판'): end_all=i; break
def stanzas(lines):
    out=[];cur=[]
    for ln in lines:
        s=ln.rstrip()
        if not s.strip():
            if cur: out.append(cur);cur=[]
        else:
            t=E.norm(s)
            if not t or t in NOISE or t in CONS or re.fullmatch(r'\d{1,3}',t) or t in titleset: continue
            cur.append(t)
    if cur: out.append(cur)
    return out
L=[];ap=L.append
ap('<div class="title-page">')
ap('<p class="logo"><img src="images/logo.png" alt="물줄기교회"/></p>')
ap('<p class="bk">내가 사랑하는 자야</p>')
ap('<p class="au">조춘숙 목사</p>')
ap('<p class="pub">물줄기교회 출판부</p>')
ap('<p class="vid">동영상 설교는 https://vimeo.com/watercourse 또는 YouTube에서 “물줄기교회”를 검색해 주세요.</p>')
ap('</div>');ap('')
ap('# 이 책을 읽는 분들께');ap('')
for p in preface: ap(esc(p));ap('')
for n,(i,t) in enumerate(entry_pos):
    end=entry_pos[n+1][0] if n+1<len(entry_pos) else end_all
    ap(f'# {esc(t)}');ap('')
    for st in stanzas(P[i+1:end]):
        ap('<p class="poem">'+'<br/>'.join(esc(x) for x in st)+'</p>')
    ap('')
    # 이 항목 범위에 앵커가 있으면 사진 삽입
    for a,img in sorted(anchors.items()):
        if i<=a<end:
            ap(f'<p class="photo"><img src="images/{img}" alt=""/></p>');ap('')
ap('# 판권');ap('')
ap('<div class="colophon"><p class="bk">내가 사랑하는 자야</p>')
ap('<p class="pubinfo">제2판 발행  2019년 3월</p>')
for line in ['지은이  조춘숙 목사','제작·편집  물줄기교회 출판부','주소  서울 강서구 수명로 68-27 웨스트엔드 2차 문화센터 4층','전화  02-6403-3221','홈페이지  https://vimeo.com/watercourse']:
    ap(f'<p>{line}</p>')
ap('<p class="ver">전자책 버전 1.0.0</p></div>');ap('')
ap('# 교회 안내');ap('')
ap('<p class="church-info"><img src="images/church-info.jpg" alt="예배안내 및 오시는 길"/></p>');ap('')
open(os.path.join(bdir,'manuscript.md'),'w',encoding='utf-8').write('\n'.join(L))
print("재생성: 사진 삽입", sum(1 for a in anchors if any(i<=a<(entry_pos[n+1][0] if n+1<len(entry_pos) else end_all) for n,(i,_) in enumerate(entry_pos))),"/5, 교회안내 뒤")
