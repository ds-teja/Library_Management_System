from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import send_file
from model import Book,db,Section,Request,UserPreferences
from datetime import datetime
from app import app,cache
import os
import shutil

from routes.cloud_file_management import upload_cover,upload_file,delete_file

bp = Blueprint('books', __name__)

'''
    API's in this file
    1) get_book_info       -> roles:[librarian,user]   -> cached route('/api/books/<int:book_id>', methods=['GET'])
    2) librarian_get_books -> roles:[librarian]        -> cached with key route('/api/books/librarian', methods=['GET'])
    3) user_get_books      -> roles:[user]             -> route('/api/books/user', methods=['GET'])
    4) view_book           -> roles:[librarian,user]   -> route('/api/books/<int:book_id>/content', methods=['GET'])
    5) delete_book         -> roles:[librarian]        -> route('/api/books/<int:book_id>', methods=['DELETE'])
    6) add_book            -> roles:[librarian]        -> route('/api/books', methods=['POST'])
    7) edit_book           -> roles:[librarian]        -> route('/api/books', methods=['PUT'])
    
    Functions in this file
    8) allowed_cover
    9) allowed_file
    
    Functions used from google_services file
    10) upload_cover
    11) upload_file
    12) delete_file
'''

@bp.route('/api/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book_info(book_id):
    '''
        This Api is accessed by both librarian and users, to get the information of a
        single book to display in Know More Page.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian' and identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    with app.app_context():
        @cache.cached(timeout=10)
        def cached_get_book_info():
            book = Book.query.get(book_id)
            if not book:
                return {"message": 'Book does not exists'}, 404
            
            return jsonify({
                "name":book.name,
                "author":book.author,
                "num_pages":book.num_pages,
                "prologue":book.prologue,
                "section_id":book.section_id,
                "section_name":book.section.name,
                "cover_url":book.cover_url,
            })
        
        return cached_get_book_info()
    
@bp.route('/api/books/librarian', methods=['GET'])
@jwt_required()
def librarian_get_books():
    '''
        This Api is accessed by librarian to get all the books information along with the content url.
        Arguments:
        section_id -> It can be passed if we want the books of a particular section.
                      If the argument is not passed, then it will return all the books, where the section_name will be empty.
    '''    
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    section_id = request.args.get('section_id', None)
    cache_key = f"librarian_get_books_{section_id}"
    
    with app.app_context():
        @cache.cached(timeout=10,key_prefix=cache_key)
        def cached_librarian_get_books():
            section_name = ''
            
            if section_id:
                section = Section.query.get(section_id)
                if section:
                    section_name = section.name
                    books = Book.query.filter_by(section_id=section_id).all()
                else:
                    return {'message':'Section Does not exist!'}, 404
            else:
                books = Book.query.all()
                
            books_info=[]
            for book in books:
                books_info.append({
                    "id": book.id,
                    "name": book.name,
                    "author": book.author,
                    "cover_url": book.cover_url,
                    "section_name": book.section.name,
                    "section_id": book.section.id,
                    "num_pages": book.num_pages,
                    "prologue": book.prologue,
                    "content_url": book.content_url,
                    "upload_date": book.upload_date
                })
            books_info.sort(key=lambda x: x['upload_date'],reverse=True)
            
            result = {
                'section_name':section_name,
                'books_info':books_info,
                'books_count':len(books_info)
            }
            return jsonify(result)
        
        return cached_librarian_get_books()
    
@bp.route('/api/books/user', methods=['GET'])
@jwt_required()
def user_get_books():
    '''
        This Api is only accessed by users, to display the all books in the user home page.
        Arguments:
            section_id -> If passed, will return the books of the section.
            shelf -> If passed, will return the books of the user from the provided shelf.
            fav -> If passed, will return the book of the user that are favourites.
        
        Books info is returned based on the req status of the books for user, selected shelf, rating, and favourites.
        Which will be used to the show the according button for the book in user home page.
    '''
    identity = get_jwt_identity()
    if identity['role'] != 'user':
        return {'message': 'Unauthorized Access!'}, 403
    

    user_id = identity['id']
    section_name = ''
    
    # Get request parameters
    section_id = request.args.get('section_id',None)
    shelf = request.args.get('shelf',None)
    fav = request.args.get('fav',None)
    downloaded = request.args.get('downloaded',None)
    
    # Base book query
    book_query = Book.query
    
    if section_id:
        section = Section.query.get(section_id)
        if section:
            section_name = section.name
            book_query = book_query.filter_by(section_id=section_id)
        else:
            return {'message': 'Section does not exist!'}, 404
    
    if shelf:
        if shelf in ['Completed List', 'Currently Reading', 'To Read List']:
            book_query = db.session.query(Book).join(
                UserPreferences, Book.id == UserPreferences.book_id
            ).filter(UserPreferences.user_id == user_id, UserPreferences.shelf == shelf)
        else:
            return {'message': "Shelf not found"}, 404

    if fav == 'true':
        book_query = db.session.query(Book).join(
            UserPreferences, Book.id == UserPreferences.book_id
        ).filter(UserPreferences.user_id == user_id, UserPreferences.favourites == True)
        
    if downloaded == 'true':
        book_query = db.session.query(Book).join(
            UserPreferences, Book.id == UserPreferences.book_id
        ).filter(UserPreferences.user_id == user_id, UserPreferences.downloaded == True)

    books = book_query.all()

    # Get user preferences and active requests
    user_preferences = {pref.book_id: pref for pref in UserPreferences.query.filter_by(user_id=user_id).all()}
    active_requests = {req.req_book_id: req for req in Request.query.filter_by(req_user_id=user_id, req_is_active=True).all()}

    # Building books info based on the req status of the books for user, selected shelf, rating, and favourites.
    books_info = [{
        "id": book.id,
        "name": book.name,
        "author": book.author,
        "cover_url": book.cover_url,
        "section_id": book.section.id,
        "section_name": book.section.name,
        "req_status": active_requests[book.id].req_status if book.id in active_requests else 'NoRequest',
        "selectedShelf": user_preferences[book.id].shelf if book.id in user_preferences else '',
        "selectedRating": user_preferences[book.id].rating if book.id in user_preferences else '',
        "isFavourite": user_preferences[book.id].favourites if book.id in user_preferences else False,
        "isDownloaded": user_preferences[book.id].downloaded if book.id in user_preferences else False,
        "upload_date": book.upload_date
    } for book in books]

    books_info.sort(key=lambda x: x['upload_date'], reverse=True)
    
    result = {
        'section_name': section_name,
        'books_info': books_info,
        'books_count': len(books_info)
    }
    return jsonify(result)

@bp.route('/api/books/<int:book_id>/content', methods=['GET'])
@jwt_required()
def view_book(book_id):
    '''
        Get_book_content api returns the drive previewe link to view the content of the book.
        It can be accessed by librarian and also the user. The librarian can view any book without any limitation.
        The user can only view the book if he has the req status for this book as approved in the request table.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian' and identity['role']!='user':
        return {'message':'Unauthorized Access!'}, 403
    
    book = Book.query.get(book_id)
    if not book:
        return {"message":'Book Does not exist!'},404
    
    if identity['role'] == 'user':
        is_valid_user = Request.query.filter(
            Request.req_user_id == identity['id'],
            Request.req_book_id == book_id,
            Request.req_status == 'Approved'
        ).first() is not None
        
        downloaded_user = UserPreferences.query.filter(
            UserPreferences.user_id == identity['id'],
            UserPreferences.book_id == book_id,
            UserPreferences.downloaded == True
        ).first() is not None

        if not (is_valid_user or downloaded_user):
            return {'message': 'Unauthorized Access!'}, 403
    
    return {"book_url":book.content_url,"name":book.name,"id":book.id,"book_name":book.book_name,"price":100},200

@bp.route('/api/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    '''
        This api is accessed only by the librarian to delete the book. Deleting the book has 4 stages,
        1) Delete the book in the google drive
        2) Delete all the requests that are related to this book
        3) Delete all the preferences that are related to this book(like, ratings, reviews, shelves, & favourites) 
        4) Finally Delete the book from the table.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    book = Book.query.get(book_id)
    if not book:
        return {'message':'Book not found'}, 404
    
    # Step 1 - Deleting the book from google drive
    try:
        file_id = book.cloud_file_id
        delete_file(file_id)
    except Exception as e:
        return {'message':f'Error Deleting the cloud file {e}'}, 400
    
    # Step 2,3,4 - Deleting requests, preferences, and finally the book.
    Request.query.filter_by(req_book_id=book_id).delete()
    UserPreferences.query.filter_by(book_id=book_id).delete()
    db.session.delete(book)
    
    db.session.commit()
    return jsonify({"message": "Book deleted successfully!"}), 200
    
