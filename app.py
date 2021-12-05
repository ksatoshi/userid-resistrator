from io import SEEK_CUR
from flask import Flask, request
import base64,hashlib,hmac #署名検証用
import yaml

app = Flask(__name__)
user_ids = []

debug = False #デバッグ用のフラグ

with open('settings.yml','r') as yml:
        settings = yaml.safe_load(yml)
        channel_secret = settings['message_api']['channel_secret'] #channel_secretの設定

@app.route('/')
def index():
    return "Hello World"

@app.route('/webhock', methods=['POST'])
def webhock():
    data = request.get_json() #user_id抽出用のリクエストデータ(json)
    body = request.get_data(as_text=True) #検証用のリクエストデータ(string)

    if debug == False:
        signature = request.headers.get('x-line-signature')
    elif debug == True:
        signature = request.headers.get('Content-Type')

    if validation(body=body, signature=signature.encode('utf-8')) == True:
        print("This is regular")

        try:
            for line in data["events"]:
                user_ids.append(line["source"]["userId"])

            if debug == True:
                print(user_ids) #デバッグ用の表示　完成時に削除すること
        except:
            print("json error")
    else:
        print("This is not regular")

    return '',200,{}

#署名検証用の関数
def validation(body,signature):
    hash = hmac.new(channel_secret.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    val_signature = base64.b64encode(hash)

    if debug == True:
        print('signature:'+str(signature))
        print('val_signature'+str(val_signature))

        print("val_signature type:"+str(type(val_signature)))
        print("signature type:"+str(type(signature)))

    if val_signature == signature:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run()