from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
import json
from dotenv import load_dotenv
import os

load_dotenv('.env')

class MongoDB:
    def __init__(self, db_name='test_database', env='dev'):
        if env != 'dev':
            connection_string = f"mongodb+srv://{os.getenv('MONGOUSERNAME')}:{os.getenv('MONGOPASSWORD')}@cluster0.vpzkuqi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
        else:
            connection_string = os.getenv('MONGO_CONNETION_DEV')
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

    def create_document(self, collection_name, document):
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def read_documents(self, collection_name, query={}):
        collection = self.db[collection_name]
        documents = collection.find(query)
        return [self._serialize(doc) for doc in documents]

    def read_document(self, collection_name, query):
        collection = self.db[collection_name]
        document = collection.find_one(query)
        return self._serialize(document)

    def update_documents(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.update_many(query, {"$set": new_values})
        return result.modified_count

    def update_document(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.find_one_and_update(query, {"$set": new_values}, return_document=ReturnDocument.AFTER)
        return self._serialize(result)

    def delete_documents(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.deleted_count

    def delete_document(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.find_one_and_delete(query)
        return self._serialize(result)

    def _serialize(self, document):
        if document is None:
            return None
        if '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    
    
class Service:
    REGISTER_SUCCESS = 200
    REGISTER_USER_EXISTS = 400
    REGISTER_FAILURE = 500
    SUCCESS=200

    LOGIN_SUCCESS = 200
    LOGIN_FAILURE = 401
    def __init__(self, env):
        print("connected to: ", env)
        self.db = MongoDB('taskmanager', env=env)
    
    def login_user(self, username, password):
        return self.db.read_document('users', {'user_name': username, 'password': password})
    
    def register_user(self, data):
        existing_user = self.db.read_document('users', {'user_name': data['user_name']})
        if existing_user:
            return {"status":self.REGISTER_USER_EXISTS, 'message':'User Already Registered'}
        else:
            data['onboading_flow_completed'] = False
            data['dept'] = None
            data['role'] = None
            data['reports_to']  = None
            user_id = self.db.create_document('users', data)
            if user_id:
                return {"status":self.REGISTER_SUCCESS, "message":'User Successfully Registered'}
            else:
                return {"status":self.REGISTER_FAILURE, "message":'User Registration Failed'}
    
    
    def get_user(self, user_id):
        data = self.db.read_document('users',{'_id':ObjectId(user_id)})
        return {'status':self.SUCCESS, 'data':data}
    
    def set_onboading(self, user_id, data):
        user = self.get_user(user_id)['data']
        query={'_id':ObjectId(user.get('_id'))}
        if user:
            updated_data = {
                'dept':data.get('dept'),
                'role':data.get('role'),
                'onboading_flow_completed':True,
                'reports_to':data.get('reports_to')
            }
            res = self.db.update_document('users', query, updated_data)
            
            if res:
                return {'status':200, 'data':res}
            else:
                return {'status': 500, 'data':'Error failed to update'}
            
    def get_onboarding(self):
        depts = self.db.read_documents('dept')
        return {'status':200, 'data': depts}
    
    def create_task(self, data):
        res = self.db.create_document('tasks', data)
        return res
    
    def update_task_status(self, task_id, status):
        res = self.db.update_document('tasks', {'_id':ObjectId(task_id)}, {'status':status})
        return res
    
    def update_task_data(self, task_id, new_data):
        res = self.db.update_document('tasks', {'_id':ObjectId(task_id)}, new_data)
        return res
            
    def get_tasks(self, is_admin, user_id): 
        res = self.db.read_documents('tasks', {'created_by':user_id} if is_admin else {'assigned_to':user_id})
        return res