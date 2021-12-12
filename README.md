# 使用時の注意
環境変数に以下のものを設定すること
- CHANNEL_ACCESS_TOKEN (LINE MESSAGE APIのアクセストークン)
- CHANNEL_SECRET (LINE APIのチャンネルシークレット)
- DATABASE_URL (形式は下記で指定したものを使用すること)

# DATABASE_URLの仕様
```bash
postgres://{USER_NAME}:{USER_PASSWORD}@{HOST_URL}:{HOST_PORT}/{DATABASE_NAME}
```

# 実行環境
下記のものをインストールすること
- PostgreSQL (version 13.5)
- Python3 (requirements.txtに記載のライブラリがすべて実行できるバージョン)

下記のものを用意すること
- ドメイン(サブドメインでも可)
- ドメインに対して発行されたSSL証明書