from flask_mail import Message
from flask import render_template
from constants import TASK_STATUS


class email_service:
    def gen_msg(self, status, data):
        reciever = data.get('assigned_to').get('email')
        subject = f"Task {TASK_STATUS.get(status)['value']}: {data.get('task_name')}"
        content = render_template(f"task_{TASK_STATUS.get(status)['value'].lower()}.html", data=data)
        msg = Message(recipients=[reciever], subject=subject)
        msg.html = content
        return msg
    
    def send_email(self, msg):
        from main import mail
        print(mail)
        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(e)
            return False  