TCABotのソースコードです。基本的にTCAPC-rightで動作させることを想定しています。

## 環境構築
1. コマンドプロンプトで`py -m pip install requirements.txt`を実行し、必要なライブラリをインストールしてください。
2. MySQLをインストールしてください。(環境によってセットアップが異なるため詳細は省略)
3. `sample.env`というファイルをコピーし名前を`.env`に変えた上で、必要な中身を入力してください。
4. `cogs/_hidden_data.py`を作成し、以下の形式で必要な情報を記入してください。
```py
TCA_MEMBERS = {
    12345678901234567890: "Real Name",
}  # TCA部員の、discordユーザーIDと本名の対応を表す

# フォームURL (リンクやエントリの番号はフェイクです。)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScs8n9l3mXo2a7e5j0ZtqkK8n9u2v6h1z5g9y0x1a2b3c4d5e6f7g8h9i0j/viewform?usp=pp_url&entry.123456789={mode}&entry.987654321={user}&entry.111111111={date}&entry.222222222={now}"
```
## 動作方法
1. MySQLを起動させておいてください。常時起動で問題ありません。
2. `py main.py`でBotを起動できます。