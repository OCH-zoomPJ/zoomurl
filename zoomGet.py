import http.client
import base64
import time
import hmac
import hashlib

import settings
import sqlite3

def main():
    
    # API情報を取得
    API_Key = settings.apiKey()
    API_Secret = settings.apiSecret()
    
    # 有効時間の設定（5秒）
    expiration = int(time.time()) + 5

    header    = base64.urlsafe_b64encode('{"alg":"HS256","typ":"JWT"}'.encode()).replace(b'=', b'') # ヘッダー
    payload   = base64.urlsafe_b64encode(('{"iss":"'+API_Key+'","exp":"'+str(expiration)+'"}').encode()).replace(b'=', b'') # APIキーと>有効期限
    hashdata  = hmac.new(API_Secret.encode(), header+".".encode()+payload, hashlib.sha256) # HMACSHA256でハッシュを作成
    signature = base64.urlsafe_b64encode(hashdata.digest()).replace(b'=', b'') # ハッシュをURL-Save Base64でエンコード
    token = (header+".".encode()+payload+".".encode()+signature).decode()  # トークンをstrで生成

    http_conn = http.client.HTTPSConnection("api.zoom.us")

    headers = {
        'authorization': "Bearer "+token,
        'content-type': "application/json"
        }

    userId = settings.zoomUserId() #zoomのuserIdを入れる
    http_conn.request("GET", f"/v2/users/{userId}/meetings", headers=headers)

    res = http_conn.getresponse()
    data = eval(res.read().decode("utf-8"))
    datas = data['meetings']

    # データベース開く
    db_conn = sqlite3.connect('C:/Users/XXXX/zoom/zoom_url.db')
    c = db_conn.cursor()
    for i in datas:
        # print(i['uuid'])
        t = (i['uuid'],)
        c.execute('SELECT uuid FROM zoom_meetings WHERE uuid=?;',t)
        mtgId = c.fetchall()
        if mtgId == []:
        # 取得したデータをデータベースに格納する
            c.execute("insert into zoom_meetings values(?, ?, ?, ?, ?, ?)",(i['uuid'], i['topic'], i['start_time'], i['duration'], i['created_at'], i['join_url']))
            db_conn.commit()
            db_conn.close()
        else:
            # すでにidがある場合は取得しない
            pass
    db_conn.close()