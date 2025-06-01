# validators.py

import re
from app.db import db
from app.config import constants
from datetime import datetime

def validate_username(username):
    if len(username) > 20:
        # The user should never see this error during normal conditions,
        # because we set a maximum length of 20 on the input field in the
        # template. However, a user or attacker could easily override that
        # and submit a longer value, so we need to handle that case.
        return 'Your username cannot exceed 20 characters.'
    elif not re.match(r'[A-Za-z0-9]+', username):
        return 'Your username can only contain letters and numbers.'
    else:
        # check if the username already exists in the database and ensure the username is unique
        with db.get_cursor() as cursor:
            cursor.execute('SELECT user_id FROM users WHERE username = %s',(username,))
            username_exists = cursor.fetchone() is not None
            if username_exists:
                return 'Username already exists. Please choose a different username.'
    return ''

def validate_firstname(firstname):
    if len(firstname) > 50:
        return 'Your first name cannot exceed 50 characters.'
    elif firstname and not firstname.strip():
        # Check if the name is empty (consisting only of spaces or an empty string).
        return "First name cannot be just whitespace. Please enter a valid name."
    return ''

def validate_lastname(lastname):
    if len(lastname) > 50:
        return 'Your last name cannot exceed 50 characters.'
    elif lastname and not lastname.strip():
        # Check if the name is empty (consisting only of spaces or an empty string).
        return "Last name cannot be just whitespace. Please enter a valid name."
    return ''

    # Validate the new user's email address. Note: The regular expression
    # we use here isn't a perfect check for a valid address, but is
    # sufficient for this example.
def validate_email(email, request_url, user_id):
    if len(email) > 320:
        # As above, the user should never see this error under normal
        # conditions because we set a maximum input length in the template.
        return 'Your email address cannot exceed 320 characters.'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return 'Invalid email address.'
    # Check email uniqueness
    with db.get_cursor() as cursor:
        cursor.execute('SELECT user_id FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            existing_user_id = existing_user[constants.USER_ID]

            if request_url == constants.URL_PROFILE:
                # Allow user to keep their own email, but prevent duplicates
                if existing_user_id != int(user_id):
                    return 'Email already exists. Please choose a different email.'
            else:
                # If not updating profile, email must be unique
                return 'Email already exists. Please choose a different email.'

    return ''

def validate_location(location):
    if len(location) > 50:
        return 'Your location content cannot exceed 50 characters.'
    elif location and not location.strip():
        # Check if the location is empty (consisting only of spaces or an empty string).
        return "Location cannot be just whitespace. Please enter a valid name."
    return ''

def validate_personal_description(personal_description):
    if personal_description and not personal_description.strip():
        # Check if the location is empty (consisting only of spaces or an empty string).
        return "Personal Description cannot be just whitespace."
    return ''

    # Validate password. Think about what other constraints might be useful
    # here for security (e.g. requiring a certain mix of character types,
    # or avoiding overly-common passwords). Make sure that you clearly
    # communicate any rules to the user, either through hints on the signup
    # page or with clear error messages here.
    #
    # Note: Unlike the username and email address, we don't enforce a
    # maximum password length. Because we'll be storing a hash of the
    # password in our database, and not the password itself, it doesn't
    # matter how long a password the user chooses. Whether it's 8 or 800
    # characters, the hash will always be the same length.
def validate_password(password):
    if len(password) < 8:
        return 'Please choose a longer password!'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return 'Password must contain at least one lowercase letter.'
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one digit.'
    if not re.search(r'[\W_]', password):
        return 'Password must contain at least one special character.'
    return ''

def validate_repassword(password, repassword):
    if password != repassword:
        return 'The two entered passwords do not match.'
    return ''


def validate_journey(title, description, start_date, status=None):
    """
    Validates journey data against database constraints.

    Args:
        title (str): Journey title
        description (str): Journey description
        start_date (str): Journey start date in dd/mm/yyyy format
        status (str, optional): Journey visibility status (private/public)

    Returns:
        tuple: (is_valid, error_message)
    """
    from datetime import datetime
    errors = []

    # Validate title (VARCHAR(100))
    if not title:
        errors.append("Title is required")
    elif len(title) > 100:
        errors.append("Title must be less than 100 characters")

    # Validate description (TEXT)
    if not description:
        errors.append("Description is required")

    # Validate start_date (TIMESTAMP) with dd/mm/yyyy format
    if not start_date:
        errors.append("Start date is required")
    else:
        try:
            # Parse the date in dd/mm/yyyy format
            input_date = datetime.strptime(start_date, '%Y-%m-%d')

            # Check if date is in the future
            # if input_date > datetime.now():
            #     errors.append("Start date cannot be in the future")
        except ValueError:
            errors.append("Invalid date format. Please use DD/MM/YYYY format")

    # Validate status if provided (ENUM('private', 'public'))
    if status is not None:
        if status not in ['private', 'public']:
            errors.append("Status must be either 'private' or 'public'")

    # Return validation result
    if errors:
        return False, errors
    else:
        return True, None
    
def validate_announcement(title, content):
    errors = []

    # Validate title (VARCHAR(100))
    if not title:
        errors.append("Title is required")
    elif len(title) > 100:
        errors.append("Title must be less than 100 characters")

    # Validate content (TEXT)
    if not content:
        errors.append("Content is required")

    # Return validation result
    if errors:
        return False, errors
    else:
        return True, None