from flask_restful import Resource, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required


class WorkspaceDetails(Resource):
    @jwt_required()
    def get(self):
        from main import db_service
        uid = request.get_json().get('_id')
        res = db_service.get_workspace_details(uid)
        return {"status": HTTPStatus.OK, "data": res}