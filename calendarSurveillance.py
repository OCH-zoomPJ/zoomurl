import jwt
import datetime
import os.path
import sqlite3
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import settings
from sendMail import sendMail

# googleapiを呼び出す際のスコープを設定（呼び出し専用）
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():

    ###########################################
    ### Googleアカウントへの認証情報を取得 
    ### credentials.jsonの確認
    ###########################################
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    ###########################################
    #### Googleアカウントへの認証情報を取得 
    ###########################################
    try:
        # Zoomデータベースに接続
        conn = sqlite3.connect('C:/Users/XXXX/zoom/zoom_url.db')
        c = conn.cursor()
        
        # ZoomURLテーブルの情報を取得
        c.execute('SELECT event_id FROM zoom_url;')
        event_ids = c.fetchall()
        
        # 取得したイベントIDをループ
        for event_id in event_ids:
            # カレンダー全体を取得(ループの外でいいかも)
            service = build('calendar', 'v3', credentials=creds)
            
            # カレンダーのイベントを取得
            event = service.events().get(
                calendarId=settings.calenderID(), 
                eventId=event_id[0]).execute()

            # ステータスが「キャンセル」でない場合
            if event['status'] != 'cancelled':
                pass
            
            # ステータスが「キャンセル」の場合
            else:
                
                #############################
                # ミーティング削除処理の開始
                #############################
                print('ここから処理開始するよ!')
                print(event_id[0])

                # zoom meetingの削除の処理
                conn = sqlite3.connect('C:/Users/XXXX/zoom/zoom_url.db')
                c = conn.cursor()
                
                # Zoom予約データテーブルを取得
                t = (event_id[0],)
                c.execute('SELECT meetingId FROM reservation_zoomData WHERE event_id=?;', t)
                
                # ミーティングIDを取得
                meetingId = c.fetchall()
                meetingId = (meetingId[0][0]).replace(' ','')

                # 現在の時刻を取得
                time_now = datetime.datetime.now()
                
                # 20秒後の時間を取得
                expireation_time = time_now + datetime.timedelta(seconds=20)
                rounded_off_exp_time = round(expireation_time.timestamp())
                
                # Zoom予約を操作するためのおまじない
                headers = {"alg": "HS256" , "typ": "JWT"}
                payload = {"iss": settings.apiKey() , "exp": rounded_off_exp_time}
                encoded_jwt = jwt.encode(payload, settings.apiSecret(), algorithm="HS256")
                
                url = f"https://api.zoom.us/v2/meetings/{meetingId}"
                headers = {"authorization": f"Bearer{encoded_jwt}"}
                response = requests.delete(url, headers=headers)
                print(response)

                # Zoom予約データテーブルの削除
                c.execute('DELETE FROM reservation_zoomData WHERE event_id=?;', event_id)
                
                # ZoomURLデータテーブルの削除
                c.execute('DELETE FROM zoom_url WHERE event_id=?;', event_id)
                
                # コミット
                conn.commit()

                print('Delete meeting!')
                
    except IndexError:
        pass
    
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()