import datetime
import sqlite3

# (getEvent.py関連)
# カレンダー情報の取得を開始する日付の設定 (現在は今日の日付で設定)
def timefrom():
    return datetime.date.today().strftime('%Y/%m/%d')
# カレンダー情報の取得を終了する日付の設定
def timeto():
    return "2024/12/31"
# 使用するカレンダーIDの設定
def calenderID():
    return "XXXXXXXXXX@gmail.com"
# 説明欄関連のkeyword設定（現在はzoomで設定）
def keyword():
    return "zoom"


# (zoom.py関連)
# zoomに登録しているemailの設定
def email():
    return "XXXXXXXXXX@gmail.com"
# zoomのAPI Keyの設定
def apiKey():
    return "XXXXXXXX"
# zoomのAPI Secretの設定
def apiSecret():
    return "XXXXXXXX"
# zoomのuserIdの設定
def zoomUserId():
    return "zoomのuserIdを入れてね"


# （sendMail.py関連）
# APIを利用するメルアドの設置
def username():
    return "XXXXXXXXXX@gmail.com"
# gmailのアプリのパスワードの設定
def password():
    return "XXXXXXXXXXXX"
# メールの送信元アドレス設定
def fromAdress():
    return "XXXXXXXXXX@gmail.com"
# どこにメールを送るのかの設定
def toAdress(event_id):
    con = sqlite3.connect('C:/Users/XXXX/zoom/zoom_url.db')
    c = con.cursor()
    t = (event_id,)
    c.execute('SELECT creator_email FROM zoom_url WHERE event_id=?;', t)
    creator_email = c.fetchone()
    return creator_email[0]
# メールのタイトル文設定
def title():
    return u'オンライン市役所運営事務局からの「zoom meeting」取得完了のお知らせ'
# メール本文の設定
def body():
    return u'''*このメールは自動送信されています。*\n\n
お世話になっております。\n
オンライン市役所運営事務局です。\n
GoogleCalendarで登録された「zoom meeting」の使用予約については、
無事予約が完了しましたのでお知らせいたします。\n
招待URL及びIDなどについては下記の通りですので、
課内の皆様にお知らせ下さい。\n\n
ミーティングID:{}\n
パスワード:{}\n
招待URL:{}\n\n
今後ともどうぞ宜しくお願いいたします。
'''