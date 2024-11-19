from routes.auth import bp as auth_bp
from routes.sections import bp as sections_bp
from routes.books import bp as books_bp
from routes.requests import bp as requests_bp
from routes.preferences import bp as preferences_bp
from routes.stats import bp as stats_bp

def register(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(sections_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(stats_bp)
    
'''
    google_services.py
    ------------------
    Functions in this file
    1) initialize_google_service
    2) upload_cover
    3) upload_file
    4) delete_file
    5) add_email_to_file
    6) remove_email_from_file
'''

'''
    auth.py
    -------
    API's in this file
    1) librarian_login  -> No JWT           -> route('/api/auth/librarian-login', methods=['POST'])
    2) user_login       -> No JWT           -> route('/api/auth/user-login', methods=['POST'])
    3) user_register    -> No JWT           -> route('/api/auth/user-register', methods=['POST'])
    4) update_profile   -> roles:[user]     -> route('/api/auth/users', methods=['PUT'])
    5) update_password  -> roles:[user]     -> route('/api/auth/password', methods=['PUT'])
    6) get_all_users    -> roles:[user]     -> route('/api/users', methods=['GET'])
    
    Functions used from google_services file
    7) remove_email_from_file 
    8) add_email_to_file 
'''

'''
    books.py
    --------
    API's in this file
    1) get_book_info       -> roles:[librarian,user]   -> route('/api/books/<int:book_id>', methods=['GET'])
    2) librarian_get_books -> roles:[librarian]        -> route('/api/books/librarian', methods=['GET'])
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

'''
    preferences.py
    --------------
    API's in this file
    1) get_book_review      -> roles:[librarian,user] -> route('/api/reviews', methods=['GET'])
    2) add_book_review      -> roles:[user]           -> route('/api/reviews', methods=['POST'])
    3) add_book_ratings     -> roles:[user]           -> route('/api/rating', methods=['POST'])
    4) add_book_favourites  -> roles:[user]           -> route('/api/favourite', methods=['POST'])
'''

'''
    requests.py
    -----------
     API's in this file
    1) get_all_requests         -> roles:[librarian]        -> route('/api/requests', methods=['GET'])
    2) export_requests_csv      -> roles:[librarian]        -> route('/api/exportcsv',methods=['GET'])
    3) get_user_requests        -> roles:[librarian,user]   -> route('/api/requests/<int:user_id>', methods=['GET'])
    4) user_add_request         -> roles:[user]             -> route('/api/requests', methods=['POST'])
    5) librarian_update_request -> roles:[librarian]        -> route('/api/requests', methods=['PUT'])
    6) user_update_request      -> roles:[user]             -> route('/api/requests/user', methods=['PUT'])
    
    Functions used from google_services file
    7) add_email_to_file
    8) remove_email_from_file
'''

'''
    sections.py
    -----------
    API's in this file
    1) get_all_sections     -> roles:[librarian,user]   -> route('/api/sections', methods=['GET'])
    2) add_section          -> roles:[librarian]        -> route('/api/sections', methods=['POST'])
    3) edit_section         -> roles:[librarian]        -> route('/api/sections', methods=['PUT'])
    4) delete_section       -> roles:[librarian]        -> route('/api/sections/<int:section_id>', methods=['DELETE'])
    
    Functions used from google_services file
    5) upload_cover -> Used in add_section, edit_section api's
'''

'''
    stats.py
    --------
    API's in this file
    1) get_user_details       -> roles:[librarian,user]   -> route('/user/stats/details',methods=['GET'])
    2) get_user_summary       -> roles:[librarian,user]   -> route('/user/stats/summary',methods=['GET'])
    3) user_interest_sections -> roles:[librarian,user]   -> route('/user/stats/sections',methods=['GET'])
    4) get_total_summary      -> roles:[librarian]        -> route('/librarian/stats/summary',methods=['GET'])
    5) get_monthly_new_users  -> roles:[librarian]        -> route('/librarian/stats/new',methods=['GET'])
    6) get_popular_sections   -> roles:[librarian]        -> route('/librarian/stats/sections',methods=['GET'])
    7) get_popular_ebooks     -> roles:[librarian]        -> route('/librarian/stats/ebooks',methods=['GET']) 
'''