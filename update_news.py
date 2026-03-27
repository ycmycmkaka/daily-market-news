import os
import datetime
import json
import urllib.request
import sys

# 攞 GitHub Secrets 入面嘅 API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ 錯誤：搵唔到 API Key！請檢查 GitHub Secrets。")
    sys.exit(1)

# 獲取今日日期
today_str = datetime.datetime.now().strftime("%Y年%m月%d日")

# 先讀取 HTML，檢查今日係咪已經 update 咗 (防暴走機制 1)
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
except FileNotFoundError:
    print("❌ 錯誤：搵唔到 index.html 檔案！")
    sys.exit(1)

if f"🗓️ {today_str}" in html_content:
    print(f"✅ 今日 ({today_str}) 嘅新聞已經存在，為免重複，停止更新。")
    sys.exit(0)

prompt = f"""
你係一個專業嘅財經同政治新聞編輯。請幫我總結今日（{today_str}）嘅重要新聞。
要求：
1. 選出 5-10 條最重要嘅新聞，必須涵蓋：環球股市、香港股市、以及影響環球局勢嘅重大政治新聞。
2. 每條新聞用一段簡短文字總結，並加上一句分析（點樣影響市場或環球局勢）。
3. 語言必須係流暢嘅繁體中文（香港習慣用語）。
4. 直接以 HTML 格式輸出，絕對唔好包含 ```html 呢啲 Markdown 標籤，亦唔好自己生成 標記。

格式要求必須完全跟隨以下結構：
<div class="daily-news">
    <h2>🗓️ {today_str} 新聞總結</h2>
    <ul>
        <li><strong>[新聞分類] 新聞標題：</strong>新聞內容同埋市場分析。</li>
        <li><strong>[新聞分類] 新聞標題：</strong>新聞內容同埋市場分析。</li>
    </ul>
</div>
"""

# 使用 gemini-2.5-flash，並將網址拆開防 Markdown 錯誤
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
except urllib.error.HTTPError as e:
    print(f"❌ API 請求失敗 (HTTP {e.code}):")
    print(e.read().decode('utf-8'))
    sys.exit(1)
except Exception as e:
    print(f"❌ 發生未知網絡錯誤: {e}")
    sys.exit(1)

try:
    new_content = result['candidates'][0]['content']['parts'][0]['text']
    new_content = new_content.replace('```html', '').replace('```', '').strip()
except KeyError:
    print("❌ 解析 API 回應時發生錯誤，可能內容被安全機制攔截。")
    sys.exit(1)

# 寫入 HTML (防暴走機制 2：限制 replace 次數為 1)
marker = ""
if marker in html_content:
    updated_html = html_content.replace(marker, f"{marker}\n{new_content}", 1)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    print(f"✅ 成功更新 {today_str} 嘅新聞！")
else:
    print("❌ 錯誤：喺 index.html 搵唔到 標記！")
    sys.exit(1)
