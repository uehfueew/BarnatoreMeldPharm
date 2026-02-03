from flask_login import UserMixin
from .db import mongo
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.is_admin = user_data.get('is_admin', False)

    @staticmethod
    def create(username, email, password_hash, is_admin=False):
        user_id = mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": password_hash,
            "is_admin": is_admin
        }).inserted_id
        return User.get_by_id(user_id)

    @staticmethod
    def get_by_id(user_id):
        if not user_id:
            return None
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            return None
        return None

    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def update_cart(user_id, cart):
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"cart": cart}}
        )

    @staticmethod
    def get_cart(user_id):
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"cart": 1})
            return user_data.get('cart', {}) if user_data else {}
        except:
            return {}
