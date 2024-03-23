import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from dotenv import load_dotenv
import datetime
from db_service import Service
from statusCodes import status_codes
from flask_mail import Mail
from email_service import email_service

load_dotenv('.env')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'str0m141v@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
mail = Mail(app)
CORS(app)
jwt = JWTManager(app)
db_service = Service()
email = email_service()


@app.before_request
def check_token_expiry():
    if request.path == '/api/login':
        return None 
    
    if request.path == '/api/register':
        return None 

    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer'):
        token = auth_header.split()[1]
        decoded_token = decode_token(token)
        exp_time = datetime.datetime.fromtimestamp(decoded_token['exp']) 
        current_time = datetime.datetime.now()  

        if current_time > exp_time:
            return jsonify({"error": "Expired token"}), 401


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_data = db_service.login_user(username, password)
    if user_data:
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=user_data.get('_id'), expires_delta=expires)
        user_data.pop('password')
        user_data['access_token'] = access_token
        return jsonify(user_data), 200
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    reg_data = {
        'user_name': data.get('username'),
        'password': data.get('password'),
        'created_at': datetime.datetime.now(),
        'display_name': data.get('display_name'),
        'email':data.get('email'),
    }
    res = db_service.register_user(reg_data)
    if status_codes.get(res['status']):
        return jsonify(res), res['status']
    else:
        return jsonify(res), res['status']


@app.route('/api/get-user', methods=['GET'])
@jwt_required()
def get_user():
    uid = get_jwt_identity()
    res = db_service.get_user(uid)
    res['data'].pop('password')
    return jsonify(res), 200


@app.route('/api/onboarding', methods=["POST", 'GET'])
@jwt_required()
def onboarding():
    uid = get_jwt_identity()
    if request.method == 'POST':
        data = request.get_json()
        res = db_service.set_onboading(uid, data)
        if status_codes.get(res['status']):
            return jsonify(res), res['status']
        else:
            return jsonify(res), res['status']
    else:
        res = db_service.get_onboarding()
        return jsonify(res)


@app.route('/api/tasks/add-task', methods=["POST"])
@jwt_required()
def add_task():
    data = request.get_json()
    res = db_service.create_task(data)
    if res:
        return jsonify(res), 200
    else:
        return jsonify(res), 401
    
@app.route("/api/tasks/update-status", methods=["POST"])
@jwt_required()
def update_status():
    data = request.get_json()
    res = db_service.update_task_status(data.get('id'), data.get('status'))
    if res:
        return jsonify(res), 200
    else:
        return jsonify(res), 401

@app.route("/api/tasks/update-task", methods=["POST"])
@jwt_required()
def update_task():
    data = request.get_json()
    res = db_service.update_task_data(data.get('id'), data)
    if res:
        return jsonify(res), 200
    else:
        return jsonify(res), 401
    
@app.route('/api/tasks/list', methods=['POST'])
@jwt_required()
def list_tasks():
    req = request.get_json()
    if created_by := req.get("created_by"):
        res = db_service.get_tasks(True, created_by)
        return jsonify(res), 200
    else:
        res = db_service.get_tasks(False, req.get('assigned_to'))
        return res, 200

@app.route("/api/send-mail", methods=["POST"])
@jwt_required()
def index():
    req = request.get_json()
    status = req.get('status')
    data = req.get('data')
    msg = email.gen_msg(status=status, data=data)
    try:
        mail.send(msg)
        return {"status":200, }
    except Exception as e:
        return {"status":401, "message":e}


if __name__ == '__main__':
    app.run(debug=True)