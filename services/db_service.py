from bson import ObjectId
from .mongo_db import MongoDB
from http import HTTPStatus


class DBService:

    def __init__(self, env):
        print("connected to: ", env)
        self.db = MongoDB('taskmanager', env=env)

    def login_user(self, username, password):
        return self.db.read_document('users', {'username': username, 'password': password})

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

    def get_user(self, user_id):
        data = self.db.read_document('users', {'_id': ObjectId(user_id)})
        return {'status': HTTPStatus.OK, 'data': data}

    def set_onboading(self, user_id, data):
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
            for hod in dept_hods:
                _id = ObjectId(hod.get('_id'))
                hod = self.db.read_document('users', {'_id': _id})
                hods.append({'display_name': hod.get(
                    'display_name'), '_id': hod.get('_id')})
            dept['hod'] = hods
        return {'status': HTTPStatus.OK, 'data': depts}

    def create_task(self, data):
        res = self.db.create_document('tasks', data)
        return res

    def update_task_status(self, task_id, status):
        res = self.db.update_document(
            'tasks', {'_id': ObjectId(task_id)}, {'status': status})
        return res

    def update_task_data(self, task_id, new_data):
        res = self.db.update_document(
            'tasks', {'_id': ObjectId(task_id)}, new_data)
        return res

    def get_tasks(self, is_admin, user_id):
        res = self.db.read_documents(
            'tasks', {'created_by': user_id} if is_admin else {'assigned_to': user_id})
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
