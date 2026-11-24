from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import sys
SRC,OUT,TB=sys.argv[1],sys.argv[2],eval(sys.argv[3])
s = Image.open(SRC).convert('RGB')
W,H=1920,1080; sc=W/1080
city=s.crop((0,1380,1080,1920)); city=city.resize((W,int(city.height*sc)),Image.LANCZOS)
sky=s.crop((0,0,1080,170)).resize((W,int(170*sc)),Image.LANCZOS)
bg=Image.new('RGB',(W,H)); bg.paste(sky,(0,0)); bg.paste(city,(0,H-city.height))
seam=H-city.height; dark=np.array([20,26,40],float)
b=np.asarray(bg).astype(float)
for y in range(H):
    a=0.86 if y<640 else max(0.30,0.86-(y-640)/440*0.56); b[y]=b[y]*(1-a)+dark*a
bg=Image.fromarray(b.clip(0,255).astype('uint8'))
band=bg.crop((0,seam-60,W,seam+60)).filter(ImageFilter.GaussianBlur(25)); bg.paste(band,(0,seam-60))
b=np.asarray(bg).astype(float); xs=np.arange(W); la=np.clip(0.55*(1-xs/900),0,0.55)[None,:,None]
bg=Image.fromarray((b*(1-la)+dark*la).clip(0,255).astype('uint8')).convert('RGBA')
def lumalpha(box,fg,lo,hi,k):
    im=s.crop(box); L=np.asarray(im.convert('L')).astype(float); a=((L-lo)/(hi-lo)).clip(0,1)
    o=np.zeros((im.height,im.width,4),'uint8'); o[...,:3]=fg; o[...,3]=(a*255).astype('uint8')
    o=Image.fromarray(o,'RGBA'); return o.resize((int(o.width*k),int(o.height*k)),Image.LANCZOS)
def rounded(box,r,k):
    im=s.crop(box).resize((int((box[2]-box[0])*k),int((box[3]-box[1])*k)),Image.LANCZOS).convert('RGBA')
    m=Image.new('L',im.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,im.width-1,im.height-1),int(r*k),fill=255); im.putalpha(m); return im
k=1.2
photo=rounded((277,628,807,1040),30,k)   # crop above pill
pad=40; cw=photo.width+pad*2
name=lumalpha((262,1104,822,1172),(222,205,186),105,205,1.12)
pill=rounded((300,1042,781,1096),14,1.12); pw,ph=pill.size
ch=pad+photo.height+30+name.height+44
cx=W-cw-130; cy=(H-ch)//2-20
cm=Image.new('L',(cw,ch),0); ImageDraw.Draw(cm).rounded_rectangle((0,0,cw-1,ch-1),40,fill=255)
glass=bg.crop((cx,cy,cx+cw,cy+ch)).filter(ImageFilter.GaussianBlur(28))
gn=np.asarray(glass.convert('RGB')).astype(float)*0.55+np.array([60,58,60])*0.45
glass=Image.fromarray(gn.clip(0,255).astype('uint8')).convert('RGBA'); glass.putalpha(cm); bg.alpha_composite(glass,(cx,cy))
f2=Image.new('RGBA',(cw,ch),(205,195,185,0)); f2.putalpha(cm.point(lambda v:int(v*0.12))); bg.alpha_composite(f2,(cx,cy))
bg.alpha_composite(photo,(cx+pad,cy+pad))
py=cy+pad+photo.height-ph//2-6
bg.alpha_composite(pill,(cx+(cw-pw)//2,py))
bg.alpha_composite(name,(cx+(cw-name.width)//2,py+ph+14))
lc=(90+cx)//2
logo=lumalpha((405,180,685,350),(250,247,240),60,200,1.5)
rh=lumalpha(TB,(236,224,206),70,190,1.05*(640/(TB[2]-TB[0])) if TB[2]-TB[0]<500 else 1.05)
addr=lumalpha((188,1226,894,1274),(240,240,240),95,200,0.95)
total=logo.height+60+rh.height+70+addr.height; y=(H-total)//2-20
for im,gap in [(logo,60),(rh,70),(addr,0)]:
    bg.alpha_composite(im,(lc-im.width//2,y)); y+=im.height+gap
o=bg.convert('RGB'); o.save(OUT+'.png'); o.save(OUT+'.jpg',quality=92)
