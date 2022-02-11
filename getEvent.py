import datetime
import os.path
import sqlite3
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import settings
import functions
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
                'C:/Users/XXXX/zoom/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    ###########################################
    #### Googleアカウントへの認証情報を取得 
    ###########################################
    try:
        # カレンダーを呼び出すための準備
        service = build('calendar', 'v3', credentials=creds)

        # 現在時刻取得
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        # カレンダー全体を取得
        events_result = service.events().list(calendarId=settings.calenderID(),
                                            timeMin=now,singleEvents=True,
                                            orderBy='startTime').execute()
        # カレンダーの予定を取得
        events = events_result.get('items', [])

        # 予定が何もなければ処理終了
        if not events:
            print('No upcoming events found.')
            return

        # カレンダーの予定をループで1個ずつ処理
        for event in events:
            # 予定の開始時刻取得
            start = event['start'].get('dateTime', event['start'].get('date'))
            # 時間の表示を整える
            start = functions.changeI(start)
            
            # 予定の終了時刻取得
            end = event['end'].get('dateTime', event['end'].get('date'))
            # 時間の表示を整える
            end = functions.changeI(end)
            
            # 予定時間を算出
            event_time = end - start

            # Zoomデータベースにアクセス
            con = sqlite3.connect('C:/Users/XXXX/zoom/zoom_url.db')
            cur = con.cursor()

            # カレンダーの予定id取得
            t = (event['id'],)
            
            # カレンダーの予定idをキーに、ZoomURLテーブルを取得実行
            cur.execute('SELECT * FROM zoom_url WHERE event_id=?;', t)
            # 取得した情報をもってくる（フェッチっていうよ）
            id_checker = cur.fetchall()

            # 取得した情報が見つからない（新規であることを確認）、もしくは、カレンダーの予定の説明に「zoom」があるか（大文字小文字区別なく）
            if not id_checker and re.search(settings.keyword(),event['description'], flags=re.IGNORECASE) :
                
                # グーグルカレンダーの予定とZoomURLテーブルの重複時間をチェック
                t = (end, start)
                cur.execute('SELECT * FROM zoom_url WHERE start <=? AND end >=?;', t)
                period_checker = cur.fetchall()

                # 重複時間がない場合
                if not period_checker:
                    # ZoomURLテーブルにカレンダーの予定を登録
                    cur.execute('INSERT INTO zoom_url VALUES (?,?,?,?,?,?,?,?,?)',
                                (event['id'], event['summary'], event['description'], start, end, event_time, event['creator']['email'], '', ''))
                    con.commit()
                    print('Successful registration to the database')
                    
                # 重複時間がある場合、処理をしない
                else:
                    print('No preiod')
            # ZoomURLテーブルにすでに予定がある、もしくは、説明に「Zoom」の記載がない場合は、何もしない
            else:
                print('No')

    # なんかエラーが出たら、エラーを表示する
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()