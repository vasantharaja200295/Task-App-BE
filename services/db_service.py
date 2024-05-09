from bson import ObjectId
from .mongo_db import MongoDB
from http import HTTPStatus
import datetime

date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

class DBService:

    def __init__(self, env):
        print("connected to: ", env)
        self.db = MongoDB('taskmanager', env=env)

    def login_user(self, username):
        return self.db.read_document('users', {'username': username})

    def register_user(self, data):
        existing_user = self.db.read_document(
            'users', {'username': data['username']})
        if existing_user:
            return {"status": HTTPStatus.CONFLICT, 'message': 'User Already Registered'}
        else:
            data['onboading_flow_completed'] = False
            data['dept'] = None
            data['role'] = None
            data['reports_to'] = None
            user_id = self.db.create_document('users', data)
            if user_id:
                return {"status": HTTPStatus.OK, "message": 'User Successfully Registered'}
            else:
                return {"status": HTTPStatus.INTERNAL_SERVER_ERROR, "message": 'User Registration Failed'}

    def get_user(self, user_id, status=None):
        if status == "completed":
            projection = {
                'password': 0,
                'email': 0,
                'role': 0,
                'username': 0,
                'firstName': 0,
                'lastName': 0,
                'onboading_flow_completed': 0,
                'reports_to': 0,
                'dept': 0,
                "created_at":0
            }
        else:
            projection = None

        data = self.db.read_document(
            'users', {'_id': ObjectId(user_id)}, projection)

        if data:
            return {'status': HTTPStatus.OK, 'data': data}
        else:
            return {'status': HTTPStatus.NOT_FOUND, 'message': 'User not found'}

    def get_users_list(self, dept_id):
        projection = {
            'password': 0,
            'role': 0,
            'username': 0,
            'firstName': 0,
            'lastName': 0,
            'onboading_flow_completed': 0
        }
        data = self.db.read_documents(
            'users', {'dept._id': dept_id}, projection)
        return data

    def set_onboarding(self, user_id, data):
        user = self.get_user(user_id)['data']
        query = {'_id': ObjectId(user.get('_id'))}
        if user:
            dept = data.get('dept')
            role = data.get('role')
            updated_data = {
                'dept': dept,
                'role': role,
                'onboading_flow_completed': True,
                'reports_to': data.get('reports_to')
            }
            res = self.db.update_document('users', query, updated_data)
            dept_doc = self.db.read_document(
                'dept', {'_id': ObjectId(dept.get('_id'))})
            if dept_doc:
                if role == "hod":
                    hod_list = self._get_hod_list(dept_doc, res)
                    self.db.update_document(
                        'dept', {'_id': ObjectId(dept.get('_id'))}, {'hod': hod_list})
                else:
                    faculty_list = self._get_faculty_list(dept_doc, res)
                    self.db.update_document('dept', {'_id': ObjectId(dept.get('_id'))}, {
                                            'faculties': faculty_list})

            if res:
                return {'status': HTTPStatus.OK, 'data': "Onboarding completed"}
            else:
                return {'status': HTTPStatus.INTERNAL_SERVER_ERROR, 'data': 'Error failed to update'}

    def get_onboarding(self):
        depts = self.db.read_documents('dept')
        for dept in depts:
            dept_hods = dept.get('hod')
            hods = []
            if dept_hods:
                for hod in dept_hods:
                    _id = ObjectId(hod.get('_id'))
                    hod = self.db.read_document('users', {'_id': _id})
                    hods.append({'display_name': hod.get(
                        'display_name'), '_id': hod.get('_id')})
                dept['hod'] = hods
        return {'status': HTTPStatus.OK, 'data': depts}

    def create_task(self, data):
        data['due_date'] = datetime.datetime.strptime(data['due_date'], date_format)
        data['created_at'] = datetime.datetime.strptime(data['created_at'], date_format)
        res = self.db.create_document('tasks', data)
        return res

    def get_task_item(self, id):
        res = self.db.read_document('tasks', {'_id': ObjectId(id)})
        return res

    def update_task_status(self, task_id, status, completed_by):
        if status == "completed":
            updated_data = {
                'status': status,
                'completed_on': datetime.datetime.now(),
                'completed_by': self.get_user(completed_by, status="completed").get('data')
            }
            res = self.db.update_document(
                'tasks', {'_id': ObjectId(task_id)}, updated_data)
        else:
            res = self.db.update_document(
                'tasks', {'_id': ObjectId(task_id)}, {'status': status, 'completed_on': None,
                                                      'completed_by': None})
        return res

    def update_task_data(self, task_id, new_data):
        res = self.db.update_document(
            'tasks', {'_id': ObjectId(task_id)}, new_data)
        return res

    def get_tasks(self, is_admin, user_id, dept_id):
        projection = {'completed_on': 0}
        res = self.db.read_documents(
            'tasks', {'dept._id': dept_id} if is_admin else {'assigned_to._id': user_id}, projection)
        return res

    def get_analytics_data(self, user_id):
        analytics_data = {
            'overall': {},
            'monthly': {}
        }
        user_filter = {"assigned_to._id": user_id}

        analytics_data['overall']['completed_count'] = self.db.count_documents(
            'tasks', {"$and": [user_filter, {"status": "completed"}]})
        analytics_data['overall']['inprogress_count'] = self.db.count_documents(
            'tasks', {"$and": [user_filter, {"status": "in_progress"}]})
        analytics_data['overall']['assigned'] = self.db.count_documents(
            'tasks', {"$and": [user_filter, {"status": "assigned"}]})

        analytics_data['monthly'] = []
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year

        for i in range(5):
            month = current_month - i
            year = current_year
            if month < 1:
                month = 12 + month
                year -= 1

            start_of_month = datetime.datetime(year, month, 1)
            end_of_month = datetime.datetime(year, month + 1, 1)

            monthly_data = {
                'month': start_of_month.strftime("%B"),
                'completed_count': self.db.count_documents('tasks', {
                    "$and": [
                        user_filter,
                        {"status": "completed"},
                        {"completed_on": {"$gte": start_of_month, "$lt": end_of_month}}
                    ]
                })
            }
            analytics_data['monthly'].append(monthly_data)

        return analytics_data

    def get_today_tasks(self, user_id):
        user_filter = {"assigned_to._id": user_id}
        return self.db.read_documents('tasks', {"$and": [user_filter, {"created_at": {"$gte": datetime.datetime.now()-datetime.timedelta(days=1)}}]})

    def delete_task(self, task_id):
        res = self.db.delete_document('tasks', {'_id': ObjectId(task_id)})
        return res

    # ------- Utils Functions -------
    def _get_hod_list(self, dept_doc, res):
        hod_list = dept_doc.get('hod')
        hod = {'_id': res.get('_id'),
               'display_name': res.get('display_name')}
        if hod not in hod_list:
            hod_list.append(hod)
        return hod_list

    def _get_faculty_list(self, dept_doc, res):
        faculty_list = dept_doc.get('faculties')
        faculty = {
            '_id': res.get('_id'),
            'display_name': res.get('display_name')
        }
        if faculty not in faculty_list:
            faculty_list.append(faculty)
        return faculty_list
