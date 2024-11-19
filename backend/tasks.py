from datetime import datetime
from celery_config import celery
from model import db,Request,User,Book,Section
from app import app
from sqlalchemy import func,case
from jinja2 import Environment, FileSystemLoader

import os
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import StringIO
from datetime import datetime, timedelta

from routes.cloud_file_management import remove_email_from_file

from time import sleep
    
def send_email(to_email,subject,html_content):
    from_email='tejag311@gmail.com'
    
    msg=MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    part1 = MIMEText(html_content,'html')
    msg.attach(part1)        
        
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'tejag311@gmail.com'
    smtp_password = 'udxx qrdl fuhr skbr'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        
@celery.task
def check_expired_books():
    with app.app_context():
        requests = Request.query.filter(Request.req_status=='Approved',Request.req_is_active==True).all()
        today_date = datetime.now()
        
        for req in requests:
            held_days = (today_date - req.issued_date).days
            if held_days  >= 7:
                file_id = Book.query.get(req.req_book_id).cloud_file_id
                email_to_remove = User.query.get(req.req_user_id).email
                remove_email_from_file(file_id,email_to_remove)
                        
                req.req_is_active = False
                req.return_date = datetime.now()
                req.req_status = 'Revoked'
                
            elif held_days == 6:
                user=User.query.filter_by(id=req.req_user_id).first()
                book=Book.query.filter_by(id=req.req_book_id).first()
                subject = 'Only one more day to return the book.'
                html_content = f"""
                                <!DOCTYPE html>
                                <head>
                                    <title>Please Return the book {book.name} before Tomorrow night 11:59pm.</title>
                                </head>
                                <body>
                                    <h2>If you couldn't return it before tomorrow night, the access will be auto revoked.</h2>
                                    
                                    <p>Thank you for using our online library services!</p>
                                    <p>Best regards,</p>
                                    <p>Library Management System Team</p>
                                </body>
                                </html>
                                """
                send_email(user.email,subject,html_content)

        db.session.commit()

