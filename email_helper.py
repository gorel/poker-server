import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app as app
from flask.ext.appconfig import AppConfig

def send_email(email, subject, text, html=None):
    username = app.config['SMTP_USERNAME']
    password = app.config['SMTP_PASSWORD']

    server = app.config['SMTP_SERVER']
    port = app.config['SMTP_PORT']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = email

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP_SSL(server, port)
    s.login(username, password)
    s.sendmail(username, email, msg.as_string())
    s.quit()
