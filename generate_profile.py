#!/usr/bin/env python3
"""Generate GitHub-safe theme-aware PNG cards using the actual supplied photo.

No AI reconstruction: uses exact original pixels for the face and overlays only 0/1
characters to maintain the code/Neofetch aesthetic. Python + Pillow only.
"""
from __future__ import annotations
import argparse
import datetime as dt
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance, ImageFilter

ROOT=Path(__file__).resolve().parent
PHOTO=ROOT/'assets'/'headshot.png'
USER='nebiyumekonnen17'
CW,CH=1135,640
S=2  # retina previews for GitHub
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
FONT_B='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
if not Path(FONT).exists():
    FONT='DejaVuSansMono.ttf'
    FONT_B='DejaVuSansMono.ttf'

def api_json(url):
    headers={'User-Agent':'BinaryProfile/2.0','Accept':'application/vnd.github+json'}
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token: headers['Authorization']='Bearer '+token
    with urlopen(Request(url, headers=headers),timeout=15) as res:
        return json.load(res)

def stats(offline):
    # Placeholders are explicitly non-real; public repository count fetched on live refresh
    vals={'repos':'—','stars':'—','followers':'—','updated':'PREVIEW'}
    if offline: return vals
    try:
        user=api_json(f'https://api.github.com/users/{USER}')
        vals['repos']=str(user.get('public_repos','—'))
        vals['followers']=str(user.get('followers','—'))
        total=0
        for n in range(1,11):
            repos=api_json(f'https://api.github.com/users/{USER}/repos?per_page=100&page={n}&type=owner')
            total+=sum(int(r.get('stargazers_count',0)) for r in repos if not r.get('fork',False))
            if len(repos)<100: break
        vals['stars']=str(total)
        vals['updated']=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
    except Exception as ex:
        print('Could not fetch live stats:',ex)
    return vals

def hex_rgb(s): return tuple(bytes.fromhex(s.lstrip('#')))
def font(px,bold=False): return ImageFont.truetype(FONT_B if bold else FONT,round(px*S))
def color(rgb,alpha=255): return (*rgb,alpha)

def binary_photo(theme):
    W,H=400*S,452*S
    photo=Image.open(PHOTO).convert('RGB')
    w,h=photo.size
    # Source image is the exact user's uploaded, non-AI headshot. Crop ONLY.
    photo=photo.crop((round(w*.19),round(h*.024),round(w*.84),round(h*.67)))
    photo=ImageOps.fit(photo,(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.31))
    photo=ImageEnhance.Color(photo).enhance(.88)
    # Vignette beyond facial area, without changing the person's geometry
    tint=(6,16,22) if theme=='dark' else (31,41,42)
    px=photo.load()
    for j in range(H):
        yy=j/H
        for i in range(W):
            xx=i/W
            vignette=((xx-.5)*2)**2
            keep=.98-.19*vignette-.09*max((yy-.84)/.16,0)
            r,g,b=px[i,j]
            px[i,j]=(int(r*keep+tint[0]*(1-keep)),int(g*keep+tint[1]*(1-keep)),int(b*keep+tint[2]*(1-keep)))
    panel=photo.convert('RGBA')
    glyph=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(glyph)
    digits=ImageFont.truetype(FONT,9*S)
    for iy,y in enumerate(range(0,H,12*S)):
        for ix,x in enumerate(range(0,W,9*S)):
            xr=x/W; yr=y/H
            # Fade coding over eyes/nose/mouth. Keep photo recognizable.
            face=((xr-.52)/.39)**2+((yr-.36)/.29)**2
            face_protection=max(0,1-face)
            edge=abs(xr-.5)*2
            opacity=int((21+100*edge+35*int(yr>.69))*(1-0.98*face_protection))
            opacity=max(2,min(150,opacity))
            digit='0' if (ix*7+iy*11)%9 < 5 else '1'
            green=(72,238,184) if theme=='dark' else (36,244,184)
            d.text((x,y),digit,font=digits,fill=(*green,opacity))
    panel=Image.alpha_composite(panel,glyph)
    return panel

