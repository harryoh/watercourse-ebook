# -*- coding: utf-8 -*-
"""반복 전처리 파이프라인: 한 권을 만든다.
argv: slug  src_hwp(sandbox)  bible_ref  series_no  bg  accent
HWP에서 제목/주제/발행일 자동 추론 → book.env → 추출 → 이미지 휴리스틱 → 표지 → 검토.
검토(REVIEWED)는 비워두고 사람 검토 대기."""
import sys,os,re,shutil,unicodedata
ROOT='/sessions/vibrant-wizardly-cerf/mnt/harry/watercourse-ebook'
sys.path.insert(0, ROOT+'/shared/lib')
import hwp5, extract_hwp as E
from PIL import Image

slug,src,ref,series,bg,accent = sys.argv[1:7]
bdir=os.path.join(ROOT,'books',slug)
os.makedirs(os.path.join(bdir,'original'),exist_ok=True)
os.makedirs(os.path.join(bdir,'images'),exist_ok=True)
base=os.path.basename(src)
# 원본 복사 (이미 /tmp 등에 받아둔 경로)
shutil.copyfile(src, os.path.join(bdir,'original',base))
P=hwp5.extract_paragraphs(os.path.join(bdir,'original',base))
# 제목/주제 추론 (앞 8문단)
head=[p.strip() for p in P[:8] if p.strip()]
title=next((h for h in head if h.endswith('강해')), f'{ref} 강해')
# 주제: 제목 다음 ~ '조춘숙'(저자) 전까지
theme=''
if title in head:
    ti=head.index(title)
    sub=[h for h in head[ti+1:] if '조춘숙' not in h and 'vimeo' not in h and '동영상' not in h and h!='차 례']
    # 보통 1~2줄
    theme=' '.join(sub[:2]).strip()
# 발행일 (콜로폰)
date=''
m=re.search(r'초판\s*\d*쇄?\s*(\d{4})\s*년\s*(\d{1,2})\s*월', '\n'.join(P[-40:]))
if m: date=f"{m.group(1)}-{int(m.group(2)):02d}"
# cover verse = 주제 (출처 없음)
cv = (theme+'|') if theme else ''
env=f'''TITLE="{title}"
BOOK_NAME="{ref}"
AUTHORS="조춘숙"
AUTHOR_TITLE="목사"
PUBLISHER="물줄기교회 출판부"
LANGUAGE="ko"
OUTPUT_NAME="{title}"
TAGS="기독교,설교,{ref},강해"
COMMENTS="물줄기교회 조춘숙 목사의 {title} 설교집 (제{series}권)."

EDITION="제1판"
VERSION="1.0.0"
RELEASE_DATE="{date}"

REVIEWED=""
REVIEW_DATE=""

HWP_SOURCE="original/{base}"
BIBLE_REF="{ref}"
VIDEO="동영상 설교는 https://vimeo.com/watercourse 또는 YouTube에서 “물줄기교회”를 검색해 주세요."
PREFACE_SIGN="{(date and (date[:4]+'년 '+str(int(date[5:7]))+'월'))}|물줄기교회 목사 조춘숙"
COLOPHON="지은이  조춘숙 목사|제작·편집  물줄기교회 출판부|주소  서울 강서구 수명로 68-27 웨스트엔드 2차 문화센터 4층|전화  02-6403-3221|홈페이지  https://vimeo.com/watercourse"

COVER_VERSE="{cv}"
COVER_BG="{bg}"
COVER_ACCENT="{accent}"
'''
open(os.path.join(bdir,'book.env'),'w',encoding='utf-8').write(env)
# 1차 추출 (이미지 _extracted 생성)
E.main(bdir)
# 이미지 휴리스틱
exd=os.path.join(bdir,'images','_extracted')
logo=church=None; church_area=0
for f in sorted(os.listdir(exd)):
    try: w,h=Image.open(os.path.join(exd,f)).size
    except: continue
    r=w/h if h else 0
    if 2.0<=r<=8.0 and 120<=h<=400 and not logo: logo=f
    if h>w and h>=1500 and 0.5<r<0.85 and w*h>church_area: church=f; church_area=w*h
if logo: shutil.copyfile(os.path.join(exd,logo), os.path.join(bdir,'images','logo.png' if logo.lower().endswith('png') else 'logo.'+logo.rsplit('.',1)[-1].lower()))
if church:
    ext=church.rsplit('.',1)[-1].lower(); ext='jpg' if ext in('jpg','jpeg') else 'png'
    shutil.copyfile(os.path.join(exd,church), os.path.join(bdir,'images','church-info.'+ext))
print(f"[{slug}] TITLE={title!r} THEME={theme!r} DATE={date!r} logo={logo} church={church}")
