from flask import Flask, request, render_template
import base64,hashlib,hmac #署名検証用
import os,sys
import psycopg2
import uuid
import secrets
from linebot.models import TextSendMessage
from linebot import(
    LineBotApi
)
import linebot

app = Flask(__name__)

#各定数を定義
DEBUG = os.environ.get('IS_DEBUG') == 'True' #デバッグ用のフラグ
CHANNEL_SECRET  = os.environ.get('CHANNEL_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ROOT_URL = os.environ.get('ROOT_URL')
CONSOLE_ROOT_URL = '{ROOT_URL}/control'.format(
    ROOT_URL=ROOT_URL
)

@app.route('/control/<uuid:id>')
def control_console(id):
    #DBへのコネクションを作成
    conn = db_connect()
    cursor = conn.cursor()

    #DB上にidが存在するかを確認
    sql = "SELECT EXISTS (SELECT * FROM public.verify WHERE id='{}');".format(id)
    if DEBUG == True:
        print('SQL EXECUTE:{}'.format(sql))
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()

    #データベース上に存在しない場合正規のリクエストではないため500を返す
    if result[0] == False:
        cursor.close()
        conn.close()
        return '',500,{}
    else:
        return render_template("control.html",title="登録",id=id)

@app.route('/control/form', methods=['POST'])
def control_form():
    #送信データから値を抽出
    user_uuid = request.form.get('user_uuid')
    user_accept = request.form.get('accept')

    #DBのコネクションを作成
    conn = db_connect()
    cursor = conn.cursor()

    #user_accept==onの時ユーザーを登録
    if user_accept == 'on':
        #DBからuserのidを取得
        sql = "SELECT user_id FROM public.verify WHERE id='{}';".format(user_uuid)
        if DEBUG == True:
            print('SQL EXECUTE:{}'.format(sql))
        cursor.execute(sql)
        user_id = cursor.fetchone()[0]
        conn.commit()

        #DBから函館の地域コードを取得
        sql = "SELECT id FROM public.area WHERE area_name='函館市';"
        if DEBUG == True:
            print('SQL EXECUTE:{}'.format(sql))
        cursor.execute(sql)
        area_id = cursor.fetchone()[0]
        conn.commit()

        #resistrationに登録
        sql = "INSERT INTO public.resistration(user_id,area_id) VALUES('{user_id}','{area_id}');".format(
            user_id = user_id,
            area_id = area_id
        )
        if DEBUG == True:
            print('SQL EXECUTE:{}'.format(sql))
        cursor.execute(sql)
        conn.commit()

        #verifyからユーザーを削除
        sql = "DELETE FROM public.verify WHERE id = '{}';".format(user_uuid)
        if DEBUG == True:
            print('SQL EXECUTE:{}'.format(sql))
        cursor.execute(sql)
        conn.commit()

        cursor.close()
        conn.close()

        return '<p>登録完了!!</p>'
    else:
        cursor.close()
        conn.close()

        return '',200,{}

@app.route('/webhock', methods=['POST'])
def webhock():

    data = request.get_json() #user_id抽出用のリクエストデータ(json)
    print('data_type:{}'.format(type(data)))
    body = request.get_data(as_text=True) #検証用のリクエストデータ(string)

    signature = request.headers.get('x-line-signature')

    conn = db_connect()

    if validation(body=body, signature=signature.encode('utf-8')) == True: #イベントの真贋判定
        if DEBUG == True:
            print('This is regular request!!')
        try:
            for line in data["events"]:
                user_id=''
                #ソースがユーザからのイベントである場合のみuser_idを抽出
                if line['source']['type'] == 'user':
                    user_id = line["source"]['userId']
                    if DEBUG == True:
                        print('user_id:{}'.format(user_id))
                else:
                    #ソースがユーザーからのイベントではない時400を返して処理を終える
                    return '',200,{}

                #DB操作用のカーソルを作成
                cursor = conn.cursor()

                #user_idが既にDB上に存在しているか確認する
                sql = "SELECT EXISTS (SELECT * FROM public.user WHERE user_id='{}');".format(user_id)
                if DEBUG == True:
                    print('SQL EXECUTE:{}'.format(sql))
                cursor.execute(sql)
                conn.commit()

                result = cursor.fetchone()
                print('Result:{}'.format(result))

                #存在しない時DBに登録
                if result[0] == False:
                    sql = "INSERT INTO public.user(user_id) VALUES('{}');".format(user_id)
                    if DEBUG == True:
                        print('SQL EXECUTE:{}'.format(sql))
                    cursor.execute(sql)
                    conn.commit()

                #イベントがmessageである時送信されたテキストの解析
                if line['type'] == 'message':
                    if line['message']['text'] == '登録' or line['message']['text'] == '初期設定':
                        #URL用のUUIDの生成
                        user_uuid = uuid.uuid4()

                        #DBからuserのidを取得
                        sql = "SELECT id FROM public.user WHERE user_id='{}'".format(user_id)
                        if DEBUG == True:
                            print('EXECUTE SQL:{}'.format(sql))
                        cursor.execute(sql)
                        id = cursor.fetchone()
                        conn.commit()

                        #認証用のコード(6桁)を作成
                        verify_code = secrets.randbelow(1100000)-100000
                        #認証用のコードをハッシュ化
                        verify_hash = hashlib.sha256(str(verify_code).encode()).hexdigest()

                        #DBにUUIDとverify_hash,userのidを記録
                        sql = "INSERT INTO public.verify(id,pass,user_id) VALUES ('{uuid}','{verify_pass}',{user_id});".format(
                            uuid=user_uuid,
                            verify_pass=verify_hash,
                            user_id=id[0]
                        )
                        if DEBUG == True:
                            print('SQL EXECUTE:{}'.format(sql))
                        cursor.execute(sql)
                        conn.commit()

                        #ユーザにURLと認証コードを送信

                        #URLを送信
                        url_msg = '管理用コンソール用URL\n{root_url}/{uuid}'.format(
                            root_url=CONSOLE_ROOT_URL,
                            uuid=user_uuid
                        )
                        verify_code_msg = '確認コードは{}です。webページに戻り入力してください'.format(
                            str(verify_code)
                        )
                        send_msg_with_line(user_id=user_id, msgs=[url_msg,verify_code_msg])

                        #DBとの接続を解除
                        cursor.close()
                        conn.close()
                
                #messageではない時200を返して処理を終了
                else:
                    return 'internal server error',200,{}

                #全ての処理が正常終了した時200を返す
                return '',200,{}

        except psycopg2.Error as e:
            print('DBへの書き込みエラー')
            print(e.pgerror)
            conn.close()

    else:
        #正規のリクエストではないため200を返して終了
        return 'internal server error',400,{}

#LINEユーザにメッセージを送信する関数
def send_msg_with_line(user_id,msgs):
    send_msg = TextSendMessage(text='')
    try:
        line_bot_api = LineBotApi(ACCESS_TOKEN)

        for msg in msgs:
            if DEBUG == True:
                print('SENDING MESSAGE:{}'.format(msg))
            send_msg = TextSendMessage(text=msg)
            line_bot_api.push_message(user_id,send_msg)
    except linebot.exceptions.LineBotApiError as e:
        print(e.error.message)
        print(e.error.details)

    for msg in msgs:
        if DEBUG == True:
            print('SENNDING MESSAGE:{}'.format(msg))

#署名検証用の関数
def validation(body,signature):
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    val_signature = base64.b64encode(hash)

    #ローカルでバック用のバイパス
    if DEBUG == True:
        return True

    if val_signature == signature:
        return True
    else:
        return False

#DB接続用の関数
def db_connect():
    #環境変数からデータベースの情報を取得
    DATABASE_URL = os.environ.get('DATABASE_URL')

    #接続先文字列の生成
    connection_info = DATABASE_URL

    print('Connecting:{info}'.format(info=connection_info))
    conn = ''
    try:
        conn = psycopg2.connect(connection_info)
    except psycopg2.Error: 
        print('Database connection failed!!') #DBとの接続に失敗した場合は終了する
        sys.exit()

    return conn

if __name__ == '__main__':
    app.run()