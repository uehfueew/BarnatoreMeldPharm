import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.db import mongo

def seed_products():
    products = [
        {
            "name": "Serum me Vitaminë C",
            "price": 29.99,
            "discount_price": 24.99,
            "description": "Serum shkëlqyes për lëkurë rrezatuese. I pasur me antioksidantë. Ndihmon në zvogëlimin e njollave të errëta dhe përmirëson teksturën e lëkurës.",
            "image_url": "https://placehold.co/400x400/2c7a7b/ffffff?text=Serum+Vitamina+C",
            "category": "skincare",
            "featured": True
        },
        {
            "name": "Kompleks Multivitaminash",
            "price": 19.99,
            "discount_price": None,
            "description": "Vitamina thelbësore ditore për shëndet të përgjithshëm. Përmban Vitaminë A, C, D, E dhe Zink.",
            "image_url": "https://placehold.co/400x400/319795/ffffff?text=Multivitamina",
            "category": "vitamins",
            "featured": True
        },
        {
            "name": "Hidratues Fytyre",
            "price": 35.00,
            "discount_price": None,
            "description": "Hidratim i thellë për lëkurë të thatë. Formulë jo e yndyrshme që ruan lagështinë për 24 orë.",
            "image_url": "https://placehold.co/400x400/2c7a7b/ffffff?text=Hidratues",
            "category": "skincare",
            "featured": False
        },
        {
            "name": "Vaj Peshku Omega-3",
            "price": 25.50,
            "discount_price": 20.00,
            "description": "Mbështet shëndetin e zemrës dhe trurit. I marrë nga peshqit e egër.",
            "image_url": "https://placehold.co/400x400/319795/ffffff?text=Omega-3",
            "category": "vitamins",
            "featured": True
        },
         {
            "name": "Krem Nate me Retinol",
            "price": 45.00,
            "discount_price": 39.99,
            "description": "Zvogëlon linjat e holla dhe rrudhat ndërsa flini. Zgjohuni me lëkurë të rinuar.",
            "image_url": "https://placehold.co/400x400/2c7a7b/ffffff?text=Krem+Retinol",
            "category": "skincare",
            "featured": False
        }
    ]

    with app.app_context():
        # Clear existing products
        try:
            mongo.db.products.delete_many({})
            print("Cleared existing products.")
        except Exception as e:
            print("Error clearing products:", e)
            
        # Insert new ones
        try:
            result = mongo.db.products.insert_many(products)
            print(f"Seeded {len(result.inserted_ids)} products successfully!")
        except Exception as e:
             print("Error inserting products:", e)

def seed_admin():
    from flask_bcrypt import Bcrypt
    users = mongo.db.users
    bcrypt = Bcrypt(app)
    
    admin_email = "admin@meldpharm.com"
    existing_user = users.find_one({"email": admin_email})
    
    if not existing_user:
        hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        users.insert_one({
            "username": "Admin",
            "email": admin_email,
            "password": hashed_password,
            "is_admin": True
        })
        print(f"Admin created: {admin_email} / admin123")
    else:
        users.update_one({"email": admin_email}, {"$set": {"is_admin": True}})
        print(f"User {admin_email} promoted to admin.")

if __name__ == "__main__":
    with app.app_context():
        # seed_products() # Uncomment if you want to reset products
        seed_admin()
