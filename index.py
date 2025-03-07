from flask import Flask, request, abort
import os
import google.generativeai as genai
import requests

app = Flask(__name__)

# LINE Messaging APIの設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
if not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN environment variable not set.")
LINE_API_ENDPOINT = "https://api.line.me/v2/bot/message/reply"

# Gemini APIの設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# プロンプトテンプレートを読み込む
try:
    with open("prompt_template.txt", "r", encoding="utf-8") as f:
        PROMPT_TEMPLATE = f.read()
except FileNotFoundError:
    PROMPT_TEMPLATE = "あなたは優秀なアシスタントです。{user_message}について答えてください。" # ファイルが見つからない場合のデフォルトプロンプト
except Exception as e:
    PROMPT_TEMPLATE = f"プロンプトテンプレートの読み込み中にエラーが発生しました: {e}" #その他のエラー

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json()
    for event in body['events']:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            user_message = event['message']['text']
            reply_token = event['replyToken']
            try:
                # プロンプトを設定
                prompt = PROMPT_TEMPLATE.format(user_message=user_message)
                response = model.generate_content(prompt)
                reply_text = response.text
            except Exception as e:
                if "429 Resource has been exhausted" in str(e):
                    reply_text = "ただいまAPIの利用上限に達しました。しばらく時間をおいてから再度お試しください。"
                else:
                    reply_text = f"エラーが発生しました: {e}"
            # LINEに返信
            send_line_reply(reply_token, reply_text)
    return 'OK'

def send_line_reply(reply_token, reply_text):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": reply_text
        }]
    }
    response = requests.post(LINE_API_ENDPOINT, headers=headers, json=data)
    if response.status_code != 200:
        print(f"LINE API error: {response.content}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)