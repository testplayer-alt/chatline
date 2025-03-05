from flask import Flask

app = Flask(__name__)

@app.route('/callback', methods=['POST'])
def callback():
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)