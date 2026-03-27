import google.generativeai as genai
import os
import datetime

# 攞 GitHub Secrets 入面嘅 API Key
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 修正：使用正確嘅 'google_search_retrieval' 字串嚟開啟聯網功能
model = genai.GenerativeModel('gemini-1.5-flash', tools='google_search_retrieval')

# 獲取今日日期
today_str = datetime.datetime.now().strftime("%Y年%m月%d日")

prompt = f"""
你係一個專業嘅財經同政治新聞編輯。請幫我總結今日（{today_str}）嘅重要新聞。
要求：
1. 選出 5-10 條最重要嘅新聞，必須涵蓋：環球股市、香港股市、以及影響環球局勢嘅重大政治新聞。
2. 每條新聞用一段簡短文字總結，並加上一句分析（點樣影響市場或環球局勢）。
3. 語言必須係流暢嘅繁體中文（香港習慣用語）。
4. 直接以 HTML 格式輸出，唔好包含 ```html 呢啲 Markdown 標籤。

格式要求必須完全跟隨以下結構：
<div class="daily-news">
    <h2>🗓️ {today_str} 新聞總結</h2>
    <ul>
        <li><strong>[新聞分類] 新聞標題：</strong>新聞內容同埋市場分析。</li>
        <li><strong>[新聞分類] 新聞標題：</strong>新聞內容同埋市場分析。</li>
    </ul>
</div>
"""

try:
    print("正在請求 Gemini 生成新聞...")
    response = model.generate_content(prompt)
    new_content = response.text.replace('```html', '').replace('```', '').strip()
    
    # 讀取現有嘅 index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 搵到標記位，將新新聞插入去標記嘅正下方
    marker = ""
    if marker in html_content:
        updated_html = html_content.replace(marker, f"{marker}\n{new_content}")
        
        # 覆寫儲存 index.html
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print(f"✅ 成功更新 {today_str} 嘅新聞！")
    else:
        print("❌ 錯誤：搵唔到 標記！")

except Exception as e:
    print(f"❌ 發生錯誤: {e}")
