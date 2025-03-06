import os
from flask import Flask, request, abort
# ... (他のインポート)

app = Flask(__name__)

# ... (他のコード)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) # 環境変数PORTを取得、なければ5000
    app.run(host="0.0.0.0", port=port)