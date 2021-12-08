# 使用時の注意
環境変数に以下のものを設定すること
- CHANNEL_ACCESS_TOKEN (LINE MESSAGE APIのアクセストークン)
- CHANNEL_SECRET (LINE APIのチャンネルシークレット)
- DATABASE_NAME (データベースのエンドポイント)
- DATABASE_PORT (データベースのエンドポイントのポート番号)
- DATABASE_NAME (データベース名)
- DATABASE_USER (データベースの接続ユーザー名)
- DATABASE_USER_PASS (データベースのの接続ユーザーパスワード)

# 実行環境
下記のものをインストールすること
- PostgreSQL (version 13.5)
- Python3 (requirements.txtに記載のライブラリがすべて実行できるバージョン)

下記のものを用意すること
- ドメイン(サブドメインでも可)
- ドメインに対して発行されたSSL証明書