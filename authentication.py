from db_manager import DBManager
import datetime
import secrets


class Authentication(object):

    def __init__(self):
        self.mongo = DBManager()
        pass

    def token_creation(self, user_id):
        now = datetime.datetime.now()
        return self.mongo.set_token(user_id, secrets.token_urlsafe(), now)

    def token_check(self, token):
        user_token = self.mongo.find_token(token)
        if user_token is None:
            return False
        else:
            expired = user_token["time"] + datetime.timedelta(hours=2)
            now = datetime.datetime.now()
            if now > expired:
                return False
        return True

    def token_recreation(self, user_id):
        now = datetime.datetime.now()
        return self.mongo.recreate_token(user_id, secrets.token_urlsafe(), now)

    def token_update(self, token):
        now = datetime.datetime.now()
        return self.mongo.update_token(token, now)

    def token_get(self, user_id):
        getter = self.mongo.get_token(user_id)
        if getter is None:
            return False
        else:
            return getter['token']

    def token_expired(self, user_id):
        expired_time = datetime.datetime.now() - datetime.timedelta(days=2)
        return self.mongo.expired_token(user_id, expired_time)

    def __del__(self):
        pass
