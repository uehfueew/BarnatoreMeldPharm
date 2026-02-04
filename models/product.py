from .db import mongo
from bson import ObjectId

class Product:
    @staticmethod
    def get_all():
        # Clean _id for json serialization if needed, or just return cursor list
        return list(mongo.db.products.find())

    @staticmethod
    def get_paginated(page=1, per_page=20):
        total_products = mongo.db.products.count_documents({})
        
        # Calculate safe skip
        if page < 1: page = 1
        skip = (page - 1) * per_page
        
        products = list(mongo.db.products.find().skip(skip).limit(per_page))
        
        import math
        total_pages = math.ceil(total_products / per_page)
        
        return products, total_pages

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
    def toggle_favorite(product_id, user_id):
        try:
            pid = ObjectId(product_id)
            product = mongo.db.products.find_one({"_id": pid})
            if not product:
                return None
            
            favorites = product.get('favorites', [])
            action = 'added'
            
            if user_id in favorites:
                mongo.db.products.update_one(
                    {"_id": pid}, 
                    {"$pull": {"favorites": user_id}}
                )
                action = 'removed'
            else:
                mongo.db.products.update_one(
                    {"_id": pid}, 
                    {"$addToSet": {"favorites": user_id}}
                )
                
            return action
        except:
            return None

    @staticmethod
    def delete(product_id):
        return mongo.db.products.delete_one({"_id": ObjectId(product_id)})

    @staticmethod
    def get_favorites_by_user(user_id):
        products = list(mongo.db.products.find({"favorites": user_id}))
        for p in products:
            p["_id"] = str(p["_id"])
        return products

    @staticmethod
    def get_by_ids(id_list):
        if not id_list:
            return []
        try:
            from bson import ObjectId
            obj_ids = [ObjectId(pid) for pid in id_list]
            products = list(mongo.db.products.find({"_id": {"$in": obj_ids}}))
            for p in products:
                p["_id"] = str(p["_id"])
            return products
        except Exception as e:
            print(f"Error in get_by_ids: {e}")
            return []
