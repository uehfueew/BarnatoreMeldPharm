
import os
path = 'models/product.py'
with open(path, 'rb') as f:
    content = f.read()

content_str = content.replace(b'\x00', b'').decode('utf-8', errors='ignore')

# Helper: Find last occurrence of 'def delete(product_id):' to strip anything after
marker = 'def delete(product_id):'
if marker in content_str:
    start_index = content_str.rfind(marker)
    # preserve up to marker + marker length
    base_content = content_str[:start_index + len(marker)]
    
    # Reconstruct the end
    clean_content = base_content + '\n        return mongo.db.products.delete_one({"_id": ObjectId(product_id)})\n\n    @staticmethod\n    def get_favorites_by_user(user_id):\n        products = list(mongo.db.products.find({"favorites": user_id}))\n        for p in products:\n            p["_id"] = str(p["_id"])\n        return products\n\n    @staticmethod\n    def get_by_ids(id_list):\n        if not id_list:\n            return []\n        try:\n            from bson import ObjectId\n            obj_ids = [ObjectId(pid) for pid in id_list]\n            products = list(mongo.db.products.find({"_id": {"$in": obj_ids}}))\n            for p in products:\n                p["_id"] = str(p["_id"])\n            return products\n        except Exception as e:\n            print(f"Error in get_by_ids: {e}")\n            return []\n'
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    print('Fixed models/product.py')
else:
    print('Marker not found')
