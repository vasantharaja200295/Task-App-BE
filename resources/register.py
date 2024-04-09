from flask_restful import Resource, reqparse
import datetime
from bcrypt import hashpw, gensalt

class Register(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True,
                        help="username cannot be blank.")
    parser.add_argument('firstName', required=True,
                        help="First name cannot be blank.")
    parser.add_argument('lastName', required=True,
                        help="Last name cannot be blank.")
    parser.add_argument('email', required=True, help="Email cannot be blank.")
    parser.add_argument('password', required=True,
                        help="Password cannot be blank.")
    parser.add_argument('confirmPassword', required=True,
                        help="Confirm password cannot be blank.")

    def post(self):
        from main import db_service
        data = Register.parser.parse_args()
        hashed_password = hashpw(
            data.get('password').encode('utf-8'), gensalt())
        reg_data = {
            'username': data.get('username'),
            'created_at': str(datetime.datetime.now()),
            'display_name': data.get('firstName') + ' ' + data.get('lastName'),
            'email': data.get('email'),
        }
        reg_data.update(data)
        reg_data['password'] = hashed_password
        reg_data.pop('confirmPassword')
        res = db_service.register_user(reg_data)
        return res
