from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

class GetUser(Resource):
    @jwt_required()
    def get(self):
        from main import db_service
        uid = get_jwt_identity()
        res = db_service.get_user(uid)
        res['data'].pop('password')
        return res, 200
