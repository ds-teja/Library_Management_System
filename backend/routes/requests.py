from flask import Blueprint, request, jsonify,make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import Book,db,Request, User
from datetime import datetime, timedelta
from tasks import export_as_csv
from app import app, cache

from routes.cloud_file_management import add_email_to_file,remove_email_from_file
bp = Blueprint('requests', __name__)

'''
    API's in this file
    1) export_requests_csv      -> roles:[librarian]        -> route('/api/exportcsv',methods=['GET'])
    2) get_all_requests         -> roles:[librarian]        -> cached with key route('/api/requests', methods=['GET'])
    3) get_user_requests        -> roles:[librarian,user]   -> cached route('/api/requests/<int:user_id>', methods=['GET'])
    4) user_add_request         -> roles:[user]             -> route('/api/requests', methods=['POST'])
    5) librarian_update_request -> roles:[librarian]        -> route('/api/requests', methods=['PUT'])
    6) user_update_request      -> roles:[user]             -> route('/api/requests/user', methods=['PUT'])
    
    Functions used from google_services file
    7) add_email_to_file
    8) remove_email_from_file   
'''

@bp.route('/api/exportcsv',methods=['GET'])
@jwt_required()
def export_requests_csv():
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403

    csv_data = export_as_csv()
    response = make_response(csv_data)
    today_date = datetime.now()
    today_date = str(today_date).split(' ')[0]
    file_name = today_date + '_requests_report.csv'
    response.headers['Content-Disposition'] = f"attachment;filename={file_name}"
    response.headers['Content-type'] = 'text/csv'
    return response 

@bp.route('/api/requests', methods=['GET'])
@jwt_required()
def get_all_requests():
    '''
        get_all_requests is accessed by the librarian to show the requests details of all users in the Requests page.
    '''
    identity = get_jwt_identity()
    if identity['role'] != 'librarian':
        return {'message': 'Unauthorized Access!'}, 403
    
    user_id = request.args.get('user_id', None)
    book_id = request.args.get('book_id', None)
    cache_key = f"get_all_requests_{user_id or 'all'}_{book_id or 'all'}"
       
    with app.app_context():
        @cache.cached(timeout=10,key_prefix=cache_key)
        def cached_get_all_requests():
            
            if user_id:
                if not User.query.get(user_id):
                    return {'message':'User Id not found'}, 404
                requests = db.session.query(Request, User, Book).join(User, Request.req_user_id == User.id).join(Book, Request.req_book_id == Book.id).filter(Request.req_user_id == user_id).all()
            elif book_id:
                if not Book.query.get(book_id):
                    return {'message':'Book Id not found'}, 404
                requests = db.session.query(Request, User, Book).join(User, Request.req_user_id == User.id).join(Book, Request.req_book_id == Book.id).filter(Request.req_book_id == book_id).all()
            else:
                requests = db.session.query(Request, User, Book).join(User, Request.req_user_id == User.id).join(Book, Request.req_book_id == Book.id).all()

            requests_info = []
            for req, user, book in requests:
                requests_info.append({
                    "id": req.id,
                    "user_id": user.id,
                    "user_name": user.username,
                    "book_name": book.name,
                    "req_date": req.req_date,
                    "req_status": req.req_status,
                    "req_is_active": req.req_is_active,
                    "issued_date":(req.issued_date).strftime("%a, %d %b %Y") if req.issued_date else None,
                    "return_date":(req.return_date).strftime("%a, %d %b %Y") if req.return_date else None,
                })
            
            requests_info.sort(key=lambda x: x['req_date'],reverse=True)
            active_requests = [req for req in requests_info if req['req_is_active']==True]
            inactive_requests = [req for req in requests_info if req['req_is_active']==False]
            result={
                'active_count':len(active_requests),
                'active_requests': active_requests,
                'inactive_count':len(inactive_requests),
                'inactive_requests': inactive_requests,
            }
            return jsonify(result)
        return cached_get_all_requests() 

