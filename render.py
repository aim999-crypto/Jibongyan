import os, json, textwrap, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
W,H=720,1280
BG=(13,38,33); GOLD=(222,184,95); WHITE=(250,250,245); MUTED=(190,210,200)

def font(size):
    candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf"]
    for p in candidates:
        if Path(p).exists():
            try: return ImageFont.truetype(p,size)
            except: pass
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    lines=[]
    for paragraph in str(text).splitlines():
        words=paragraph.split()
        line=""
        for word in words:
            test=(line+" "+word).strip()
            if draw.textbbox((0,0),test,font=fnt)[2] <= max_width:
                line=test
            else:
                if line: lines.append(line)
                line=word
        if line: lines.append(line)
    return lines

def make_card(item, path, frame=0, total=1):
    img=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(img)
    # Decorative geometry
    d.ellipse((W-220,-160,W+120,180),outline=(36,86,70),width=12)
    d.ellipse((-140,H-260,180,H+60),outline=(36,86,70),width=12)
    d.rounded_rectangle((42,52,W-42,H-52),radius=34,outline=(82,112,88),width=3)
    d.text((78,100),"জীবনজ্ঞান ৩৬৫",font=font(36),fill=GOLD)
    d.text((78,164),"ছোট ভিডিও, বড় সমাধান।",font=font(22),fill=MUTED)
    d.line((78,220,W-78,220),fill=GOLD,width=3)
    title=item.get("title","আজকের জীবনজ্ঞান")
    y=285
    for line in wrap(d,title,font(48),W-156)[:4]:
        d.text((78,y),line,font=font(48),fill=WHITE); y+=72
    y+=40
    body=item.get("body","")
    for line in wrap(d,body,font(31),W-156)[:14]:
        d.text((78,y),line,font=font(31),fill=(235,240,232)); y+=51
    d.text((78,H-125),f"বিষয়: {item.get('category','দৈনন্দিন জীবন')}",font=font(22),fill=GOLD)
    d.text((78,H-85),"তথ্য যাচাই করে ব্যবহার করুন",font=font(18),fill=MUTED)
    img.save(path)
    return path

def render(item, index):
    kind=item["type"]
    if kind=="text":
        return None
    if kind=="video":
        # 5-second motion-graphics clip; can be extended via settings.
        png=OUT/f"frame_{index}.png"
        mp4=OUT/f"{index}.mp4"
        make_card(item,png)
        cmd=["ffmpeg","-y","-loop","1","-i",str(png),"-vf",
             "zoompan=z='min(zoom+0.0008,1.04)':d=875:s=720x1280:fps=25,format=yuv420p",
             "-t","35","-an","-c:v","libx264","-preset","ultrafast",str(mp4)]
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        png.unlink(missing_ok=True)
        return mp4
    png=OUT/f"{index}.png"
    make_card(item,png)
    return png

def main():
    queue=json.loads((ROOT/"database/queue.json").read_text(encoding="utf-8"))
    for i,item in enumerate(queue):
        if item.get("status")!="published":
            item["media"]=str(render(item,i).relative_to(ROOT)) if item["type"]!="text" else ""
    (ROOT/"database/queue.json").write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__": main()
