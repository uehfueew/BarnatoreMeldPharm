from pymongo import MongoClient
import sys

try:
    uri = "mongodb://localhost:27017/meldpharm?tls=false"
    client = MongoClient(uri, serverSelectionTimeoutMS=2000)
    print(f"Connecting to {uri}...")
    db = client.get_database()
    count = db.products.count_documents({})
    print(f"Connection successful! Found {count} products in 'meldpharm.products'.")
    
    # Check smart_grocery too
    uri2 = "mongodb://localhost:27017/smart_grocery"
    client2 = MongoClient(uri2, serverSelectionTimeoutMS=2000)
    db2 = client2.get_database()
    count2 = db2.products.count_documents({})
    print(f"Found {count2} products in 'smart_grocery.products'.")

except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
