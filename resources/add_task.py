from flask_restful import Resource, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required


class AddTask(Resource):
    @jwt_required()
    def post(self):
        from app import db_service
        data = request.get_json()
        res = db_service.create_task(data)
        if res:
            return {"status": HTTPStatus.OK, "message": "Task Added Successfully"}
        else:
            return {"status": HTTPStatus.INTERNAL_SERVER_ERROR, "message": "Error while adding task"}
