from flask import jsonify, request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import jwt_required


class UpdateTaskData(Resource):

    @jwt_required()
    def post(self):
        from main import db_service
        data = request.get_json()
        res = db_service.update_task_data(data.get('id'), data)
        if res:
            return {'status': HTTPStatus.OK, 'data': 'Task updated successfully'}
        else:
            return {'status': HTTPStatus.INTERNAL_SERVER_ERROR, 'data': 'Error while updating task'}
