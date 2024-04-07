import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from services import DBService
from middleware import check_token_expiry
from resources import Login, Register, GetUser, Onboarding, AddTask, GetTasks, UpdateStatus, UpdateTaskData

load_dotenv('.env')

app = Flask(__name__)
api = Api(app)

# Config
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# initialization
CORS(app)
env = os.getenv('ENV')
jwt = JWTManager(app)
db_service = DBService(env)


#  Resources
api.add_resource(Login, '/api/login')
api.add_resource(Register, '/api/register')
api.add_resource(GetUser, '/api/get-user')
api.add_resource(Onboarding, '/api/onboarding')
api.add_resource(AddTask, '/api/tasks/add-task')
api.add_resource(GetTasks, '/api/tasks/get-tasks')
api.add_resource(UpdateStatus, '/api/tasks/update-status')
api.add_resource(UpdateTaskData, '/api/tasks/update-task-data')

# middleware
app.before_request(check_token_expiry)


if __name__ == '__main__':
    app.run(debug=True)
