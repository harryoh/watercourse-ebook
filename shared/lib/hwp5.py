# -*- coding: utf-8 -*-
"""Minimal HWP 5.0 (OLE2/CFB) text extractor — stdlib only.
한글(.hwp) 5.0 파일에서 문단 텍스트를 그대로 뽑아낸다. 외부 의존성 없음."""
import struct, zlib

class CFB:
    def __init__(self, data):
        assert data[:8]==b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1', "OLE2(.hwp 5.0) 형식이 아닙니다"
        self.d=data
        self.ssize=1<<struct.unpack_from('<H',data,30)[0]
        self.msize=1<<struct.unpack_from('<H',data,32)[0]
        self.dir_start=struct.unpack_from('<I',data,48)[0]
        self.minicut=struct.unpack_from('<I',data,56)[0]
        self.minifat_start=struct.unpack_from('<I',data,60)[0]
        self.n_minifat=struct.unpack_from('<I',data,64)[0]
        self.difat_start=struct.unpack_from('<I',data,68)[0]
        self.n_difat=struct.unpack_from('<I',data,72)[0]
        difat=list(struct.unpack_from('<109I',data,76))
        sec=self.difat_start
        for _ in range(self.n_difat):
            o=self._off(sec); vals=struct.unpack_from('<%dI'%(self.ssize//4),data,o)
            difat+=list(vals[:-1]); sec=vals[-1]
            if sec>=0xFFFFFFFE: break
        self.fat=[]
        for fs in difat:
            if fs>=0xFFFFFFFE: continue
            self.fat+=list(struct.unpack_from('<%dI'%(self.ssize//4),data,self._off(fs)))
        self.minifat=[]; sec=self.minifat_start
        for _ in range(self.n_minifat):
            self.minifat+=list(struct.unpack_from('<%dI'%(self.ssize//4),data,self._off(sec)))
            sec=self.fat[sec]
            if sec>=0xFFFFFFFE: break
        self.dir=[]; sec=self.dir_start; dd=b''
        while sec<0xFFFFFFFE:
            o=self._off(sec); dd+=data[o:o+self.ssize]; sec=self.fat[sec]
        for i in range(0,len(dd),128):
            e=dd[i:i+128]
            if len(e)<128: break
            nlen=struct.unpack_from('<H',e,64)[0]
            self.dir.append({'name':e[:max(nlen-2,0)].decode('utf-16le','ignore'),
                'type':e[66],'start':struct.unpack_from('<I',e,116)[0],
                'size':struct.unpack_from('<Q',e,120)[0]})
        self.root=next(x for x in self.dir if x['type']==5)
        self.mini=self._chain(self.root['start'],self.root['size'])
    def _off(self,s): return 512+s*self.ssize
    def _chain(self,start,size):
        out=b''; s=start
        while s<0xFFFFFFFE and s<len(self.fat):
            o=self._off(s); out+=self.d[o:o+self.ssize]; s=self.fat[s]
        return out[:size] if size else out
    def _minichain(self,start,size):
        out=b''; s=start
        while s<0xFFFFFFFE and s<len(self.minifat):
            o=s*self.msize; out+=self.mini[o:o+self.msize]; s=self.minifat[s]
        return out[:size]
    def names(self): return [x['name'] for x in self.dir]
    def read(self,name):
        e=next((x for x in self.dir if x['name']==name),None)
        if not e: return None
        return self._minichain(e['start'],e['size']) if e['size']<self.minicut else self._chain(e['start'],e['size'])

INLINE={4,5,6,7,8,9,19,20}
EXT={1,2,3,11,12,14,15,16,17,18,21,22,23}
def _para_text(buf):
    n=len(buf)//2; ws=struct.unpack('<%dH'%n,buf[:n*2]); out=[]; i=0
    while i<n:
        c=ws[i]
        if c in INLINE or c in EXT: i+=8; continue
        if c<32:
            if c==9: out.append('\t')
            elif c in (10,13): out.append('\n')
            elif c in (30,31): out.append(' ')
            i+=1; continue
        out.append(chr(c)); i+=1
    return ''.join(out)
def _section(data,comp):
    if comp: data=zlib.decompress(data,-15)
    paras=[]; i=0; L=len(data)
    while i+4<=L:
        h=struct.unpack_from('<I',data,i)[0]; i+=4
        tag=h&0x3FF; size=(h>>20)&0xFFF
        if size==0xFFF: size=struct.unpack_from('<I',data,i)[0]; i+=4
        body=data[i:i+size]; i+=size
        if tag==67: paras.append(_para_text(body))
    return paras
def extract_paragraphs(path):
    """.hwp -> 문단 문자열 리스트 (원본 공백·문단 구조 보존)."""
    cfb=CFB(open(path,'rb').read())
    comp=bool(struct.unpack_from('<I',cfb.read('FileHeader'),36)[0]&1)
    secs=sorted([n for n in cfb.names() if n.startswith('Section')],key=lambda x:int(x[7:]))
    res=[]
    for s in secs: res+=_section(cfb.read(s),comp)
    return res
def extract_images(path,outdir):
    """.hwp 내부 BinData 이미지(png/jpg 등) 저장. 저장한 파일명 리스트 반환."""
    import os
    cfb=CFB(open(path,'rb').read()); saved=[]
    os.makedirs(outdir,exist_ok=True)
    for n in cfb.names():
        if n.upper().endswith(('.PNG','.JPG','.JPEG','.BMP','.GIF')):
            raw=cfb.read(n); out=raw
            if raw[:1]!=b'\x89' and raw[:2]!=b'\xff\xd8':
                try: out=zlib.decompress(raw,-15)
                except Exception: out=raw
            p=os.path.join(outdir,n); open(p,'wb').write(out); saved.append(n)
    return saved
if __name__=='__main__':
    import sys
    for p in extract_paragraphs(sys.argv[1])[:40]:
        if p.strip(): print(repr(p[:90]))