@bp.route('/api/books', methods=['POST'])
@jwt_required()
def add_book():
    '''
        This API is accessed only by the librarian to add books, along with the content, which will upload the 
        content to Google Drive and also save a copy in the uploads folder on the backend.
    '''
    # Check if the user is authorized as a librarian
    identity = get_jwt_identity()
    if identity['role'] != 'librarian':
        return {'message': 'Unauthorized Access!'}, 403
    
    # Check if all required fields are provided
    required_fields = ['name', 'author', 'section_id', 'num_pages', 'prologue']
    if not all(field in request.form for field in required_fields):
        return {'message': 'Missing required fields'}, 400
    
    # Check if content field are provided
    if 'content' not in request.files:
        return {'message':'content is required field'},400
    
    # Check if the book already exists
    existing_book = Book.query.filter_by(name=request.form['name']).first()
    if existing_book:
        return {"message": 'Book already exists'}, 400
    
    # Validate cover image if uploaded
    if 'cover' in request.files:
        cover = request.files['cover']
        if not allowed_cover(cover.filename):
            return {'message': 'Invalid cover image format. Only JPG, JPEG, PNG allowed.'}, 400
        try:
            cover_url = upload_cover(cover)
        except Exception as e:
            return {"message": 'Error uploading cover'}, 400
    else:
        cover_url = ''
    
    # Validate content file (PDF)
    file = request.files['content']
    section_id = request.form['section_id']
    section_name = Section.query.get(section_id).name
    if not allowed_file(file.filename):
        return {'message': 'Invalid file format. Only PDF files allowed.'}, 400
    try:
        file_id,content_url = upload_file(file,section_name)
    except Exception as e:
        return {"message": 'Error uploading File'}, 400
    
    # Create a new book entry in the database
    new_book = Book(
        name=request.form['name'].strip(),
        author=request.form['author'].strip(),
        book_name=file.filename,
        cover_url=cover_url,
        content_url=content_url,
        cloud_file_id=file_id,
        section_id=request.form['section_id'],
        num_pages=request.form['num_pages'],
        prologue=request.form['prologue'],
        upload_date=datetime.now()
    )
    
    # Commit to database
    db.session.add(new_book)
    db.session.commit()
    
    return {'message': 'Book added successfully'}, 200

