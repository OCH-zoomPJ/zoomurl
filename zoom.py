import jwt
import datetime
import requests
import json
import sqlite3
import pandas as pd

import settings
import sendMail
import pass_gen


def main():
    # Zoomデータベースに接続
    conn = sqlite3.connect('C:/Users/XXXX/zoom/zoom_url.db')
    c = conn.cursor()

    # ZoomURLテーブルにあって、Zoom予約データテーブルにないものを取得
    c.execute('''
            SELECT event_id
            FROM zoom_url
            EXCEPT
            SELECT event_id
            FROM reservation_zoomData
            ;''')
    
    # データをリストにする
    difference_list = c.fetchone()

    try:
        # イベントIDのリストを取得
        t = (difference_list[0],)
        
        # ZoomURLテーブルを検索する
        c.execute('SELECT * FROM zoom_url WHERE event_id=?;', t)
        
        # 予約候補リストを取得
        reservation_list = c.fetchone()

    except TypeError:
        reservation_list = []
    
    # 予約候補リストが空っぽじゃなければ
    if reservation_list is not None:
        
        try:
            # 現在の時刻を取得
            time_now = datetime.datetime.now()
            
            # 20秒後の時間を取得
            expireation_time = time_now + datetime.timedelta(seconds=20)
            # コンマ秒を切り上げ？
            rounded_off_exp_time = round(expireation_time.timestamp())

            # Zoom予約のJWT認証の準備
            headers = {"alg": "HS256" , "typ": "JWT"}
            payload = {"iss": settings.apiKey() , "exp": rounded_off_exp_time}
            encoded_jwt = jwt.encode(payload, settings.apiSecret(), algorithm="HS256")
            
            # Gmail送信準備
            email = settings.email()

            # ミーティングURLの設定
            url = f"https://api.zoom.us/v2/users/{email}/meetings"

            # Zoomに登録できるように時間表示を整える
            date = pd.to_datetime(str(reservation_list[3])).strftime("%Y-%m-%dT%H: %M: %S")
            # 何かを右寄せ0埋め
            reservation_list5 = str(reservation_list[5]).zfill(6)

            # 予定の時間を色々整える
            event_time_H = reservation_list5[0:2]
            event_time_H = int(event_time_H)*60
            event_time_M = reservation_list5[2:4]
            event_time_M = int(event_time_M)
            event_time = event_time_H + event_time_M

            # Zoom予約に使うパラメータ（上で色々整えたもの）をobjに突っ込む
            obj = {"topic": reservation_list[1], "start_time": date, "duration": event_time, "password": pass_gen.pass_gen(10)}
            
            # 認証情報をheadersに突っ込む
            headers = {"authorization": f"Bearer{encoded_jwt}"}
            
            # post処理をし、ミーティング作成を実行
            creat_meeting = requests.post(url, json=obj, headers=headers)
            
            # 実行結果を取得
            response_data = json.loads(creat_meeting.text)

            # ミーティング情報を取得
            meetingId = response_data.get('id')
            meetingPass = response_data.get('password')
            meetingURL = response_data.get('join_url')

            # ミーティング情報をZoom予約データテーブルに登録
            t = (reservation_list[0], reservation_list[1], reservation_list[2], reservation_list[3], reservation_list[4], reservation_list[5], meetingId, meetingPass, meetingURL)
            c.execute("INSERT INTO reservation_zoomData VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", t)
            
            # コミット（登録を確定させる）
            conn.commit()
            
            # メールを送信
            sendMail.sendMail(reservation_list[0],meetingId, meetingPass, meetingURL)
        
        # indexエラーが出たら、何もしない
        except IndexError:
            pass
        
    # 予約候補リストがなければ、何もしない
    else:
        pass

    # データベースの接続をクローズ
    conn.close()