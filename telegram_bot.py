import os, json, requests, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"database/queue.json"
HISTORY=ROOT/"database/published.json"
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
API=f"https://api.telegram.org/bot{TOKEN}"

def send(item):
    caption=item.get("caption") or f"📌 {item.get('title','জীবনজ্ঞান')}\n\n{item.get('body','')}\n\n#জীবনজ্ঞান৩৬৫"
    kind=item["type"]
    media=ROOT/item["media"] if item.get("media") else None
    if kind=="video" and media and media.exists():
        with media.open("rb") as f:
            r=requests.post(API+"/sendVideo",data={"chat_id":CHAT,"caption":caption[:1024]},files={"video":f},timeout=180)
    elif kind=="image" and media and media.exists():
        with media.open("rb") as f:
            r=requests.post(API+"/sendPhoto",data={"chat_id":CHAT,"caption":caption[:1024]},files={"photo":f},timeout=120)
    else:
        r=requests.post(API+"/sendMessage",json={"chat_id":CHAT,"text":caption[:4096],"disable_web_page_preview":True},timeout=60)
    r.raise_for_status()
    data=r.json()
    if not data.get("ok"):
        raise RuntimeError(data)
    return data["result"].get("message_id")

def main():
    if not TOKEN or not CHAT:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    q=json.loads(QUEUE.read_text(encoding="utf-8"))
    history=json.loads(HISTORY.read_text(encoding="utf-8"))
    pending=[x for x in q if x.get("status")!="published"]
    batch=pending[:4]
    if not batch:
        print("No pending posts.")
        return
    for item in batch:
        try:
            mid=send(item)
            item["status"]="published"
            item["telegram_message_id"]=mid
            history.append({"id":item["id"],"title":item["title"],"message_id":mid})
            print("Published",item["id"],mid)
        except Exception as e:
            print("Publish failed; will retry next run:",repr(e))
            break
    QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
    HISTORY.write_text(json.dumps(history[-1000:],ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__": main()
