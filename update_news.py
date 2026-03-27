import google.generativeai as genai
import datetime

# 設定 API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# 使用 Gemini 3 Flash 並開啟 Google Search 功能 (Grounding)
model = genai.GenerativeModel('gemini-2.5-flash', tools=[{'google_search': {}}])

prompt = """
請幫我寫一份今日嘅新聞總結（日期：{today}）。
要求：
1. 選出 5-10 條最重要嘅新聞。
2. 焦點：環球股市、香港股市、以及重大國際政治新聞。
3. 語言：繁體中文（香港口語或書面語）。
4. 每條新聞要有簡短分析佢點樣影響市場。
5. 請以 HTML 格式輸出。
""".format(today=datetime.date.today())

response = model.generate_content(prompt)
news_content = response.text

# 將結果存入 news.html 或者更新到你的數據庫/JSON
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"<h1>每日新聞總結 - {datetime.date.today()}</h1>")
    f.write(news_content)
