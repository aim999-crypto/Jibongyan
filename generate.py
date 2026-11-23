import os, json, random, re, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT/"config/settings.json").read_text(encoding="utf-8"))
CATEGORIES = json.loads((ROOT/"config/categories.json").read_text(encoding="utf-8"))
QUEUE = ROOT/"database/queue.json"

def ask_gemini():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    model = SETTINGS.get("gemini_model", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    mix = SETTINGS["post_mix"]
    prompt = f"""
তুমি বাংলাদেশের সকল বয়সের জন্য 'জীবনজ্ঞান ৩৬৫' চ্যানেলের বাংলা সম্পাদক।
২৪টি একেবারে আলাদা, বাস্তবসম্মত, সংক্ষিপ্ত ও উপকারী পোস্ট তৈরি করো।
ক্যাটাগরি: {', '.join(CATEGORIES)}
বণ্টন: {mix}
শুধু JSON array ফেরত দাও। প্রতিটি object-এ type, category, title, body, caption, visual_hint থাকবে।
type হবে video/image/text/tip/quiz/challenge।
video-র body হবে ৩০-৪৫ সেকেন্ডের voiceover script; image-এর body হবে ৩-৫টি ছোট bullet; text-এ সহজ নির্দেশনা।
tip সংক্ষিপ্ত; quiz-এ প্রশ্ন ও ৪টি option এবং সঠিক উত্তর/ব্যাখ্যা; challenge-এ আজকের ছোট কাজ।
সব লেখা প্রাঞ্জল বাংলা। ভুয়া পরিসংখ্যান, অযাচিত চিকিৎসা/আইনি/আর্থিক নিশ্চয়তা, বিপজ্জনক পরামর্শ নয়।
স্বাস্থ্য/আইন/অর্থ সংক্রান্ত হলে সাধারণ সচেতনতা হিসেবে লিখবে এবং প্রয়োজনে বিশেষজ্ঞ/সরকারি উৎস দেখার কথা বলবে।
"""
    payload = {"contents":[{"parts":[{"text":prompt}]}],
               "generationConfig":{"temperature":0.8, "responseMimeType":"application/json"}}
    try:
        r = requests.post(url, json=payload, timeout=90)
        r.raise_for_status()
        txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(txt)
        if isinstance(data, list) and len(data) >= 24:
            valid = [x for x in data if x.get("type") in mix and x.get("title") and x.get("body")]
            if len(valid) >= 24:
                return valid[:24]
    except Exception as e:
        print("Gemini generation failed; using fallback:", repr(e))
    return None

def fallback():
    samples = [
      ("ডিজিটাল নিরাপত্তা","অপরিচিত কাউকে OTP দেবেন না","কোনো ব্যক্তি পরিচয় যাই দিক, ফোনে বা মেসেজে পাওয়া OTP, PIN বা পাসওয়ার্ড কাউকে বলবেন না। সন্দেহ হলে কল কেটে অফিসিয়াল অ্যাপ বা নম্বরে যোগাযোগ করুন।"),
      ("টাকা-পয়সার সচেতনতা","ছোট সঞ্চয়ের অভ্যাস","প্রতিদিনের খরচ লিখে রাখুন। প্রয়োজন আর ইচ্ছার খরচ আলাদা করুন। সামর্থ্য অনুযায়ী অল্প হলেও নিয়মিত সঞ্চয় করুন।"),
      ("স্বাস্থ্য ও পরিচ্ছন্নতা","হাত ধোয়ার সঠিক অভ্যাস","খাবারের আগে, টয়লেটের পরে এবং বাইরে থেকে ফিরে সাবান-পানি দিয়ে ভালোভাবে হাত ধুয়ে নিন।"),
      ("নিরাপদ চলাফেরা","রাস্তা পার হওয়ার আগে থামুন","ফুটপাত ব্যবহার করুন। জেব্রা ক্রসিং বা নিরাপদ পারাপারের স্থান বেছে নিন। দুই দিক দেখে তারপর রাস্তা পার হন।"),
      ("ঘরোয়া সমস্যা সমাধান","বিদ্যুতের নিরাপত্তা","ভেজা হাতে সুইচ বা বৈদ্যুতিক যন্ত্র ধরবেন না। তার ছেঁড়া বা স্পার্ক দেখা গেলে নিজে মেরামত না করে বিদ্যুৎ সংযোগ বন্ধ করে দক্ষ ইলেকট্রিশিয়ানের সাহায্য নিন।"),
      ("স্মার্ট কেনাকাটা","কেনার আগে দাম ও রসিদ","পণ্য কেনার আগে দাম, মেয়াদ, সিল ও ফেরত নীতি যাচাই করুন। রসিদ সংরক্ষণ করুন।"),
      ("পড়াশোনা ও দক্ষতা","২৫ মিনিট মনোযোগ","একটি ছোট লক্ষ্য ঠিক করে ২৫ মিনিট মনোযোগ দিয়ে কাজ করুন, তারপর ছোট বিরতি নিন। নিজের সুবিধামতো সময় বদলাতে পারেন।"),
      ("নাগরিক সেবা","কাগজপত্রের কপি নিরাপদে রাখুন","গুরুত্বপূর্ণ কাগজের পরিষ্কার স্ক্যান নিজের নিরাপদ জায়গায় রাখুন। অচেনা কাউকে NID বা ব্যক্তিগত তথ্য পাঠাবেন না।"),
      ("AI ও প্রযুক্তি","AI-এর উত্তর যাচাই করুন","AI দ্রুত সাহায্য করতে পারে, কিন্তু ভুলও করতে পারে। গুরুত্বপূর্ণ তথ্য সরকারি বা নির্ভরযোগ্য উৎসে মিলিয়ে নিন।"),
      ("দৈনন্দিন জীবনদক্ষতা","আগামী দিনের প্রস্তুতি","রাতে পরের দিনের তিনটি জরুরি কাজ লিখে রাখুন। প্রয়োজনীয় জিনিস এক জায়গায় রাখলে সকাল সহজ হয়।")
    ]
    types = ["video"]*8 + ["image"]*6 + ["text"]*5 + ["tip"]*3 + ["quiz"] + ["challenge"]
    random.shuffle(types)
    out=[]
    for i,t in enumerate(types):
        cat,title,body = samples[i % len(samples)]
        if t == "quiz":
            title="নিরাপদ ডিজিটাল অভ্যাস: ছোট কুইজ"
            body="প্রশ্ন: OTP কার সঙ্গে শেয়ার করা উচিত?\nA) বন্ধুর সঙ্গে\nB) ফোনকারীর সঙ্গে\nC) কারও সঙ্গে নয়\nD) দোকানদারের সঙ্গে\nউত্তর: C — OTP গোপনীয়।"
        elif t == "challenge":
            title="আজকের চ্যালেঞ্জ"
            body="আজ নিজের ফোনে 2-step verification চালু আছে কি না যাচাই করুন। চালু না থাকলে অফিসিয়াল নির্দেশনা দেখে সেট করুন।"
        elif t == "tip":
            title="দ্রুত টিপস: "+title
        out.append({"type":t,"category":cat,"title":title,"body":body,
                    "caption":f"📌 {title}\n\n{body}\n\n#জীবনজ্ঞান৩৬৫ #বাংলাটিপস",
                    "visual_hint":title})
    return out

def main():
    data = ask_gemini() or fallback()
    # Enforce exact requested mix by sorting/repairing types if AI returns a malformed mix.
    target = SETTINGS["post_mix"]
    buckets = {k:[] for k in target}
    for item in data:
        if item.get("type") in buckets:
            buckets[item["type"]].append(item)
    result=[]
    for kind, count in target.items():
        while len(buckets[kind]) < count:
            buckets[kind].append(fallback_item(kind, len(buckets[kind])))
        result.extend(buckets[kind][:count])
    random.shuffle(result)
    for i,item in enumerate(result):
        item["id"] = f"{__import__('datetime').date.today().isoformat()}-{i+1:02d}"
        item["status"] = "pending"
    QUEUE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {len(result)} posts.")

def fallback_item(kind, idx):
    return {"type":kind,"category":CATEGORIES[idx % len(CATEGORIES)],
            "title":"আজকের প্রয়োজনীয় জীবনজ্ঞান",
            "body":"গুরুত্বপূর্ণ তথ্য যাচাই করুন, ব্যক্তিগত তথ্য সুরক্ষিত রাখুন এবং প্রয়োজন হলে নির্ভরযোগ্য বিশেষজ্ঞের পরামর্শ নিন।",
            "caption":"📌 আজকের প্রয়োজনীয় জীবনজ্ঞান\n\nগুরুত্বপূর্ণ তথ্য যাচাই করুন এবং নিরাপদ থাকুন।\n\n#জীবনজ্ঞান৩৬৫",
            "visual_hint":"আজকের জীবনজ্ঞান"}

if __name__ == "__main__":
    main()
