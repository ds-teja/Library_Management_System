from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import Book,db,Section,Request, User, UserPreferences
from datetime import datetime
from sqlalchemy import or_
from app import app,cache

bp = Blueprint('preferences', __name__)

'''
    API's in this file
    1) get_book_review      -> roles:[librarian,user] -> route('/api/reviews', methods=['GET'])
    2) add_book_review      -> roles:[user]           -> route('/api/reviews', methods=['POST'])
    3) add_book_ratings     -> roles:[user]           -> route('/api/rating', methods=['POST'])
    4) add_book_favourites  -> roles:[user]           -> route('/api/favourite', methods=['POST'])
'''

@bp.route('/api/reviews', methods=['GET'])
@jwt_required()
def get_book_reviews():
    identity = get_jwt_identity()
    if identity['role']!='user' and identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    book_id = request.args.get('book_id', None)    
    cache_key = f"get_book_reviews_{book_id}"
    
    if not Book.query.get(book_id):
        return {'message':'Book does not exist!'}, 404

    reviews = db.session.query(
        User.id,
        User.username,
        UserPreferences.rating,
        UserPreferences.review
    ).join(UserPreferences, UserPreferences.user_id==User.id
    ).filter(UserPreferences.book_id==book_id,or_(UserPreferences.rating != '', UserPreferences.review != '')  
    ).all()

    reviews_info = [{
        'user_id': userid,
        'username':name,
        'rating':rating,
        'review':review
    } for userid, name, rating, review in reviews]

    return jsonify(reviews_info)

@bp.route('/api/reviews', methods=['POST'])
@jwt_required()
def add_book_review():
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    user_id = identity['id']
    data = request.get_json()
    book_id = data['book_id']
    review = data['review']
    
    existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
    if not existing_record:
        new_record = UserPreferences(user_id=user_id,book_id=book_id)
        db.session.add(new_record)
        db.session.commit()
        existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()
    
    existing_record.review = review
    db.session.commit()
    
    return {'message': 'Review added successfully'}, 200
        
    
@bp.route('/api/rating', methods=['POST'])
@jwt_required()
def add_book_ratings():
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    data = request.get_json()
    user_id = identity['id']
    book_id = data['id']
    selectedRating = data['selectedRating']
    selectedShelf = data['selectedShelf']
    
    existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
    if not existing_record:
        new_record = UserPreferences(user_id=user_id,book_id=book_id)
        db.session.add(new_record)
        db.session.commit()
        existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
        
    existing_record.rating = selectedRating
    if(selectedShelf=='Completed List'):
        existing_record.completed_date = datetime.now()
    else:
        existing_record.completed_date = None
    
    existing_record.shelf = selectedShelf
    db.session.commit()
    
    return {'message': 'Preferences added successfully'}, 200

@bp.route('/api/favourite', methods=['POST'])
@jwt_required()
def add_book_favourites():
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    data = request.get_json()
    user_id = identity['id']
    book_id = data['id']
    isFavourite = data['isFavourite']
    
    existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
    if not existing_record:
        new_record = UserPreferences(user_id=user_id,book_id=book_id)
        db.session.add(new_record)
        db.session.commit()
        existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
        
    existing_record.favourites = isFavourite
    db.session.commit()
    
    return {'message': 'Preferences added successfully'}, 200

    