import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from dotenv import load_dotenv
import datetime
from db_service import Service
from statusCodes import status_codes
from flask_mail import Mail, Message
from email_service import email_service
from utils import Utils

load_dotenv('.env')

app = Flask(__name__)
env = os.getenv('ENV')
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
db_service = Service(env)
email = email_service()
utils = Utils()


@app.before_request
@jwt_required(optional=True)
def check_token_expiry():
    """
    Check if the token is expired before each request. If the request path is for login, register, or task reminder, return None. Otherwise, verify the token and return an error message if it's expired.
    """
    if request.path == '/api/login':
        return None 
    
    if request.path == '/api/register':
        return None 
    
    if request.path == '/api/cron/task-reminder':
        return None

    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer'):
        token = auth_header.split()[1]
        res = utils.verify_token(token=token)
        if not res:
            return jsonify({"error": "Expired token"}), 401


@app.route('/api/login', methods=['POST'])
def login():
    """
    A function to handle user login. 
    Retrieves username and password from request data, 
    validates the user, generates an access token, 
    and returns user data with the access token if login is successful.
    
    Parameters:
    None
    
    Returns:
    JSON response with user data and status code
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_data = db_service.login_user(username, password)
    if user_data:
        expires = datetime.timedelta(days=3)
        access_token = create_access_token(identity=user_data.get('_id'), expires_delta=expires)
        user_data.pop('password')
        user_data['access_token'] = access_token
        return jsonify(user_data), 200
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    reg_data = {
        'password': data.get('password'),
        'created_at': datetime.datetime.now(),
        'display_name': data.get('firstName')+ ' '+ data.get('lastName'),
        'email':data.get('email'),
    }
    reg_data.update(data)
    reg_data.pop('confirmPassword')
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









# Cron ----------------

@app.route('/api/cron/task-reminder')
def cron():
    msg = Message( 
    'Hello', 
    sender ='str0m141v@gmail.com', 
    recipients = ['vasantharaja200295@gmail.com'] 
    ) 
    msg.body = 'Hello Flask message sent from Flask-Mail' + str(datetime.datetime.now())
    mail.send(msg) 
    return "message-sent"

# ---------------------



if __name__ == '__main__':
    app.run(debug=True)