from flask_jwt_extended import decode_token
import datetime


class Utils:
    def verify_token(self, token):
        
        decoded_token = decode_token(token)
        exp_time = datetime.datetime.fromtimestamp(decoded_token['exp']) 
        current_time = datetime.datetime.now()  
        if current_time > exp_time:
            return False
        else: 
            return True