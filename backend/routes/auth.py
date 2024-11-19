from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token,unset_jwt_cookies
from flask_cors import cross_origin
from model import db,User,Book,Request
from datetime import timedelta, datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app,cache

from routes.cloud_file_management import add_email_to_file,remove_email_from_file

bp = Blueprint('auth', __name__)

'''
    API's in this file
    1) librarian_login  -> No JWT           -> route('/api/auth/librarian-login', methods=['POST'])
    2) user_login       -> No JWT           -> route('/api/auth/user-login', methods=['POST'])
    3) user_register    -> No JWT           -> route('/api/auth/user-register', methods=['POST'])
    4) update_profile   -> roles:[user]     -> route('/api/auth/users', methods=['PUT'])
    5) update_password  -> roles:[user]     -> route('/api/auth/password', methods=['PUT'])
    6) get_all_users    -> roles:[user]     -> cached route('/api/users', methods=['GET'])
    
    Functions used from google_services file
    7) remove_email_from_file -> Used in update_profile while updating email to remove the books access for old email 
    8) add_email_to_file -> Used in update_profile while updating email to add the books access for new email 
'''

@bp.route('/api/auth/librarian-login', methods=['POST'])
def librarian_login():
    '''
        This api is for the librarian to login.
        On succesfful login, returns the access token.
    '''
    data = request.get_json()
    name_or_email = data.get('username')
    password = data.get('password')
        
    name_user = User.query.filter_by(username=name_or_email, role='librarian').first()
    email_user = User.query.filter_by(email=name_or_email, role='librarian').first()
    
    if name_user and check_password_hash(name_user.password, password):
        token = create_access_token(identity={'id': name_user.id, 'role': name_user.role}, expires_delta=timedelta(days=1))
        return jsonify({'access_token': token}), 200
    elif email_user and check_password_hash(email_user.password, password):
        token = create_access_token(identity={'id': email_user.id, 'role': email_user.role}, expires_delta=timedelta(days=1))
        return jsonify({'access_token': token}), 200        
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
@bp.route('/api/auth/user-login', methods=['POST'])
def user_login():
    '''
        This Api is for the user to login.
        On succesfful login, returns the access token.
    '''
    data = request.get_json()
    name_or_email = data.get('username')
    password = data.get('password')
        
    name_user = User.query.filter_by(username=name_or_email, role='user').first()
    email_user = User.query.filter_by(email=name_or_email, role='user').first()
    
    if name_user and check_password_hash(name_user.password, password):
        token = create_access_token(identity={'id': name_user.id, 'role': name_user.role}, expires_delta=timedelta(days=1))
        return jsonify({'access_token': token}), 200
    elif email_user and check_password_hash(email_user.password, password):
        token = create_access_token(identity={'id': email_user.id, 'role': email_user.role}, expires_delta=timedelta(days=1))
        return jsonify({'access_token': token}), 200        
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
@bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return response, 200

@bp.route('/api/auth/user-register', methods=['POST'])
def user_register():
    '''
        This api is for the user to register.
    '''
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    nationality = data.get('nationality')
    password = generate_password_hash(data.get('password'))

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists! Try another Username!'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists! Try another Email!'}), 400

    new_user = User(username=username, email=email, password=password, created_date=datetime.now(), nationality=nationality)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True}), 200

@bp.route('/api/auth/users', methods=['PUT'])
@jwt_required()
def update_profile():
    '''
        This api is used by only users to update their profile page.
        If the email is also changed, then we get the approved requests of the user,
        and remove the access for the older mail, and give access for the new mail.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403

    user_id = identity['id']
    user = User.query.get(user_id)
    if not user:
        return {'message':'User does not exist'}, 404
    
    data = request.get_json()
    username = data.get('username')
    new_email = data.get('email')
    about_me = data.get('about_me')
    
    user.username = username
    user.about_me = about_me

    if(user.email!=new_email):
        try:
            requests = Request.query.filter_by(user_id=user_id,req_status='Approved').all()
            for request_record in requests:
                file_id = Book.query.get(request_record.req_book_id).cloud_file_id
                # Remove permission for the old email
                remove_email_from_file(file_id,user.email)
                # Add Permission for the new email
                add_email_to_file(file_id,new_email)
                
            user.email = new_email
        except Exception as e:
            return {'message':f'Error Chaning the mail for Approved books {e}'}, 400
    
    db.session.commit()
    
    return {'message':'User Details updated succesfully!'}, 200


@bp.route('/api/auth/password', methods=['PUT'])
@jwt_required()
def update_password():
    '''
        This api is for the users to update their account password.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403

    user_id = identity['id']
    user = User.query.get(user_id)
    if not user:
        return {'message':'User does not exist'}, 404
    
    data = request.get_json()
    password = data.get('password')
    
    user.password = generate_password_hash(password)
    
    db.session.commit()
    return {'message':'Password updated succesfully!'}, 200
    
@bp.route('/api/users', methods=['GET'])
@jwt_required()
def get_all_users():
    '''
      This api is for the librarian, to monitor the users in Handle users page.
      It returns the details of all the users.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_all_users():
            users = User.query.filter_by(role='user').all()
            user_list = [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nationality': user.nationality,
                    'created_date': user.created_date
                }
                for user in users
            ]
            user_list.sort(key=lambda x: x['created_date'],reverse=True)
            return jsonify(user_list)

        return cached_get_all_users()
