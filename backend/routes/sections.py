from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import Section,Book,db,Request,UserPreferences
from datetime import datetime
from app import app,cache
import os

from routes.cloud_file_management import upload_cover
from routes.books import delete_book

bp = Blueprint('sections', __name__)

'''
    API's in this file
    1) get_all_sections     -> roles:[librarian,user]   -> cached route('/api/sections', methods=['GET'])
    2) add_section          -> roles:[librarian]        -> route('/api/sections', methods=['POST'])
    3) edit_section         -> roles:[librarian]        -> route('/api/sections', methods=['PUT'])
    4) delete_section       -> roles:[librarian]        -> route('/api/sections/<int:section_id>', methods=['DELETE'])
    
    Functions used from google_services file
    5) upload_cover -> Used in add_section, edit_section api's
'''
@bp.route('/api/sections', methods=['GET'])
@jwt_required()
def get_all_sections():
    '''
        This api is accessed by both librarians and users to get all the sections 
        to display in the all sections page.
    '''
    identity = get_jwt_identity()
    if identity['role'] != 'librarian' and identity['role'] != 'user':
        return {'message': 'Unauthorized Access!'}, 403

    with app.app_context():
        @cache.cached(timeout=10)
        def get_sections_from_db():
            sections = Section.query.all()
            sections_info = [{
                "id": section.id,
                "name": section.name,
                "created_date": section.created_date,
                "description": section.description,
                'cover_url': section.cover_url
            } for section in sections]

            sections_info.sort(key=lambda x: x['created_date'], reverse=True)
            return jsonify(sections_info)

        return get_sections_from_db()

@bp.route('/api/sections', methods=['POST'])
@jwt_required()
def add_section():
    '''
        This api is accessed by librarian to add the section, the cover may or may not be provided.
        If cover is provided, it will be uploaded to drive and the url will be saved in table, 
        if not, the cover url will be empty string.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    name = request.form['name']
    description = request.form['description']
    created_date = datetime.now()
    
    if Section.query.filter_by(name=name).first():
        return {"message":'Section already exists'},400
    
    if 'cover' in request.files:
        cover = request.files['cover']
        if not allowed_cover(cover.filename):
            return {'message': 'Invalid cover image format. Only JPG, JPEG, PNG allowed.'}, 400
        try:
            cover_url = upload_cover(cover)
        except Exception as e:
            return {"message": 'Error uploading cover'}, 400
        new_section = Section(name=name,description=description,cover_url=cover_url,created_date=created_date)
    else:
        new_section = Section(name=name,description=description,created_date=created_date)
    db.session.add(new_section)
    db.session.commit()
    
    return {'message':'Section added successfully'},200

@bp.route('/api/sections', methods=['PUT'])
@jwt_required()
def edit_section():
    '''
        This api is accessed by librarian to edit the section.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    name = request.form['name']
    description = request.form['description']
    
    section = Section.query.get(request.form['id'])
    if not section:
        return {'message':'Section not found'},404
    
    if 'cover' in request.files:
        cover = request.files['cover']
        cover_url = upload_cover(cover)
        section.cover_url=cover_url
    
    section.name = name
    section.description = description
    
    db.session.commit()
    
    return {'message':'Section Updated successfully'},200

@bp.route('/api/sections/<int:section_id>', methods=['DELETE'])
@jwt_required()
def delete_section(section_id):
    '''
        This api is accessed by librarian to delete the section.
        Arguments:
            1) delete_books:
                If true, then for each book in this section, we use the delete_book function.
            2) new_section_id:
                If delete_books is false, then the api expects a new section id, to which this
                books should be moved to. Section id of each book of the existing section wil
                be changed to the new section id.
    '''
    identity = get_jwt_identity()
    if identity['role']!='librarian':
        return {'message':'Unauthorized Access!'}, 403
    
    delete_books = request.args.get('delete_books')
    if delete_books=='true':
        delete_books = True
    elif delete_books=='false':
        delete_books = False
    else:
        return jsonify({"message": "Unknown parameter for delete books!"}), 404
        
    new_section_id = request.args.get('new_section_id', None)
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found!"}), 404

    if delete_books:
        # Delete books associated with the section
        books = Book.query.filter_by(section_id=section_id).all()
        for book in books:
            delete_book(book.id)
    else:
        if new_section_id is None:
            return jsonify({"message": "New section ID required to move books!"}), 400
        
        # Move books to a new section
        new_section = Section.query.get(new_section_id)
        if not new_section:
            return jsonify({"message": "New section not found!"}), 404
        
        books = Book.query.filter_by(section_id=section_id).all()
        for book in books:
            book.section_id = new_section_id
        db.session.commit()

    db.session.delete(section)
    db.session.commit()

    return jsonify({"message": "Section deleted successfully!"}), 200

def allowed_cover(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}