from flask_restful import Resource, reqparse
from http import HTTPStatus
from flask_jwt_extended import create_access_token
import datetime

class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True, help="Username cannot be blank.")
    parser.add_argument('password', required=True, help="Password cannot be blank.")

    def post(self):
        from app import db_service
        data = self.parser.parse_args()
        username = data['username']
        password = data['password']
        user_data = db_service.login_user(username, password)
        if user_data:
            expires = datetime.timedelta(days=3)
            access_token = create_access_token(identity=user_data.get('_id'), expires_delta=expires)
            user_data.pop('password')
            user_data['access_token'] = access_token
            return user_data, HTTPStatus.OK
        return {"error": "Invalid username or password"}, HTTPStatus.UNAUTHORIZED
