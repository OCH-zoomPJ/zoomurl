import time
import threading

import getEvent
import zoom
import zoomGet
import calendarSurveillance

def worker():
    try:
        # Googleカレンダーから予定を取得して、Zoom予約表(DB)に登録
        getEvent.main()
        
        # Zoomミーティングの作成
        zoom.main()
        
        #
        #zoomGet.main()
        
        # カレンダーチェック（削除処理確認）
        calendarSurveillance.main()
        
        # 8秒ごとに待つ
        time.sleep(8)
        
    except TypeError:
        pass

def mainloop(time_interval, f):
    now = time.time()
    
    # 処理を永遠とループ
    while True:
        
        # workerをスレッド（並列）処理する
        t = threading.Thread(target=f)
        t.setDaemon(True)
        t.start()
        t.join()
        wait_time = time_interval - ( (time.time() - now) % time_interval )
        time.sleep(wait_time)

# mainloopを呼び出し(5秒ごとに実行する設定)
mainloop(5, worker)