from .db import mongo
from bson import ObjectId

class Product:
    @staticmethod
    def get_all():
        # Clean _id for json serialization if needed, or just return cursor list
        return list(mongo.db.products.find())

    @staticmethod
    def get_by_category(category):
        return list(mongo.db.products.find({"category": category}))

    @staticmethod
    def get_by_id(product_id):
        try:
            return mongo.db.products.find_one({"_id": ObjectId(product_id)})
        except:
            return None
    
    @staticmethod
    def get_featured():
        # Changed to return discounted products as per request
        return list(mongo.db.products.find({
            "discount_price": {"$ne": None, "$gt": 0}
        }))

    @staticmethod
    def get_related(category, exclude_id, limit=3):
        try:
            return list(mongo.db.products.find({
                "category": category,
                "_id": {"$ne": ObjectId(exclude_id)}
            }).limit(limit))
        except:
            return []

    @staticmethod
    def create(data):
        return mongo.db.products.insert_one(data)

    @staticmethod
    def update(product_id, data):
        return mongo.db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": data}
        )

    @staticmethod
    def delete(product_id):
        return mongo.db.products.delete_one({"_id": ObjectId(product_id)})