def make_card(theme,values):
    dark=theme=='dark'
    bg=hex_rgb('#0b1017' if dark else '#eef2f4')
    surface=hex_rgb('#151b23' if dark else '#ffffff')
    border=hex_rgb('#2f3c46' if dark else '#d3dde2')
    txt=hex_rgb('#e6edf3' if dark else '#1e2933')
    muted=hex_rgb('#8b99a6' if dark else '#5d6978')
    key=hex_rgb('#f3aa61' if dark else '#926019')
    val=hex_rgb('#a8d4ff' if dark else '#215c9b')
    accent=hex_rgb('#6fe6b6' if dark else '#126e53')
    out=Image.new('RGB',(CW*S,CH*S),bg)
    d=ImageDraw.Draw(out)
    def rect(bounds,fill,radius=0,outline=None,width=1):
        b=tuple(round(x*S) for x in bounds)
        if radius: d.rounded_rectangle(b,round(radius*S),fill,outline,round(width*S))
        else: d.rectangle(b,fill,outline,round(width*S))
    def text(x,y,string,sz=15,fill=txt,bold=False):
        d.text((round(x*S),round(y*S)),str(string),font=font(sz,bold),fill=fill,anchor='la')
    def line(x1,y1,x2,y2,col=border,width=1): d.line((round(x1*S),round(y1*S),round(x2*S),round(y2*S)),fill=col,width=max(1,round(width*S)))
    rect((9,9,1126,631),surface,18,border)
    for x,col in [(35,'#ff5f57'),(56,'#febc2e'),(77,'#28c840')]:d.ellipse(((x-5.5)*S,(35-5.5)*S,(x+5.5)*S,(35+5.5)*S),fill=hex_rgb(col))
    text(100,26,'nebiyu@github  ~/identity/portrait.bin',12,muted)
    line(25,57,1110,57)
    rect((27,72,437,592),bg,9,border)
    text(43,84,'$ render --source=headshot --encoding=01',11,accent)
    face=binary_photo(theme)
    out.paste(face,((34)*S,(109)*S))
    d=ImageDraw.Draw(out)
    d.rounded_rectangle((34*S,109*S,434*S,561*S),radius=5*S,outline=border,width=1*S)
    text(42,572,'01001000 01100101 01101100 01101100 01101111',11,muted)
    # right panel
    text(469,82,'nebiyu',15,accent,bold=True)
    text(533,82,'@github',15,val)
    line(469,105,1095,105)
    def entry(y,label,value):
        text(469,y,label,14,key)
        text(692,y,value,14,val)
    entry(119,'Name:', 'Nebiyu Mekonnen')
    entry(144,'Role:', 'Software Developer & Cloud Builder')
    entry(169,'OS:', 'Windows / Linux / AWS')
    entry(194,'Education:', 'Year Up United / Per Scholas')
    entry(219,'Languages:', 'Java / Python / JS / TypeScript')
    entry(244,'Frontend:', 'React / HTML / CSS / PWA')
    entry(269,'Backend:', 'Node.js / Express / MySQL')
    entry(294,'Cloud:', 'AWS / Vercel / GitHub Actions')
    text(469,330,'~/featured-projects',14,accent,bold=True);line(671,338,1095,338)
    entry(353,'Visual Tizita:', 'AWS event memories platform')
    entry(378,'Lisan:', 'Amharic speech-to-text PWA')
    entry(403,'NAEP:', 'AI engineering foundation')
    entry(428,'Nehas Digital Signage:', 'AWS screen fleet platform')
    text(469,466,'~/connect',14,accent,bold=True);line(568,475,1095,475)
    entry(489,'Website:', 'nebiyumekonnen.com')
    entry(514,'Links:', 'links.nebiyumekonnen.com')
    text(469,548,'~/github-stats',14,accent,bold=True);line(614,555,1095,555)
    for x,label,value in [(469,'REPOS',values['repos']),(624,'STARS',values['stars']),(768,'FOLLOWERS',values['followers'])]:
        text(x,575,label,11,muted);text(x,595,value,21,val,bold=True)
    text(991,604,'SYNC '+values['updated'],9,muted)
    dest=ROOT/f'{theme}_mode.png'
    out.save(dest,optimize=True)
    # Preview for chat at normal CSS display resolution
    preview=out.resize((CW,CH),Image.Resampling.LANCZOS)
    preview.save(ROOT/f'{theme}_preview.png',optimize=True)
    return dest

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--offline',action='store_true')
    args=p.parse_args()
    values=stats(args.offline)
    for mode in ('dark','light'):
        path=make_card(mode,values)
        print(path,path.stat().st_size)

if __name__=='__main__': main()
