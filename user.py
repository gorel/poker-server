import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Constants
SELECT_QUERY = "SELECT * FROM users WHERE username=?"
INDEX_COLUMN    = 0
USERNAME_COLUMN = 1
PASSWORD_COLUMN = 2

class UserNotFoundError(Exception):
    pass

class User:
    def __init__(self, username):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        data = (username, )
        c.execute(SELECT_QUERY, data)
        user = c.fetchone()
        conn.close()

        if user is None:
            raise UserNotFoundError

        self.user_id = user[INDEX_COLUMN]
        self.username = user[USERNAME_COLUMN]
        self.pw_hash = user[PASSWORD_COLUMN]

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return not self.is_authenticated()

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def get_user_id(self):
        return self.user_id

    def get_username(self):
        return self.username

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    @classmethod
    def get(self_class, id):
        try:
            return self_class(id)
        except UserNotFoundError:
            return None

    @classmethod
    def get_pw_hash(self_class, password):
        return generate_password_hash(password)
