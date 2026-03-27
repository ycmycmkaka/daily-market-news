import os
import datetime
import json
import urllib.request
import sys

# 攞 GitHub Secrets 入面嘅 API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ 錯誤：搵唔到 API Key！")
    sys.exit(1)

today_str = datetime.datetime.now().strftime("%Y年%m月%d日")
data_file = 'news_data.html'

# 讀取現有嘅新聞數據
existing_content = ""
if os.path.exists(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()

# 防重複機制：檢查今日新聞係咪已經存在
if f"🗓️ {today_str}" in existing_content:
    print(f"✅ 今日 ({today_str}) 嘅新聞已經存在，停止更新。")
    sys.exit(0)

prompt = f"""
你係一個專業嘅財經同政治新聞編輯。請幫我總結今日（{today_str}）嘅重要新聞。
要求：
1. 選出 5-10 條最重要嘅新聞，必須涵蓋：環球股市、香港股市、以及影響環球局勢嘅重大政治新聞。
2. 每條新聞用一段簡短文字總結，並加上一句分析（點樣影響市場或環球局勢）。
3. 語言必須係流暢嘅繁體中文（香港習慣用語）。
4. 直接以 HTML 格式輸出，絕對唔好包含 ```html 呢啲 Markdown 標籤。

格式要求必須完全跟隨以下結構：
<div class="daily-news">
    <h2>🗓️ {today_str} 新聞總結</h2>
    <ul>
        <li><strong>[新聞分類] 新聞標題：</strong>新聞內容同埋市場分析。</li>
        <li><strong>[新聞分類] 新聞標題：</strong>新聞內容同埋市場分析。</li>
    </ul>
</div>
"""

domain = "https://" + "generativelanguage.googleapis.com"
endpoint = "/v1beta/models/gemini-2.5-flash:generateContent?key="
url = domain + endpoint + api_key

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "tools": [{"googleSearch": {}}]
}

headers = {'Content-Type': 'application/json'}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers)

print("正在請求 Gemini 2.5 生成新聞...")
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
except Exception as e:
    print(f"❌ API 請求失敗: {e}")
    sys.exit(1)

try:
    new_content = result['candidates'][0]['content']['parts'][0]['text']
    new_content = new_content.replace('```html', '').replace('```', '').strip()
except KeyError:
    print("❌ 解析 API 回應時發生錯誤。")
    sys.exit(1)

# 將新新聞放喺最頂，然後駁埋舊新聞
updated_content = f"{new_content}\n\n{existing_content}"

with open(data_file, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print(f"✅ 成功將 {today_str} 嘅新聞寫入 {data_file}！")
