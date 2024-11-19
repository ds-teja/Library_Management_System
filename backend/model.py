from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACT_MODIFICATIONS'] = False
db = SQLAlchemy(app)  

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    nationality = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    about_me = db.Column(db.String())
    role = db.Column(db.String(), nullable=False, default='user')
    
    requests = db.relationship('Request',backref='user')
    
    def __init__(self,username,email,password,created_date,nationality,role: str='user'):
        self.username = username
        self.email = email
        self.password = password
        self.nationality = nationality
        self.role = role
        self.created_date=created_date

    def __repr__(self):
        return f'<User {self.username}>'
  
class Section(db.Model):
    __tablename__='sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(), nullable=False)
    cover_url = db.Column(db.String(),default='')
    
    books = db.relationship('Book',backref='section')
    
    def __init__(self,name,created_date,description,cover_url:str=''):
        self.name=name
        self.created_date=created_date
        self.description=description
        self.cover_url=cover_url
    
    def __repr__(self):
        return f'<Section {self.name}>'
    
class Book(db.Model):
    __tablename__='books'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    author = db.Column(db.String(), nullable=False)
    book_name = db.Column(db.String(), nullable=False)
    num_pages = db.Column(db.Integer, nullable=False)
    prologue = db.Column(db.String(),default='')
    cover_url = db.Column(db.String(),default='')
    content_url = db.Column(db.String(), nullable=False)
    cloud_file_id = db.Column(db.String(), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    upload_date = db.Column(db.DateTime,nullable=False)
    
    requests = db.relationship('Request',backref='book')
    
    def __init__(self,name,author,section_id,book_name,num_pages,upload_date,content_url,cloud_file_id,cover_url:str='',prologue:str=''):
        self.name=name
        self.author=author
        self.section_id=section_id
        self.num_pages = num_pages
        self.cover_url=cover_url
        self.content_url=content_url
        self.book_name = book_name
        self.prologue = prologue
        self.upload_date = upload_date
        self.cloud_file_id = cloud_file_id
        
    def __repr__(self):
        return f'<Book {self.name}>'

class Request(db.Model):
    __tablename__='requests'
    
    id = db.Column(db.Integer, primary_key=True)
    req_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    req_book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    req_date = db.Column(db.DateTime, nullable=False)
    req_status = db.Column(db.String(), nullable=False)
    req_is_active = db.Column(db.Boolean, default=True, nullable=False)
    issued_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)    
    
    def __init__(self,req_user_id,req_book_id,req_date,req_status):
        self.req_user_id = req_user_id
        self.req_book_id = req_book_id
        self.req_date = req_date
        self.req_status = req_status    

class UserPreferences(db.Model):
    __tablename__='userPreferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Integer,default='')
    favourites = db.Column(db.Boolean, default=False)
    shelf = db.Column(db.String,default='')
    completed_date = db.Column(db.DateTime)
    review = db.Column(db.String,default='')
    downloaded = db.Column(db.Boolean, default=False)
    
    def __init__(self,user_id,book_id):
        self.user_id = user_id
        self.book_id = book_id
def create_sections():
    sections = [
        {'name': 'Self-help', 'created_date': '2024-07-17 18:06:40.642175', 'description': 'Explore the self help books to improve your mental health.', 'cover_url': 'https://drive.google.com/thumbnail?id=1vdez-u90DpDVOERRJBU4V-lcXKBdulsT'},
        {'name': 'Machine Learning', 'created_date': '2024-07-17 18:10:33.102007', 'description': 'Machine learning is better learnt with books, Explore the intricate machine learning books.', 'cover_url': 'https://drive.google.com/thumbnail?id=1vl770jzYbMa4DEkwgPcjyuQvUu46YoIP'},
        {'name': 'Deep Learning', 'created_date': '2024-07-17 18:18:20.486954', 'description': 'Explore the neural networks with clear visuals from these books.', 'cover_url': 'https://drive.google.com/thumbnail?id=1xUhqUtYR7YPRJIAuZx_BiXEsQLKyQeOI'}
    ]
    
    for data in sections:
        section = Section(
            name=data['name'],
            created_date=datetime.strptime(data['created_date'], '%Y-%m-%d %H:%M:%S.%f'),
            description=data['description'],
            cover_url=data['cover_url']
        )
        db.session.add(section)
    
    db.session.commit()

    print("Sections have been created and added to the database.")
    
