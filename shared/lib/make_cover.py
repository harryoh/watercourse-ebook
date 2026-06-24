# -*- coding: utf-8 -*-
"""book.env 설정으로 표지 이미지(cover.jpg) 생성. 의존성: Pillow.
사용법: python3 make_cover.py <book_dir>
COVER_VERSE="구절1|구절2|출처"  형식. 색상은 COVER_BG / COVER_ACCENT (옵션)."""
import os,sys
from PIL import Image, ImageDraw, ImageFont
def load_env(p):
    e={}
    for ln in open(p,encoding='utf-8'):
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); v=v.strip()
        if len(v)>=2 and v[0]==v[-1] and v[0] in '"\'' : v=v[1:-1]
        e[k.strip()]=v
    return e
def hexc(s,d): 
    s=(s or '').lstrip('#')
    try: return tuple(int(s[i:i+2],16) for i in (0,2,4))
    except: return d
def main(bd):
    env=load_env(os.path.join(bd,'book.env'))
    W,H=1600,2400
    bg=hexc(env.get('COVER_BG'),(28,49,68)); accent=hexc(env.get('COVER_ACCENT'),(201,162,90))
    SER="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
    SERB="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
    for c in (SER,SERB):
        if not os.path.exists(c): SER=SERB=None; break
    img=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(img)
    def F(p,s): return ImageFont.truetype(p,s) if p else ImageFont.load_default()
    def center(t,y,f,fill):
        bb=d.textbbox((0,0),t,font=f); d.text(((W-(bb[2]-bb[0]))/2-bb[0],y),t,font=f,fill=fill)
    d.rectangle([W/2-1,160,W/2+1,360],fill=accent)
    center(env.get('BOOK_NAME',''),560,F(SERB,300),(245,245,240))
    center(env.get('TITLE',''),940,F(SER,96),accent)
    d.rectangle([W/2-140,1120,W/2+140,1123],fill=(120,140,160))
    verse=(env.get('COVER_VERSE') or '').split('|')
    y=1260
    for line in verse[:-1]:
        center(line,y,F(SER,64),(210,218,228)); y+=100
    if len(verse)>=2 and verse[-1]:
        center(f'— {verse[-1]} —',y+20,F(SER,44),(150,168,188))
    center(f"{env.get('AUTHORS','')} {env.get('AUTHOR_TITLE','목사')}",1980,F(SER,76),(235,235,230))
    center(env.get('PUBLISHER',''),2150,F(SER,52),(160,178,196))
    d.rectangle([60,60,W-60,H-60],outline=accent,width=4)
    out=os.path.join(bd,'cover.jpg'); img.save(out,'JPEG',quality=88)
    print("cover.jpg 생성:",out)
if __name__=='__main__': main(sys.argv[1])
