from flask import Flask, request
import base64,hashlib,hmac #署名検証用

app = Flask(__name__)
user_ids = []

debug = False #デバッグ用のフラグ

channel_secret = 'test secret'

@app.route('/')
def index():
    return "Hello World"

@app.route('/webhock', methods=['POST'])
def webhock():
    data = request.get_json() #user_id抽出用のリクエストデータ(json)
    body = request.get_data(as_text=True) #検証用のリクエストデータ(string)
    signature = request.headers['x-line-signature']

    validation(body=body, signature=signature)

    try:
        for line in data["events"]:
            user_ids.append(line["source"]["userId"])

        print(user_ids) #デバッグ用の表示　完成時に削除すること
    except:
        print("json error")

    return '',200,{}

#署名検証用の関数
def validation(body,signature):
    hash = hmac.new(channel_secret.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    val_signature = base64.b64encode(hash)

    print("val_signature:"+val_signature)
    print("signature:"+signature)

if __name__ == '__main__':
    app.run()