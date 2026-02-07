import os
import sys
# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models.db import mongo, init_db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Ensure we get the MONGO_URI from env
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/meldpharm')
init_db(app)

with app.app_context():
    # 1. Rename "Dermokozmetikë & Bukuri" -> "Dermokozmetikë"
    print("Renaming 'Dermokozmetikë & Bukuri' to 'Dermokozmetikë'...")
    result1 = mongo.db.products.update_many(
        {"category": "Dermokozmetikë & Bukuri"},
        {"$set": {"category": "Dermokozmetikë"}}
    )
    print(f"Updated {result1.modified_count} products.")
    
    # Optional: Verify
    count = mongo.db.products.count_documents({"category": "Dermokozmetikë"})
    print(f"Total products in 'Dermokozmetikë': {count}")

    print("Done.")
