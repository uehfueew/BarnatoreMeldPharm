from .db import mongo
from bson import ObjectId

class Banner:
    @staticmethod
    def get_all():
        return list(mongo.db.banners.find().sort('_id', -1))

    @staticmethod
    def get_active():
        return list(mongo.db.banners.find({"is_active": True}).sort('_id', -1))

    @staticmethod
    def get_by_id(banner_id):
        try:
            return mongo.db.banners.find_one({"_id": ObjectId(banner_id)})
        except:
            return None

    @staticmethod
    def create(data):
        return mongo.db.banners.insert_one(data)

    @staticmethod
    def update(banner_id, data):
        return mongo.db.banners.update_one(
            {"_id": ObjectId(banner_id)},
            {"$set": data}
        )

    @staticmethod
    def delete(banner_id):
        return mongo.db.banners.delete_one({"_id": ObjectId(banner_id)})
