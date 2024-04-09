from flask_restful import Resource, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required

class DeleteTask(Resource):
    @jwt_required()
    def post(self):
        from app import db_service
        data = request.get_json()
        print(data)
        res = db_service.delete_task(data)
        if res:
            return {'status': HTTPStatus.OK, 'data': 'Task deleted successfully'}
        else:
            return {'status': HTTPStatus.INTERNAL_SERVER_ERROR, 'data': 'Error while deleting task'}