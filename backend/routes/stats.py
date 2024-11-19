from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token
from flask_cors import cross_origin
from model import db,User, Book, Section, Request,UserPreferences
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import timedelta, datetime
from sqlalchemy import func, case
from app import app,cache

bp = Blueprint('stats', __name__)

'''
    API's in this file
    1) get_user_details       -> roles:[librarian,user]   -> cached with key route('/user/stats/details',methods=['GET'])
    2) get_user_summary       -> roles:[librarian,user]   -> cached with key route('/user/stats/summary',methods=['GET'])
    3) user_interest_sections -> roles:[librarian,user]   -> cached with key route('/user/stats/sections',methods=['GET'])
    4) get_total_summary      -> roles:[librarian]        -> cached route('/librarian/stats/summary',methods=['GET'])
    5) get_monthly_new_users  -> roles:[librarian]        -> cached route('/librarian/stats/new',methods=['GET'])
    6) get_popular_sections   -> roles:[librarian]        -> cached route('/librarian/stats/sections',methods=['GET'])
    7) get_popular_ebooks     -> roles:[librarian]        -> cached route('/librarian/stats/ebooks',methods=['GET'])  
'''

@bp.route('/user/stats/details',methods=['GET'])
@jwt_required()
def get_user_details():
    '''
        This api is accessed by both librarian and users. It returns the basic user details.
        If the librarian is accessing it, it expects the user_id argument.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user' and identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    if identity['role']=='user':
        user_id = identity['id']
    elif identity['role']=='librarian':
        user_id = request.args.get('user_id',None)
    
    cache_key = f"get_user_details_{identity['role']}_{user_id or 'none'}"
    
    with app.app_context():
        @cache.cached(timeout=10,key_prefix=cache_key)
        def cached_get_user_details():
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {'message':"User not found"}, 404
            
            result = {
                'name':user.username,
                'email':user.email,
                'nationality':user.nationality,
                'created_date':user.created_date,
                'about_me':user.about_me
            }
            
            return jsonify(result)
        return cached_get_user_details()
    
@bp.route('/user/stats/summary',methods=['GET'])
@jwt_required()
def get_user_summary():
    '''
        This api is accessed by both librarian and users. 
        It returns the summary of requests and bookshelves of the user.
        If the librarian is accessing it, it expects the user_id argument.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user' and identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    if identity['role']=='user':
        user_id = identity['id']
    elif identity['role']=='librarian':
        user_id = request.args.get('user_id',None)
    
    cache_key = f"get_user_summary_{identity['role']}_{user_id or 'none'}"
    
    with app.app_context():
        @cache.cached(timeout=10,key_prefix=cache_key)
        def cached_get_user_summary():
            total_requests = Request.query.filter_by(req_user_id=user_id).count()
            pending = Request.query.filter_by(req_user_id=user_id,req_status='Pending').count()
            withdrawn = Request.query.filter_by(req_user_id=user_id,req_status='Withdrawn').count()
            declined = Request.query.filter_by(req_user_id=user_id,req_status='Declined').count()
            approved = Request.query.filter_by(req_user_id=user_id,req_status='Approved').count()
            returned = Request.query.filter_by(req_user_id=user_id,req_status='Returned').count()
            revoked = Request.query.filter_by(req_user_id=user_id,req_status='Revoked').count()
            
            to_read = UserPreferences.query.filter_by(user_id=user_id,shelf='To Read List').count()
            reading = UserPreferences.query.filter_by(user_id=user_id,shelf='Currently Reading').count()
            completed = UserPreferences.query.filter_by(user_id=user_id,shelf='Completed List').count()
            result = {
                'total_requests': total_requests,
                'pending': pending,
                'withdrawn': withdrawn,
                'declined': declined,
                'approved': approved,
                'returned': returned,
                'revoked': revoked,
                'to_read': to_read,
                'reading': reading,
                'completed': completed
            }
            return jsonify(result)
        return cached_get_user_summary()

