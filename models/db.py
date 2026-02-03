from flask_pymongo import PyMongo
import certifi
import ssl

mongo = PyMongo()

def init_db(app):
    app.config["MONGO_TLSCAFILE"] = certifi.where()
    # Explicitly set tls=True and tlsAllowInvalidCertificates=True only if you are stuck in dev env with bad certs, 
    # but normally certifi.where() is enough. 
    # However, sometimes on macOS python environments, SSL context needs to be passed explicitly or allowed invalid.
    # For now, let's stick to certifi. But ensure URI has params.
    mongo.init_app(app, tlsCAFile=certifi.where())
