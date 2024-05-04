from flask import request, jsonify
from http import HTTPStatus
from utils import Utils

utils = Utils()

def check_token_expiry():
    
    if request.path in ['/api/login', '/api/register', '/api/cron/task-reminder']:
            return None
        
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer'):
        token = auth_header.split()[1]
        res = utils.verify_token(token=token)
        if not res:
            return jsonify({"error": "Expired token"}), HTTPStatus.UNAUTHORIZED
