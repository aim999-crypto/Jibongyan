# জীবনজ্ঞান ৩৬৫ — Telegram Automated Knowledge Channel

Android phone + GitHub Actions দিয়ে চালানোর starter project।

## কী করে
প্রতিদিন ২৪টি বাংলা পোস্টের queue তৈরি করে:
- ৮টি MP4 animated explainer (template-based motion graphics)
- ৬টি PNG infographic
- ৫টি text guide
- ৩টি quick tip
- ১টি quiz
- ১টি daily challenge

Telegram-এ প্রতিদিন ৬টি publishing window-তে ৪টি করে পোস্ট পাঠায়। সময়গুলো বাংলাদেশ সময় (UTC+6):
06:05, 09:05, 12:05, 15:05, 18:05, 21:05।

## গুরুত্বপূর্ণ বাস্তবতা
- ৳০ বাজেটে ২৪টি/দিনের **সম্পূর্ণ নতুন generative AI video/image** নিশ্চিত করা সম্ভব নয়। এই starter-এ Gemini API-এর free-tier থাকলে AI দিয়ে বাংলা লেখা/স্ক্রিপ্ট তৈরি হয়; ছবি ও ভিডিও স্থানীয় template renderer দিয়ে তৈরি হয়। তাই API key ছাড়া deterministic fallback content তৈরি হবে।
- Gemini free-tier-এর quota/availability Google পরিবর্তন করতে পারে। Free tier মানে সীমাহীন নয়।
- GitHub Actions scheduled workflow নির্দিষ্ট মিনিটে চলার নিশ্চয়তা দেয় না। Workflow delay হতে পারে।
- Telegram bot token ও channel-এ bot admin permission আবশ্যক।
- প্রকাশের আগে health/legal/financial/safety তথ্য যাচাই করুন। AI ভুল করতে পারে।

## 1) Telegram bot তৈরি
1. Telegram-এ `@BotFather` খুলুন, `/newbot` দিন।
2. Bot token কপি করুন।
3. আপনার channel-এ bot-কে Admin করুন; Post Messages permission দিন।
4. Public channel হলে `@YourChannelName` ব্যবহার করতে পারেন। Private channel হলে `-100...` numeric chat ID দিন।

## 2) GitHub repository
1. GitHub-এ নতুন repository তৈরি করুন: `jibon-gyan-365`
2. ZIP extract করে সব ফাইল repository root-এ upload করুন (Android browser থেকেও করা যায়)।
3. Settings → Secrets and variables → Actions → New repository secret:
   - `TELEGRAM_BOT_TOKEN` = BotFather token
   - `TELEGRAM_CHAT_ID` = `@channelusername` অথবা numeric chat ID
   - `GEMINI_API_KEY` = ঐচ্ছিক; Google AI Studio থেকে পাওয়া free-tier API key
4. Settings → Actions → General → Workflow permissions → **Read and write permissions** দিন।
5. Actions tab-এ গিয়ে workflow enable করুন।

## 3) প্রথমবার test
Actions → `Daily Content Generator` → Run workflow।
তারপর Actions → `Telegram Publisher` → Run workflow।
প্রথমে private test channel-এ পরীক্ষা করা ভালো।

## 4) Publishing schedule
প্রতিদিন 00:05 UTC-তে queue তৈরি হয় (বাংলাদেশে 06:05)।
Publish workflow 00:15, 03:15, 06:15, 09:15, 12:15, 15:15 UTC-তে চলে।
প্রতিবার ৪টি করে পোস্ট পাঠায়। মোট ২৪টি/দিন।

## 5) Android দিয়ে edit
GitHub repository → যে ফাইল edit করবেন → pencil icon → পরিবর্তন → Commit changes।
`config/settings.json`-এ channel branding, ভাষা, video duration, post count বদলাতে পারবেন।
`config/categories.json`-এ category list বদলাতে পারবেন।

## 6) Workflow কীভাবে কাজ করে
- Gemini key থাকলে Gemini থেকে JSON-ভিত্তিক বাংলা content plan চায়।
- API fail/quota শেষ হলে safe fallback templates ব্যবহার করে।
- `engine/render.py` Pillow দিয়ে infographic ও FFmpeg দিয়ে motion-graphics video বানায়।
- `publisher/telegram_bot.py` Telegram Bot API দিয়ে post করে।
- `database/queue.json`-এ queue এবং `database/published.json`-এ history থাকে।
- Workflow generated media সাময়িকভাবে তৈরি করে; GitHub repository-তে media commit করে না।

## Troubleshooting
- `chat not found`: bot-কে channel admin করুন, chat ID যাচাই করুন।
- `not enough rights`: Post Messages permission দিন।
- `GEMINI_API_KEY` না থাকলে AI text generation হবে না; fallback চলবে।
- FFmpeg error: GitHub runner-এ FFmpeg install step আছে।
- Actions schedule না চললে Actions manually run করুন; scheduled runs কখনও delayed হতে পারে।
- GitHub public repo-তে secret কখনও code-এ লিখবেন না।

## Free-tier note
GitHub Actions-এর usage limits/terms account ও সময় অনুযায়ী বদলাতে পারে। ২৪টি পোস্টের media generation runner time ব্যবহার করবে। API quota শেষ হলে workflow fallback-এ যাবে, কিন্তু AI-generated quality একই থাকবে না।
