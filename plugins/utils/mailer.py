﻿# -*- coding: utf-8 -*-

# Author:       Sychev Pavel
# Created:      11.03.2012
# Copyright:    (c) Sychev Pavel 2017
# Licence:      GPL


def build_table(contents):
    template = '''<html>
    <head></head>
    <body>
    <table width="100%" border="0" cellspacing="0" cellpadding="0"
        bgcolor="#333333">
    <tr>
        <td>
            <table width="600" border="1" align="center"
                cellpadding="0" cellspacing="5" bgcolor="#ffffff">
            {}
            </table>
        </td>
       </tr>
    </table>
    </body>
    </html>'''
    return template.format(contents)


def send_email(smtp_host, is_ssl, is_tls,
               login, password, from_addr, to_addr, html_text, mail_text):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    multi_msg = MIMEMultipart('alternative')
    multi_msg['From'] = from_addr
    multi_msg['To'] = to_addr
    multi_msg['Subject'] = 'New episodes to watch'

    html_msg = MIMEText(html_text, 'html')
    text_msg = MIMEText(mail_text, 'plain')

    multi_msg.attach(text_msg)
    multi_msg.attach(html_msg)

    if is_ssl:
        server = smtplib.SMTP_SSL(smtp_host, timeout=10)
    else:
        server = smtplib.SMTP(smtp_host, timeout=10)

    if is_tls:
        server.ehlo()
        server.starttls()
        server.ehlo()
    server.login(login, password)
    server.sendmail(from_addr, to_addr, multi_msg.as_string())
    server.quit()
    print('Message sent!')

if __name__ == '__main__':
    print('''Usage:
    import mailer
    ...
    creating body table:
    html_body = mailer.build_table(mail_body)
    ...
    mailer.sendEmail('SMTPHost', 'FromMail', 'FromPassword', 'ToMail', html_body, simple_text_body)''')
