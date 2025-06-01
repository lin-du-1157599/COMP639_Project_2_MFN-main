from app.db import db

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_extension(mimetype):
    if not mimetype.startswith('image/'):
        return None

    ext = mimetype.split('/')[-1].lower()
    if ext == 'jpeg':
        return 'jpg'
    elif ext in ['png', 'gif', 'jpg']:
        return ext
    else:
        return None
    
def user_details(user_id):
    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s;', (user_id,))
        userDetails = cursor.fetchone()
        return userDetails