@bp.route('/api/books', methods=['PUT'])
@jwt_required()
def edit_book():
    '''
        This API is accessed only by the librarian to add books, along with the content, which will upload the 
        content to Google Drive and also save a copy in the uploads folder on the backend.
    '''
    identity = get_jwt_identity()
    if identity['role'] != 'librarian':
        return {'message': 'Unauthorized Access!'}, 403
    
    book = Book.query.get(request.form['id'])
    if not book:
        return {"message": 'Book does not exists'}, 404
    
    name_change = Book.query.filter_by(name=request.form['name']).first()
    if name_change and name_change.id!=book.id:
        return {'message':'Book name already exists!'}, 400
    
    book.name = request.form['name']    
    book.author = request.form['author']
    book.num_pages = request.form['num_pages']
    book.prologue = request.form['prologue']
    
    new_section_id = request.form['section_id']
    # Move the file to the new section directory if the section has changed
    if book.section_id != new_section_id:
        new_section = Section.query.get(new_section_id)
        if not new_section:
            return {'message':'section not found'}, 404
        
        # If section is changed, move the book to new section directory
        file_uploads_dir = 'file_uploads'

        old_section_dir = os.path.join(file_uploads_dir, book.section.name)
        new_section_dir = os.path.join(file_uploads_dir, new_section.name)

        old_file_path = os.path.join(old_section_dir, book.book_name)
        new_file_path = os.path.join(new_section_dir, book.book_name)

        try:
            shutil.move(old_file_path, new_file_path)
            book.section_id = new_section_id
        except Exception as e:
            return {'message': f"Error moving file {e}"}, 500
    
    # Validate cover image if uploaded
    if 'cover' in request.files:
        cover = request.files['cover']
        if not allowed_cover(cover.filename):
            return {'message': 'Invalid cover image format. Only JPG, JPEG, PNG allowed.'}, 400
        try:
            # Replace this with actual upload cover logic
            book.cover_url = upload_cover(cover)
        except Exception as e:
            return {"message": 'Error uploading cover'}, 400
    
    # Validate content file (PDF)
    section_id = request.form['section_id']
    section_name = Section.query.get(section_id).name
    if 'content' in request.files:
        file = request.files['content']
        if not allowed_file(file.filename):
            return {'message': 'Invalid file format. Only PDF files allowed.'}, 400
        try:
            # Replace this with actual upload file logic
            book.cloud_file_id,book.content_url = upload_file(file,section_name)
        except Exception as e:
            return {"message": 'Error uploading File'}, 400

    db.session.commit()
    
    return {'message': 'Book Updated successfully'}, 200

@bp.route('/api/books/download/<int:book_id>',methods=['GET'])
@jwt_required()
def download_book(book_id):
    identity = get_jwt_identity()
    if identity['role'] != 'librarian' and identity['role']!='user':
        return {'message': 'Unauthorized Access!'}, 403
    
    book = Book.query.get(book_id)
    if not book:
        return {"message": 'Book does not exists'}, 404
    
    book_file_path = f'file_uploads/{book.section.name}/{book.book_name}'
    if(identity['role']=='user'):
        user_id = identity['id']
        existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
        if not existing_record:
            new_record = UserPreferences(user_id=user_id,book_id=book_id)
            db.session.add(new_record)
            db.session.commit()
            existing_record = UserPreferences.query.filter(UserPreferences.user_id==user_id,UserPreferences.book_id==book_id).first()  
        
        existing_record.downloaded = True
        request_record = Request.query.filter_by(req_user_id=user_id,req_book_id=book_id,req_is_active=True).first()
        request_record.req_status = 'Downloaded'
        request_record.req_is_active = False
        db.session.commit()
        
    try:
        return send_file(book_file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Error with file path'}), 404

def allowed_cover(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'pdf'