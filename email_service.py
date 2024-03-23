from flask_mail import Message
from flask import render_template


class email_service:
    def gen_msg(self, status, data):
        reciever = data.get('assigned_to_email')
        subject = f"Task Created: {data.get("task_name")}"
        content = render_template(f"{status}.html", data=data)
        
        msg = Message(recipients=[reciever], subject=subject)
        msg.html = content
        
        return msg