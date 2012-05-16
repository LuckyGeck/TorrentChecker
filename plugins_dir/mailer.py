#-------------------------------------------------------------------------------
# Name:        mailer
# Purpose:      Sends Mail Notiffication from gmail acc with HTML contents
#
# Author:      Pavel Sychev
#
# Created:     11.03.2012
# Copyright:   (c) Pavel 2012
# Licence:     GNU GPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# -*- coding: utf-8 -*-

def build_table(contents):
    beg_text = '''<html>
    <head></head>
    <body>
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#333333">
    <tr>
        <td>
    		<table width="600" border="1" align="center" cellpadding="0" cellspacing="5" bgcolor="#ffffff">
    		'''
    end_text = '''
    		</table>
    	</td>
       </tr>
    </table>
    </body>
    </html>'''
    return beg_text + contents + end_text;
    pass

def sendEmail(fromaddr, password, toaddrs, html_text, mail_text):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.header import Header
    import email


    mail_coding = 'cp1251'
    multi_msg = MIMEMultipart('alternative')
    multi_msg['From'] = fromaddr
    multi_msg['To'] = toaddrs
    multi_msg['Subject'] =  'New episode of serial'

    html_text = str(html_text.encode("cp1251"))
    mail_text = str(mail_text.encode("cp1251"))

    html_msg = MIMEText(html_text, 'html')
    text_msg = MIMEText(mail_text, 'plain')

    multi_msg.attach(text_msg)
    multi_msg.attach(html_msg)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, password)
    server.sendmail(fromaddr, toaddrs, multi_msg.as_string())
    server.quit()
    print 'Message sent!'

if __name__ == '__main__':
    print '''Usage:
    import mailer
    ...
    creating body table:
    html_body = mailer.build_table(mail_body)
    ...
    mailer.sendEmail('FromMail', 'FromPassword', 'ToMail', html_body, simple_text_body)'''