@bp.route('/api/requests/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_requests(user_id):
    '''
        get_user_requests is accessed by the user to the requests information of that particular user to show in mybooks page.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user' and identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_user_requests():
            user_book_requests = Request.query.filter_by(req_user_id = user_id).all()
            
            if not user_book_requests:
                result={'inactive_count':0,'active_count':0,'active_requests': {},'inactive_requests': {}}
                return jsonify(result), 200
            
            requests_info = []
            for request in user_book_requests:
                book = Book.query.get(request.req_book_id)
                if book:
                    requests_info.append({
                        "req_id": request.id,
                        "book_id": book.id,
                        "name": book.name,
                        "author": book.author,
                        "section_name": book.section.name,
                        "req_date": request.req_date,
                        "req_status": request.req_status,
                        "req_is_active": request.req_is_active,
                        "issued_date": (request.issued_date).strftime("%a, %d %b %Y") if request.issued_date else None,
                        "expiry_date": (request.issued_date + timedelta(days=7)).strftime("%a, %d %b %Y") if request.issued_date else None,
                        "return_date": (request.return_date).strftime("%a, %d %b %Y") if request.return_date else None,
                    })
                    
            requests_info.sort(key=lambda x: x['req_date'],reverse=True)
            active_requests = [req for req in requests_info if req['req_is_active']==True]
            inactive_requests = [req for req in requests_info if req['req_is_active']==False]
            result={
                'active_count':len(active_requests),
                'active_requests': active_requests,
                'inactive_count':len(inactive_requests),
                'inactive_requests': inactive_requests,
            }
            return jsonify(result)
        return cached_get_user_requests()

@bp.route('/api/requests', methods=['POST'])
@jwt_required()
def user_add_request():
    '''
        add_request api is to create a Pending request for a user.
        It will throw error for any other type of status.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    data = request.get_json()
    req_user_id = data.get('req_user_id')
    req_book_id = data.get('req_book_id')
    
    already_active_record = Request.query.filter_by(req_user_id = req_user_id, req_book_id = req_book_id, req_is_active=True).first()
    if already_active_record:
        return {'message':'The book status is already active for the user!'}, 404
    
    max_active_records = Request.query.filter(Request.req_user_id == req_user_id, Request.req_is_active==True).count()
    if max_active_records >= 5:
        return {'message': 'Maximum active requests reached.'}, 400
    
    req_date = datetime.fromisoformat(data['req_date'].replace("Z", "+00:00"))
    req_status = data.get('req_status')
    
    if req_status == 'Approved' or req_status == 'Revoked' or req_status == 'Declined':
        return {'message':'Unauthorized Access!'}, 403
    elif req_status != 'Pending':
        return {'message':'Status does not exist!'}, 404
    
    new_request = Request(req_user_id,req_book_id,req_date,req_status)
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({'message': 'Request Added Succesfully! Please wait for Admin Response.'}), 200

@bp.route('/api/requests', methods=['PUT'])
@jwt_required()
def librian_update_request():
    '''
        This api is to be accessed by librarian alone to update the request status to 
        either Approved, Declined, or Revoked. Any other status will throw error.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    data = request.get_json()
    request_id = data.get('request_id')
    request_record = Request.query.get(request_id)
    
    if not request_record:
        return jsonify({'message': 'Request not found'}), 404
    
    new_status = data.get('req_status')
    
    if new_status == 'Approved':
        try:
            file_id = Book.query.get(request_record.req_book_id).cloud_file_id
            email_to_add = User.query.get(request_record.req_user_id).email
            add_email_to_file(file_id,email_to_add)
            request_record.issued_date = datetime.now()
        except Exception as e:
            return {'message':f'Error approving the user - {e}'}, 404
        
        
    elif new_status == 'Declined':
        request_record.req_is_active = False
        
    elif new_status == 'Revoked':
        try:
            file_id = Book.query.get(request_record.req_book_id).cloud_file_id
            email_to_remove = User.query.get(request_record.req_user_id).email
            remove_email_from_file(file_id,email_to_remove)         
            request_record.req_is_active = False
            request_record.return_date = datetime.now()
        except Exception as e:
            return {'message':f'Error to Revoke acces for the user {e}'}, 404
        
    else:
        return jsonify({'message': 'Status does not exist!'}), 404
        
    request_record.req_status=new_status
    db.session.commit()
    return jsonify({'message': 'Request Updated Succesfully.'}), 200

@bp.route('/api/requests/user', methods=['PUT'])
@jwt_required()
def user_update_request():
    '''
        This api is to be accessed by user alone to update the request status to 
        either withdrawn or returned. Any other status will throw error.
    '''
    identity = get_jwt_identity()
    if identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    data = request.get_json()
    request_id = data.get('request_id')
    request_record = Request.query.get(request_id)
    
    if not request_record:
        return jsonify({'message': 'Request not found'}), 404
    
    new_status = data.get('req_status')
    if new_status == 'Approved' or new_status == 'Revoked' or new_status == 'Declined':
        return {'message':'Unauthorized Access!'}, 403
    elif new_status == 'Returned':
        try:
            file_id = Book.query.get(request_record.req_book_id).cloud_file_id
            email_to_remove = User.query.get(request_record.req_user_id).email
            remove_email_from_file(file_id,email_to_remove)         
            request_record.req_is_active = False
            request_record.return_date = datetime.now()
        except Exception as e:
            return {'message':f'Error while returning the book, please retry'}, 404
    elif new_status == 'Withdrawn':
        request_record.req_is_active = False
    else:
        return jsonify({'message': 'status does not exist'}), 404
    
    request_record.req_status=new_status
    db.session.commit()
    return jsonify({'message': 'Request Updated Succesfully.'}), 200

