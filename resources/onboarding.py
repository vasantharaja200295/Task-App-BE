from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

class Onboarding(Resource):
    @jwt_required()
    def post(self):
        from main import db_service
        uid = get_jwt_identity()
        data = request.get_json()
        res = db_service.set_onboarding(uid, data)
        return res

    def get(self):
        from main import db_service
        res = db_service.get_onboarding()
        return res
