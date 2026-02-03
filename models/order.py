from .db import mongo
from datetime import datetime
from bson import ObjectId

class Order:
    @staticmethod
    def create(order_data):
        order = {
            "fullname": order_data.get('fullname'),
            "email": order_data.get('email'),
            "address": order_data.get('address'),
            "city": order_data.get('city'),
            "phone": order_data.get('phone'),
            "payment_method": order_data.get('payment_method'),
            "items": order_data.get('items'),
            "total_price": order_data.get('total_price'),
            "shipping_cost": order_data.get('shipping_cost'),
            "grand_total": order_data.get('grand_total'),
            "user_id": order_data.get('user_id'), # Optional, if logged in
            "status": "Delivering",
            "created_at": datetime.utcnow()
        }
        
        result = mongo.db.orders.insert_one(order)
        return str(result.inserted_id)

    @staticmethod
    def update_status(order_id, status):
        mongo.db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status}}
        )

    @staticmethod
    def get_by_user(user_id):
        return list(mongo.db.orders.find({"user_id": user_id}).sort("created_at", -1))
    
    @staticmethod
    def get_all():
        return list(mongo.db.orders.find().sort("created_at", -1))
