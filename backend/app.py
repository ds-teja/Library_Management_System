from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from model import db
from celery_config import celery
import os 
import redis

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. Enable CORS
CORS(app, origins="http://localhost:8080", supports_credentials=True)

# 3. Enable Cache
redis_client = redis.Redis(host='localhost', port=6379, db=0)
cache = Cache(app,config={'CACHE_TYPE': 'redis', 'CACHE_REDIS': redis_client})

# 4. Add Configurations and Celery
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'library'
celery.conf.update(app.config)

BASE_UPLOAD_FOLDER = 'file_uploads'
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)
    
COVER_UPLOAD_FOLDER = 'cover_uploads'
if not os.path.exists(COVER_UPLOAD_FOLDER):
    os.makedirs(COVER_UPLOAD_FOLDER)

CSV_FOLDER = 'csv_reports'
if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)
    
# 4. Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# 5. Register routes
def register_routes():
    from routes import register
    register(app)

if __name__ == '__main__':
    register_routes()
    app.run(debug=True)
