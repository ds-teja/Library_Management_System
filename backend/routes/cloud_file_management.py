from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import os
'''
    Functions in this file
    1) initialize_google_service
    2) upload_cover
    3) upload_file
    4) delete_file
    5) add_email_to_file
    6) remove_email_from_file
'''         
def initialize_google_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)
    
    service = build('drive', 'v3', credentials=creds)
    return service 

def upload_cover(cover): 
    service = initialize_google_service()
    
    COVER_UPLOAD_FOLDER = 'cover_uploads'
    
    # Save cover image to local storage
    cover_path = os.path.join(COVER_UPLOAD_FOLDER, cover.filename)
    cover.save(cover_path)
    
    # Upload cover image to Google Drive
    COVER_FOLDER_ID='1tl-bO0-n4RMtzMFEH14qUTHSeEqg8tqS'
    cover_file_metadata = {
        'name': cover.filename,
        'parents': [COVER_FOLDER_ID]
    }
    cover_media = MediaFileUpload(cover_path, resumable=True)
    cover_upload_file = service.files().create(
        body=cover_file_metadata,
        media_body=cover_media,
        fields='id'
    ).execute()
    
    cover_id = cover_upload_file.get('id')
    cover_url = f'https://drive.google.com/thumbnail?id={cover_id}'
    
    return cover_url

def upload_file(file,section_name):
    service = initialize_google_service()
    
    BASE_UPLOAD_FOLDER = 'file_uploads'  
    section_folder_path = os.path.join(BASE_UPLOAD_FOLDER, section_name)
    if not os.path.exists(section_folder_path):
        os.makedirs(section_folder_path)
    
    file_path = os.path.join(section_folder_path, file.filename)
    file.save(file_path)
    
    
    # Check if section folder exists on Google Drive, if not, create it
    folder_id = None
    PARENT_FOLDER_ID = "1zCd5vs2oI5f_yf4r2pVFkOiaMUOnsjei"
    query = f"name='{section_name}' and mimeType='application/vnd.google-apps.folder' and '{PARENT_FOLDER_ID}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        folder_id = items[0]['id']
    else:
        file_metadata = {
            'name': section_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [PARENT_FOLDER_ID]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
    
    # Upload content file to Google Drive
    file_metadata = {
        'name': file.filename,
        'copyRequiresWriterPermission': True,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    upload_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    file_id = upload_file.get("id")
    
    # Ensure file is private by removing any public permissions
    permissions = service.permissions().list(fileId=file_id).execute()
    for permission in permissions.get('permissions', []):
        if permission['type'] == 'anyone':
            service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()
    
    content_url = upload_file.get("webViewLink")
    content_url = content_url.split('/view')[0] + '/preview'
    
    return file_id,content_url

def delete_file(file_id):
    service = initialize_google_service()
    service.files().delete(fileId=file_id).execute()
        
def add_email_to_file(file_id,email_to_add):
    service = initialize_google_service()
    user_permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email_to_add
    }
    service.permissions().create(
        fileId=file_id,
        body=user_permission,
        fields='id'
    ).execute()

def remove_email_from_file(file_id,email_to_remove):
    service = initialize_google_service()
    permissions = service.permissions().list(fileId=file_id, fields='permissions(id, emailAddress)').execute()
    for permission in permissions.get('permissions', []):
        if permission.get('emailAddress') == email_to_remove:
            service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()