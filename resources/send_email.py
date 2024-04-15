from flask_restful import Resource, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from services import email_service
from datetime import datetime




class SendEmail(Resource):
    @jwt_required()
    def post(self):
        from main import db_service, email
        data = request.get_json()
        status = data.get('status')
        _id = data.get('id')
        task_data = db_service.get_task_item(_id)
        date_obj = datetime.strptime(task_data.get('due_date'), "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_date = date_obj.strftime("%d/%b/%Y")
        task_data.update({'due_date': formatted_date})
        res = email.gen_msg(status=status, data=task_data)
        if res:
            return {"status": HTTPStatus.OK, "data": "Email sent successfully"}
        else:
            return {"status": HTTPStatus.INTERNAL_SERVER_ERROR, "data": "Error while sending email"}
