from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        from main import db_service
        user_id = get_jwt_identity()
        analytics = db_service.get_analytics_data(user_id)
        tasks = db_service.get_today_tasks(user_id)
        res = {
            'analytics': analytics,
            'tasks': tasks
        }
        return {'status': HTTPStatus.OK, 'data': res}
    
    

