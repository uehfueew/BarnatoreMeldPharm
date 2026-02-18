from app import app
from models.db import mongo

def update_subcategories():
    with app.app_context():
        # Mapping rules (keywords -> Subcategory)
        rules = [
            (['cleanser', 'pastrues', 'gel', 'foam', 'xhel', 'tonik'], 'Pastrues & Tonikë'),
            (['moisturis', 'hidratues', 'lotion', 'lëng', 'gel-cream'], 'Hidratues'),
            (['serum'], 'Serume & Trajtime'),
            (['spf', 'dielli', 'sun', 'photo'], 'Kremra Dielli (SPF)'),
            (['akne', 'blemish', 'acne', 'dermopure'], 'Kundër Akneve'),
            (['eye', 'syve'], 'Kujdesi i Syve'),
            (['foot', 'këmbët', 'feet'], 'Duart & Këmbët'),
            # Cream is a very general keyword, only use if others don't match or for specific ones
            (['cream', 'krem'], 'Hidratues'),
            (['repair', 'cicaplast', 'baume', 'active repair'], 'Riparsus & Balma'),
            (['anti-pigment', 'pigmentim'], 'Pigmentim & Njolla'),
            (['anti-aging', 'rrudhat', 'q10'], 'Anti-aging & Rrudhat'),
            (['sensitive', 'sensitve', 'ph5'], 'Lëkurë Sensitive')
        ]
        
        updated = 0
        
        # First, ensure products in "Dermokozmetikë" are considered
        # Then apply rules
        for keywords, sub in rules:
            for kw in keywords:
                res = mongo.db.products.update_many({
                    'name': {'$regex': kw, '$options': 'i'},
                    'category': 'Dermokozmetikë'
                }, {'$set': {'subcategory': sub}})
                updated += res.modified_count
        
        # Special case for "Kujdes Personal & Higjienë"
        personal_rules = [
            (['shampoo', 'shampo', 'flokësh', 'hair'], 'Shampo & Kujdes flokësh'),
            (['sapun', 'sapuni', 'dushi', 'shower'], 'Sapunë & Xhele dushi'),
            (['loshion trupi', 'lotion trupi', 'losion për trup', 'krem trupi'], 'Lotion & Kremra trupi'),
            (['oral', 'furça', 'pasta', 'dhëmbëve'], 'Kujdes Oral'),
            (['intime', 'intimate'], 'Higjienë Intime'),
            (['dezinfektues', 'sanitizer'], 'Dezinfektues & Mbrojtje'),
            (['deodorant', 'antiperspirant'], 'Deodorantë & Antiperspirantë')
        ]
        
        for keywords, sub in personal_rules:
            for kw in keywords:
                res = mongo.db.products.update_many({
                    'name': {'$regex': kw, '$options': 'i'},
                    'category': 'Kujdes Personal & Higjienë'
                }, {'$set': {'subcategory': sub}})
                updated += res.modified_count

        print(f"Successfully updated/populating {updated} product subcategories.")

if __name__ == "__main__":
    update_subcategories()
