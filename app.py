from io import SEEK_CUR
from flask import Flask, request
import base64,hashlib,hmac #署名検証用
import os,sys
import psycopg2

app = Flask(__name__)
user_id_list = []
resistrated_user_id_list = []

debug = os.environ.get('IS_DEBUG') == 'True' #デバッグ用のフラグ

#環境変数からchannel_secretを取得
CHANNEL_SECRET  = os.environ.get('CHANNEL_SECRET')

@app.route('/')
def index():
    return 'Not found!!',404,{}

@app.route('/webhock', methods=['POST'])
def webhock():
    data = request.get_json() #user_id抽出用のリクエストデータ(json)
    print('data_type:{}'.format(type(data)))
    body = request.get_data(as_text=True) #検証用のリクエストデータ(string)

    if debug == False:
        signature = request.headers.get('x-line-signature')
    elif debug == True:
        signature = request.headers.get('Content-Type')

    if validation(body=body, signature=signature.encode('utf-8')) == True: #イベントの真贋判定
        print("This is regular")

        try:
            for line in data["events"]:
                user_id_list.append(line["source"]["userId"])

                #DBから登録されているuser_idのリストを取得
                sql = "SELECT user_id FROM public.user;"
                print('executed SQL:{}'.format(sql))
                coursor.execute(sql)
                reistrated_user_id_list = list(coursor.fetchall())
                conn.commit()

                #resistrated_usr_id_listとuser_id_listの差分を求める
                filted_user_id_list = list(filter(lambda x:x not in resistrated_user_id_list, user_id_list))

                #DBへの登録
                for id in filted_user_id_list:
                    sql = "INSERT INTO public.user(user_id) VALUES ('{}');".format(id)
                    coursor.execute(sql)
                    conn.commit()
                    print('executed SQL:{}'.format(sql))

        except psycopg2.Error as e:
            print('DBへの書き込みエラー')
            print(e.pgerror)
            #coursorの更新
            conn.commit()

    else:
        print("This is not regular")
        return '',200,{}

    return '',200,{}

#署名検証用の関数
def validation(body,signature):
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    val_signature = base64.b64encode(hash)

    #デバッグ用のバイパス(完成後削除すること)
    if debug == True:
        return True

    if val_signature == signature:
        return True
    else:
        return False

#DB接続用の関数
def db_connect():
    #環境変数からデータベースの情報を取得
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASE_PORT = os.environ.get('DATABASE_PORT')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    DATABASE_USER = os.environ.get('DATABASE_USER')
    DATABASE_USER_PASS = os.environ.get('DATABASE_USER_PASS')

    #接続先文字列の生成
    connection_info = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
        user=DATABASE_USER,
        password=DATABASE_USER_PASS,
        host=DATABASE_URL,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME
    )

    print('Connecting:{info}'.format(info=connection_info))
    conn = ''
    try:
        conn = psycopg2.connect(connection_info)
    except psycopg2.Error: 
        print('Database connection failed!!') #DBとの接続に失敗した場合は終了する
        sys.exit()

    return conn

#DB操作用のカーソルを作成
conn = db_connect()
coursor = conn.cursor()

if __name__ == '__main__':
    app.run()