def create_books():
    books = [
        ('Think Like a Monk', 'Jay Shetty', 'Think Like a Monk (Jay Shetty).pdf', 'https://drive.google.com/thumbnail?id=1uda449_aRvHtcVtdGP7qPvOKkrkeeTh2', 'https://drive.google.com/file/d/1Xy6oLsO8IB9aicrbA1_wOjZL6kPcOxKK/preview', '1Xy6oLsO8IB9aicrbA1_wOjZL6kPcOxKK', 1, 319, """When you think like a monk, you’ll understand:
- How to overcome negativity
- How to stop overthinking
- Why comparison kills love
- How to use your fear
- Why you can’t find happiness by looking for it
- How to learn from everyone you meet
- Why you are not your thoughts
- How to find your purpose
- Why kindness is crucial to success
- And much more...

In this inspiring, empowering book, Shetty draws on his time as a monk to show us how we can clear the roadblocks to our potential and power. Combining ancient wisdom and his own rich experiences in the ashram, Think Like a Monk reveals how to overcome negative thoughts and habits, and access the calm and purpose that lie within all of us. He transforms abstract lessons into advice and exercises we can all apply to reduce stress, improve relationships, and give the gifts we find in ourselves to the world. Shetty proves that everyone can—and should—think like a monk."""),
        ('Atomic Habits', 'James Clear', 'Atomic Habits Tiny Changes, Remarkable Results (James Clear).pdf', 'https://drive.google.com/thumbnail?id=1I9mq5c_78kvQ8P9sxOFcyr2rS8UMXXyc', 'https://drive.google.com/file/d/1zDD6blvnm2AFHZ-kGtaN0uOdT2ozzkfi/preview', '1zDD6blvnm2AFHZ-kGtaN0uOdT2ozzkfi', 1, 290, """Learn how to:
- Make time for new habits (even when life gets crazy);
- Overcome a lack of motivation and willpower;
- Design your environment to make success easier;
- Get back on track when you fall off course;
...and much more.

Atomic Habits will reshape the way you think about progress and success, and give you the tools and strategies you need to transform your habits--whether you are a team looking to win a championship, an organization hoping to redefine an industry, or simply an individual who wishes to quit smoking, lose weight, reduce stress, or achieve any other goal."""),
        ('Think and Grow Rich', 'Napoleon Hill', 'Think and Grow Rich (Napoleon Hill).pdf', 'https://drive.google.com/thumbnail?id=1NhrxDrxU-G6472Cjaz7XdFLvzS_-UaMb', 'https://drive.google.com/file/d/1LQi9d4PevhjDVR2TkfH_NqjaL5ciZHfE/preview', '1LQi9d4PevhjDVR2TkfH_NqjaL5ciZHfE', 1, 426, """Think and Grow Rich is a guide to success by Napoleon Hill, which was first published in 1937 following the Great Depression. It was immediately welcomed as an antidote to hard times and remained a bestseller for decades. Many people still find its philosophy of positive thinking and its specific steps for achieving wealth both relevant and life-changing. Hill contends that our thoughts become our reality, and offers a plan and principles for transforming thoughts into riches, including visualization, affirmation, creating a Master Mind group, defining a goal, and planning."""),
        ('Machine Learning Yearning', 'Andrew NG', 'Ng_MachineLearningYearning.pdf', 'https://drive.google.com/thumbnail?id=1TDcySUCYeB1o7YLowidihVfFIALRrNLI', 'https://drive.google.com/file/d/1125_1A0Blb2WjFSPnQzFEWJbIAkzm1lg/preview', '1125_1A0Blb2WjFSPnQzFEWJbIAkzm1lg', 2, 118, """AI, machine learning, and deep learning are transforming numerous industries. But building a machine learning system requires that you make practical decisions:

Should you collect more training data?
Should you use end-to-end deep learning?
How do you deal with your training set not matching your test set?
and many more.

Historically, the only way to learn how to make these "strategy" decisions has been a multi-year apprenticeship in a graduate program or company. This is a book to help you quickly gain this skill, so that you can become better at building AI systems."""),
        ('Data Science from Scratch', 'Joel Grus', 'Data Science from Scratch First Principles with Python by Joel Grus (z-lib.org).pdf', 'https://drive.google.com/thumbnail?id=1aodQ8hAqwQF7lZtstZXgh7XIOEtp_7f4', 'https://drive.google.com/file/d/1tfX8odGDylfQnc4Th7ZZhNDals-CimFq/preview', '1tfX8odGDylfQnc4Th7ZZhNDals-CimFq', 2, 330, """Data science libraries, frameworks, modules, and toolkits are great for
doing data science, but they’re also a good way to dive into the discipline
without actually understanding data science. In this book, you’ll learn how
many of the most fundamental data science tools and algorithms work by
implementing them from scratch.
If you have an aptitude for mathematics and some programming skills,
author Joel Grus will help you get comfortable with the math and statistics
at the core of data science, and with hacking skills you need to get started
as a data scientist. Today’s messy glut of data holds answers to questions
no one’s even thought to ask. This book provides you with the know-how
to dig those answers out."""),
        ('A Visual Intro to Deep Learning', 'Meor Amer', 'A Visual Intro to Deep Learning. .pdf', 'https://drive.google.com/thumbnail?id=1dOxoZWx2pNMVVs3qHN8lQ1rt9pC_f3Br', 'https://drive.google.com/file/d/1Wivg_AffEH8rZOn8tAaEOltZEA-TC_zO/preview', '1Wivg_AffEH8rZOn8tAaEOltZEA-TC_zO', 3, 42, """Deep learning is the algorithm powering the current renaissance of artificial intelligence (AI). And its progress is not showing signs of slowing down. A McKinsey report estimates that by 2030, AI will potentially deliver $13 trillion to the global economy, or 16% of the world's current GDP. This opens up exciting career opportunities in the coming decade.

But deep learning can be quite daunting to learn. With the abundance of learning resources in recent years has emerged another problem—information overload.

This book aims to compress this knowledge and make the subject approachable. By the end of this book, you will be able to build a visual intuition about deep learning and neural networks."""),
    ]
    
    for data in books:
        book = Book(
            name=data[0],
            author=data[1],
            book_name=data[2],
            cover_url=data[3],
            content_url=data[4],
            cloud_file_id=data[5],
            section_id=data[6],
            upload_date=datetime.now(),
            num_pages=data[7],
            prologue=data[8]
        )
        db.session.add(book)
    
    db.session.commit()

    print("Dummy books have been created and added to the database.")
  
with app.app_context():
    db.create_all()
    
    # search if it has a username admin, if it doesn't then create
    if User.query.filter_by(username='admin').first() is None: 
        admin_password = generate_password_hash('admin')
        test_password = generate_password_hash('asdf')
        admin = User(username='admin',email='admin@gmail.com',password=admin_password,created_date=datetime.now(),nationality='Indian',role='librarian')
        testuser = User(username='testuser',email='ts@gmail.com',password=test_password,created_date=datetime.now(),nationality='Indian',role='user')
        db.session.add(admin)
        db.session.add(testuser)
        db.session.commit()
        
        create_sections()
        create_books()
    else:
        print('Admin already exists')
        # create_sections()
        # create_books()