@celery.task
def generate_monthly_report():
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    current_date = datetime.now()
    
    last_day_prev_month = current_date - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    
    with app.app_context():
        # 1.1 Query for new users, new sections, new ebooks
        new_users = User.query.filter(User.created_date >= first_day_prev_month, User.created_date <= last_day_prev_month).count()
        new_sections = Section.query.filter(Section.created_date >= first_day_prev_month, Section.created_date <= last_day_prev_month).count()
        new_ebooks = Book.query.filter(Book.upload_date >= first_day_prev_month, Book.upload_date <= last_day_prev_month).count()
        
        # 1.2 Query for total users, total sections, total ebooks
        total_users = User.query.count()
        total_sections = Section.query.count()
        total_ebooks = Book.query.count()

        # 2. Query for most active users based on total requests, along with details of their requests.
        most_active_users = (
            db.session.query(
                    User.id.label('user_id'),
                    User.username.label('username'),
                    func.count(Request.id).label('total_requests'),
                    func.sum(case((Request.req_status == 'Declined', 1), else_=0)).label('declined_requests'),
                    func.sum(case((Request.req_status == 'Withdrawn', 1), else_=0)).label('withdrawn_requests'),
                    func.sum(case((Request.req_status == 'Approved', 1), else_=0)).label('approved_requests'),
                    func.sum(case((Request.req_status == 'Returned', 1), else_=0)).label('returned_on_time_requests'),
                    func.sum(case((Request.req_status == 'Revoked', 1), else_=0)).label('overdue_requests')
                )
                .join(Request, Request.req_user_id == User.id)
                .filter(Request.req_date >= first_day_prev_month, Request.req_date <= last_day_prev_month)
                .group_by(User.id)
                .order_by(func.count(Request.id).desc())
            ).all()

        
        # 3. Query for Popular sections
        popular_sections = (
            db.session.query(
                    Section.id.label('section_id'),
                    Section.name.label('section_name'),
                    func.count(Request.id).label('total_requests'),
                    func.sum(case((Request.req_status == 'Declined', 1), else_=0)).label('declined_requests'),
                    func.sum(case((Request.req_status == 'Withdrawn', 1), else_=0)).label('withdrawn_requests'),
                    func.sum(case((Request.req_status == 'Approved', 1), else_=0)).label('approved_requests'),
                    func.sum(case((Request.req_status == 'Returned', 1), else_=0)).label('returned_on_time_requests'),
                    func.sum(case((Request.req_status == 'Revoked', 1), else_=0)).label('overdue_requests')
                )
                .join(Book, Book.section_id == Section.id)
                .join(Request, Request.req_book_id == Book.id)
                .filter(Request.req_date >= first_day_prev_month, Request.req_date <= last_day_prev_month)
                .group_by(Section.id)
                .order_by(func.count(Request.id).desc())
            ).all()
        
        # 4. Query for popular books
        popular_books = (
            db.session.query(
                    Book.name.label('book_name'),
                    Section.name.label('section_name'),
                    func.count(Request.id).label('total_requests'),
                    func.sum(case((Request.req_status == 'Declined', 1), else_=0)).label('declined_requests'),
                    func.sum(case((Request.req_status == 'Withdrawn', 1), else_=0)).label('withdrawn_requests'),
                    func.sum(case((Request.req_status == 'Approved', 1), else_=0)).label('approved_requests'),
                    func.sum(case((Request.req_status == 'Returned', 1), else_=0)).label('returned_on_time_requests'),
                    func.sum(case((Request.req_status == 'Revoked', 1), else_=0)).label('overdue_requests')
                )
                .join(Section, Book.section_id == Section.id)
                .join(Request, Request.req_book_id == Book.id)
                .filter(Request.req_date >= first_day_prev_month, Request.req_date <= last_day_prev_month)
                .group_by(Book.id, Section.name)
                .order_by(func.count(Request.id).desc())
            ).all()

    
        # Render the HTML using Jinja2
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('report_template.html')
        html_report = template.render(
            current_month=current_date.strftime('%B'),
            current_year=current_date.year,
            new_users=new_users,
            total_users=total_users,
            new_sections=new_sections,
            total_sections=total_sections,
            new_ebooks=new_ebooks,
            total_ebooks=total_ebooks,
            most_active_users=most_active_users,
            popular_sections = popular_sections,
            popular_books = popular_books
        )
        
        # Sending mail for librarian
        librarian = User.query.filter_by(role='librarian').first()
        subject = f"""Montly Activity Report for  {current_month} {current_year}"""
        send_email(librarian.email,subject,html_report)
    
@celery.task
def export_as_csv():
    requests = db.session.query(Request, User, Book).join(User, Request.req_user_id == User.id).join(Book, Request.req_book_id == Book.id).filter(Request.req_is_active==False).all()

    requests_info = []
    for req, user, book in requests:
        requests_info.append({
            "id": req.id,
            "user_id": user.id,
            "user_name": user.username,
            "book_name": book.name,
            "req_date": req.req_date,
            "req_status": req.req_status,
            "issued_date":req.issued_date,
            "return_date":req.return_date
        })
    
    requests_info.sort(key=lambda x: x['req_date'],reverse=True)

    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["User Id", "User Name", "Book Name","Request Date", "Request Status", "Issued Date", "Return Date"])

    for req in requests_info:
        csv_writer.writerow([
            req['user_id'],
            req['user_name'],
            req['book_name'],
            str(req['req_date']),
            req['req_status'],
            str(req['issued_date']),
            str(req['return_date'])
        ])

    today_date = datetime.now()
    today_date = str(today_date).split(' ')[0]
    file_name = today_date + '_requests_report.csv'
    base_dir = os.path.abspath(os.path.dirname(__file__))
    csv_file_path = os.path.join(base_dir, f"csv_reports/{file_name}")
    with open(csv_file_path, 'w') as csv_file:
        csv_file.write(csv_buffer.getvalue())

    return csv_buffer.getvalue()
    