@bp.route('/user/stats/sections',methods=['GET'])
@jwt_required()
def user_interest_sections():
    '''
        This api is accessed by both librarian and users. 
        It returns the top 5 interested sections of the user.
        If the librarian is accessing it, it expects the user_id argument.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user' and identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    if identity['role']=='user':
        user_id = identity['id']
    elif identity['role']=='librarian':
        user_id = request.args.get('user_id')
    
    cache_key = f"user_interest_sections_{identity['role']}_{user_id or 'none'}"
        
    with app.app_context():
        @cache.cached(timeout=10,key_prefix=cache_key)
        def cached_user_interest_sections():
            # Query to get the top 5 popular sections based on the number of requests
            popular_sections = db.session.query(
                Section.id,
                Section.name,
                func.count(Request.id).label('request_count'),
                func.sum(case((Request.req_status == 'Pending', 1), else_=0)).label('pending'),
                func.sum(case((Request.req_status == 'Declined', 1), else_=0)).label('declined'),
                func.sum(case((Request.req_status == 'Withdrawn', 1), else_=0)).label('withdrawn'),
                func.sum(case((Request.req_status == 'Approved', 1), else_=0)).label('approved'),
                func.sum(case((Request.req_status == 'Returned', 1), else_=0)).label('returned'),
                func.sum(case((Request.req_status == 'Revoked', 1), else_=0)).label('revoked')
            ).join(Book, Book.section_id == Section.id
            ).join(Request, Request.req_book_id == Book.id
            ).filter(Request.req_user_id == user_id
            ).group_by(Section.id
            ).order_by(func.count(Request.id).desc()
            ).limit(5).all()
            
            result = [
            {
                'id': id,
                'section': section,
                'request_count': request_count,
                'pending': pending,
                'declined': declined,
                'withdrawn': withdrawn,
                'approved': approved,
                'returned': returned,
                'revoked': revoked
            }
            for id, section, request_count, pending, declined, withdrawn, approved, returned, revoked in popular_sections ]
            
            return jsonify(result)
        return cached_user_interest_sections()

@bp.route('/librarian/stats/summary',methods=['GET'])
@jwt_required()
def get_total_summary():
    '''
     This api is accessed by librarian to get the total summary of books, sections, users.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_total_summary():
            total_users = User.query.count()
            total_sections = Section.query.count()
            total_ebooks = Book.query.count()
            
            result = {
                'total_users': total_users,
                'total_sections': total_sections,
                'total_ebooks': total_ebooks
            }
            
            return jsonify(result)
        return cached_get_total_summary()
    
