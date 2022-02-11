from email.mime.text import MIMEText
import smtplib
from email.header import Header

import settings


def sendMail(event_id, meetingId, meetingPass, meetingURL):
    cset = 'utf-8'
    username = settings.username()
    password = settings.password()
    from_address = settings.fromAdress()
    to_address = settings.toAdress(event_id)
    title = settings.title()
    body = settings.body().format(meetingId, meetingPass, meetingURL)
    con = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # FQDN とポート番号
    con.login(username, password)

    con.set_debuglevel(True)

    cset = 'utf-8'

    message = MIMEText(body, 'plain', cset)
    message['Subject'] = Header(title, cset)
    message['From'] = from_address
    message['To'] = to_address

    con.sendmail(from_address, [to_address], message.as_string())

    con.close()