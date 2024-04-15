import os
from flask import render_template
from constants import TASK_STATUS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class email_service:
    def __init__(self):
        self.smtp_server = 'smtp.gmail.com.'
        self.smtp_port = 587 
        self.email = os.getenv("GOOGLE_EMAIL")  
        self.password = os.getenv('GOOGLE_ACCOUNT_KEY')  

    def send_email(self, to_email, subject, content):
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        try:
            server.starttls()
            server.login(self.email, self.password)

            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = ', '.join(to_email)
            msg['Subject'] = subject

            msg.attach(MIMEText(content, 'html'))

            server.sendmail(self.email, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            server.quit()

    def gen_msg(self, status, data):
        print(data)
        recievers = [data.get('created_by')['email'], data.get('assigned_to').get('email')]
        subject = f"Task {TASK_STATUS.get(status)['label']}: {data.get('task_name')}"
        if status == 'created':
            content = render_template('task_created.html', data=data)
        else:
            content = render_template("task_status.html", data=data)
        res = self.send_email(recievers, subject, content)
        return res
