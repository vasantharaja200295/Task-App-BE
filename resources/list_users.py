from flask_restful import Resource, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required


class ListUsers(Resource):
    @jwt_required()
    def post(self):
        from app import db_service
        req = request.get_json()
        res = db_service.get_users_list(req.get('dept_id'))
        return {"status": HTTPStatus.OK, "data": res}