@bp.route('/librarian/stats/new',methods=['GET'])
@jwt_required()
def get_monthly_new_users():
    '''
        This api is accessed by librarian, to get the monthly new books, users, sections for past 6 months.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_montly_new_users():
            six_months_ago = datetime.now() - timedelta(days=6*30)  # Roughly 6 months
            
            users = db.session.query(
                func.strftime('%Y-%m', User.created_date).label('month'),
                func.count(User.id).label('new_users'),
            ).filter(User.created_date >= six_months_ago
            ).group_by(func.strftime('%Y-%m', User.created_date)
            ).order_by('month').all()
            
            sections = db.session.query(
                func.strftime('%Y-%m', Section.created_date).label('month'),
                func.count(Section.id).label('new_sections'),
            ).filter(Section.created_date >= six_months_ago
            ).group_by(func.strftime('%Y-%m', Section.created_date)
            ).order_by('month').all()

            books = db.session.query(
                func.strftime('%Y-%m', Book.upload_date).label('month'),
                func.count(Book.id).label('new_books'),
            ).filter(Book.upload_date >= six_months_ago
            ).group_by(func.strftime('%Y-%m', Book.upload_date)
            ).order_by('month').all()
            
            user_labels = [result.month for result in users]
            new_users = [result.new_users for result in users]
            
            section_labels = [result.month for result in sections]
            new_secitons = [result.new_sections for result in sections]
            
            book_labels = [result.month for result in books]
            new_books = [result.new_books for result in books]
            
            # Temp data
            # import random
            # current_date = datetime.now()
            # labels = [(current_date - timedelta(days=30*i)).strftime('%B') for i in range(6)]
            # labels.reverse()
            # new_users = [random.randint(50, 200) for _ in range(6)] 

            data = {
                'user_labels': user_labels,
                'section_labels': section_labels,
                'book_labels': book_labels,
                'new_users': new_users,
                'new_sections': new_secitons,
                'new_books': new_books
            }
            return jsonify(data)
        return cached_get_montly_new_users()

@bp.route('/librarian/stats/sections',methods=['GET'])
@jwt_required()
def get_popular_sections():
    '''
     This api is accessed by librarian, to get the popular sections based on the total requests received.
     It returns the total requests count, along with the counts of each request status.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_popular_sections():
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6 * 30)

            # Query to get the top 5 popular sections based on the number of requests
            popular_sections = db.session.query(
                Section.id,
                Section.name,
                func.count(Request.id).label('request_count'),
                func.sum(case((Request.req_status == 'Pending', 1), else_=0)).label('pending'),
                func.sum(case((Request.req_status == 'Declined', 1), else_=0)).label('declined'),
                func.sum(case((Request.req_status == 'Withdrawn', 1), else_=0)).label('withdrawn'),
                func.sum(case((Request.req_status == 'Approved', 1), else_=0)).label('approved'),
                func.sum(case((Request.req_status == 'Returned', 1), else_=0)).label('returned'),
                func.sum(case((Request.req_status == 'Revoked', 1), else_=0)).label('revoked')
            ).join(Book, Book.section_id == Section.id
            ).join(Request, Request.req_book_id == Book.id
            ).filter(Request.req_date.between(start_date, end_date)
            ).group_by(Section.id
            ).order_by(func.count(Request.id).desc()
            ).limit(5).all()

            result = [
            {
                'id': id,
                'section': section,
                'request_count': request_count,
                'pending': pending,
                'declined': declined,
                'withdrawn': withdrawn,
                'approved': approved,
                'returned': returned,
                'revoked': revoked
            }
            for id, section, request_count, pending, declined, withdrawn, approved, returned, revoked in popular_sections ]
            
            return jsonify(result)
        return cached_get_popular_sections()

@bp.route('/librarian/stats/ebooks',methods=['GET'])
@jwt_required()
def get_popular_ebooks():
    '''
     This api is accessed by librarian, to get the popular ebooks based on the total requests received.
     It returns the total requests count, along with the counts of each request status.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_popular_books():
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6 * 30)

            # Query to get the top 5 popular sections based on the number of requests
            popular_ebooks = db.session.query(
                Book.id,
                Book.name,
                func.count(Request.id).label('request_count'),
                func.sum(case((Request.req_status == 'Pending', 1), else_=0)).label('pending'),
                func.sum(case((Request.req_status == 'Declined', 1), else_=0)).label('declined'),
                func.sum(case((Request.req_status == 'Withdrawn', 1), else_=0)).label('withdrawn'),
                func.sum(case((Request.req_status == 'Approved', 1), else_=0)).label('approved'),
                func.sum(case((Request.req_status == 'Returned', 1), else_=0)).label('returned'),
                func.sum(case((Request.req_status == 'Revoked', 1), else_=0)).label('revoked')
            ).join(Request, Request.req_book_id == Book.id
            ).filter(Request.req_date.between(start_date, end_date)
            ).group_by(Book.id
            ).order_by(func.count(Book.id).desc()
            ).limit(5).all()

            result = [
            {
                'id': id,
                'name': name,
                'request_count': request_count,
                'pending': pending,
                'declined': declined,
                'withdrawn': withdrawn,
                'approved': approved,
                'returned': returned,
                'revoked': revoked
            }
            for id, name, request_count, pending, declined, withdrawn, approved, returned, revoked in popular_ebooks
        ]
            return jsonify(result)
    return cached_get_popular_books()

