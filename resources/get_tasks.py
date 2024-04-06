from flask_restful import Resource, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity



class GetTasks(Resource):
    @jwt_required()
    def post(self):
        from app import db_service
        user_id = get_jwt_identity()
        is_admin = request.get_json().get('isAdmin')
        res = db_service.get_tasks(is_admin, user_id)
        return {"status": HTTPStatus.OK, "data": res}