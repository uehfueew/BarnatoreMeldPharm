from .db import mongo
from bson import ObjectId
from datetime import datetime

class Product:

    @staticmethod

    def get_all():

        # Clean _id for json serialization if needed, or just return cursor list

        return list(mongo.db.products.find())



    @staticmethod
    def get_paginated(page=1, per_page=20, category=None, search_query=None, subcategory=None, sort=None, brand=None, min_price=None, max_price=None, discount_only=False, best_seller_only=False, no_discount=False):
        query = {}
        if category and category != 'all':
            query["category"] = category
        
        if subcategory and subcategory != 'all':
            query["subcategory"] = subcategory

        if brand and brand != 'all':
            query["brand"] = brand

        if discount_only:
            query["discount_price"] = {"$ne": None, "$gt": 0}
        elif no_discount:
            query["$or"] = [
                {"discount_price": {"$exists": False}},
                {"discount_price": None},
                {"discount_price": 0}
            ]

        if best_seller_only:
            query["is_best_seller"] = True

        if min_price is not None or max_price is not None:
            # Match against effective_price instead of just price
            if "effective_price" not in query:
                # We need to use $expr to access the calculated effective_price in $match
                # or simpler: match against both price and discount_price since we can't match against addFields in $match stage of aggregate directly if we want to use the same logic
                pass

        if search_query:
            search_filter = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"brand": {"$regex": search_query, "$options": "i"}},
                    {"category": {"$regex": search_query, "$options": "i"}},
                    {"subcategory": {"$regex": search_query, "$options": "i"}}
                ]
            }
            if "$or" in query:
                # If we already have an $or (from no_discount), we must use $and to combine them
                if "$and" not in query: query["$and"] = []
                # Move existing $or to $and if it's there
                existing_or = query.pop("$or")
                query["$and"].append({"$or": existing_or})
                query["$and"].append(search_filter)
            else:
                query.update(search_filter)
            
        # Determine sort order
        # Default sort
        sort_dict = {"_id": -1}
        if sort == 'price-low':
            sort_dict = {"effective_price": 1}
        elif sort == 'price-high':
            sort_dict = {"effective_price": -1}
        elif sort == 'newest':
            sort_dict = {"_id": -1}
        elif sort == 'discount':
            sort_dict = {"discount_percent": -1}
        elif sort == 'relevance':
            sort_dict = {"is_best_seller": -1, "_id": -1}

        # Use aggregation to handle dynamic sorting by effective price (discount_price if exists, else price)
        pipeline = [
            {
                "$addFields": {
                    "effective_price": {
                        "$cond": [
                            {"$and": [
                                {"$gt": ["$discount_price", 0]},
                                {"$ne": ["$discount_price", None]}
                            ]},
                            "$discount_price",
                            "$price"
                        ]
                    },
                    "discount_percent": {
                        "$cond": [
                            {"$and": [
                                {"$gt": ["$discount_price", 0]},
                                {"$ne": ["$discount_price", None]}
                            ]},
                            {"$divide": [{"$subtract": ["$price", "$discount_price"]}, "$price"]},
                            0
                        ]
                    }
                }
            }
        ]

        # Apply basic filters first
        match_query = query.copy()
        # Remove price filter from match_query as we'll apply it after addFields
        match_query.pop("price", None)
        
        # Insert initial match
        pipeline.insert(0, {"$match": match_query})

        # Apply price filter on effective_price
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        
        if price_filter:
            pipeline.append({"$match": {"effective_price": price_filter}})

        # Get total count after price filtering
        count_pipeline = pipeline[:]
        count_pipeline.append({"$count": "total"})
        count_result = list(mongo.db.products.aggregate(count_pipeline))
        total_products = count_result[0]['total'] if count_result else 0

        # Add remaining stages
        pipeline.extend([
            {"$sort": sort_dict},
            {"$skip": (page - 1) * per_page if page > 0 else 0},
            {"$limit": per_page}
        ])
        
        products = list(mongo.db.products.aggregate(pipeline))
        for p in products:
            p["_id"] = str(p["_id"])
        
        import math
        total_pages = math.ceil(total_products / per_page)
        
        return products, total_pages, total_products



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

    def get_featured(limit=15):

        # Changed to return discounted products as per request

        return list(mongo.db.products.find({

            "discount_price": {"$ne": None, "$gt": 0}

        }).limit(limit))

    @staticmethod
    def get_best_sellers(limit=15):
        return list(mongo.db.products.find({"is_best_seller": True}).limit(limit))

    @staticmethod
    def get_regular(limit=20):
        # Returns products WITHOUT a discount_price
        # Align with get_paginated default sort (_id: -1)
        return list(mongo.db.products.find({
            "$or": [
                {"discount_price": {"$exists": False}},
                {"discount_price": None},
                {"discount_price": 0}
            ]
        }).sort([('_id', -1)]).limit(limit))

    @staticmethod
    def get_regular_count():
        return mongo.db.products.count_documents({
            "$or": [
                {"discount_price": {"$exists": False}},
                {"discount_price": None},
                {"discount_price": 0}
            ]
        })

    @staticmethod

    def get_related(category, exclude_id, limit=4):

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

    @staticmethod
    def delete(product_id):
        return mongo.db.products.delete_one({"_id": ObjectId(product_id)})

    @staticmethod
    def revert_expired_offers():
        now = datetime.now()
        # Find products where discount_until is in the past
        expired = mongo.db.products.find({
            "discount_until": {"$lt": now},
            "discount_price": {"$ne": None}
        })
        
        count = 0
        for product in expired:
            mongo.db.products.update_one(
                {"_id": product["_id"]},
                {"$set": {
                    "discount_price": None,
                    "discount_until": None
                }}
            )
            count += 1
        return count

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
