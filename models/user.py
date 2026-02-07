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
        # Add profile fields
        self.fullname = user_data.get('fullname', '')
        self.address = user_data.get('address', '')
        self.city = user_data.get('city', '')
        self.country = user_data.get('country', '')
        self.phone = user_data.get('phone', '')

    @staticmethod
    def create(username, email, password_hash, is_admin=False):
        user_id = mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": password_hash,
            "is_admin": is_admin,
            "fullname": "",
            "address": "",
            "city": "",
            "country": "",
            "phone": ""
        }).inserted_id
        return User.get_by_id(user_id)

    @staticmethod
    def update_profile(user_id, profile_data):
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "fullname": profile_data.get('fullname', ''),
                "address": profile_data.get('address', ''),
                "city": profile_data.get('city', ''),
                "country": profile_data.get('country', ''),
                "phone": profile_data.get('phone', '')
            }}
        )

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
