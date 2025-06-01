from app import app
from flask import redirect, render_template, request, session, url_for, flash
from app.config import constants
from app.config.constants import DEFAULT_USER_ROLE, DEFAULT_STATUS
from app.utils.decorators import if_logged_in_redirect, login_required, subscription_required
from app.db import db
from flask_bcrypt import Bcrypt
from app.utils.helpers import allowed_file, get_image_extension
from werkzeug.utils import secure_filename
import re, os
from app.utils.validators import validate_firstname, validate_lastname, validate_email, validate_password, \
    validate_repassword, validate_location, validate_username, validate_personal_description
from app.utils.helpers import user_details

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

@app.route('/')
def root():
    """Root endpoint (/)
    
    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    # 查询published状态的，并且发布的用户是订阅用户的旅程
    with db.get_cursor() as cursor:
                cursor.execute('''
                            SELECT j.*
                            FROM journeys j
                            LEFT JOIN users u ON u.user_id = j.user_id 
                            WHERE j.status = %s AND u.subscription_status != %s ;
                            ''', (constants.JOURNEY_STATUS_PUBLISHED,constants.USER_SUBSCRIPTION_FREE ))
                journeys = cursor.fetchall()
    return render_template(constants.TEMPLATE_HOME, journeys=journeys)

@app.route('/home')
def home():
    # Call the user_home_url method
    return redirect(user_home_url())

def user_home_url():
    """Generates a URL to the homepage for the currently logged-in user.
    
    If the user is not logged in, or the role stored in their session cookie is
    invalid, this returns the URL for the login page instead."""
    role = session.get(constants.USER_ROLE, None)

    if role == constants.USER_ROLE_TRAVELLER:
        home_endpoint = constants.URL_TRAVELLER_HOME
    elif role == constants.USER_ROLE_EDITOR:
        home_endpoint = constants.URL_EDITOR_HOME
    elif role == constants.USER_ROLE_ADMIN:
        home_endpoint = constants.URL_ADMIN_HOME
    elif role == constants.USER_ROLE_MODERATOR:
        home_endpoint = constants.URL_MODERATOR_HOME
    else:
        home_endpoint = constants.URL_HOME

    return url_for(home_endpoint)

@app.route('/login', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@if_logged_in_redirect
def login():
    """Handles user login.
    
    This endpoint supports both GET and POST requests:
    
    - GET: Renders the login page.
    - POST: Attempts to authenticate the user using the provided username and password.
      - If authentication is successful, redirects the user to their role-specific homepage.
      - If authentication fails, re-renders the login page with appropriate error messages.

    If a user is already logged in, they are redirected to their homepage instead of seeing the login form.
    
    Returns:
        - A rendered login page (for GET requests or failed login attempts).
        - A redirection to the user's homepage upon successful login.
    """
    # Check if this is a POST request and the username & password fields exist in the request form.
    if request.method==constants.HTTP_METHOD_POST and constants.USERNAME in request.form and constants.PASSWORD in request.form:
        # Get the login details submitted by the user.
        username = request.form[constants.USERNAME]
        password = request.form[constants.PASSWORD]
        if not username or not password:
            flash("Please enter both username and password.", constants.FLASH_MESSAGE_DANGER)
            return render_template(constants.TEMPLATE_LOGIN)

        try:
            # Attempt to validate the login details against the database.
            with db.get_cursor() as cursor:
                cursor.execute('''
                            SELECT user_id, username, password_hash, subscription_end_date, role, status, subscription_status, profile_image, is_trial_used
                            FROM users
                            WHERE username = %s;
                            ''', (username,))
                account = cursor.fetchone()
                if account is not None:
                    # Banned users cannot log in.
                    if account[constants.USER_STATUS]==constants.USER_STATUS_BANNED:
                        # No matching username found in the database.
                        flash("User is banned, cannot log in", constants.FLASH_MESSAGE_DANGER)
                        return render_template(constants.TEMPLATE_LOGIN, username=username)
                    # Retrieve stored password hash from the database.
                    password_hash = account[constants.PASSWORD_HASH]
                    # Verify the provided password against the stored hash.
                    if flask_bcrypt.check_password_hash(password_hash, password):
                        # Authentication successful: store user session data.
                        session[constants.SESSION_LOGGED_IN] = True
                        session[constants.USER_ID] = account[constants.USER_ID]
                        session[constants.USERNAME] = account[constants.USERNAME]
                        session[constants.USER_ROLE] = account[constants.USER_ROLE]
                        session[constants.USER_SUBSCRIPTION_STATUS] = account[constants.USER_SUBSCRIPTION_STATUS]
                        session[constants.USER_IS_TRIAL_USED] = account[constants.USER_IS_TRIAL_USED]
                        session[constants.USER_PROFILE_IMAGE] = account[constants.USER_PROFILE_IMAGE]

                        subscription_end_date = account[constants.USER_SUBSCRIPTION_END_DATE]
                        if subscription_end_date is not None:
                            session[constants.USER_SUBSCRIPTION_END_DATE] = subscription_end_date.strftime('%d/%m/%Y')

                        return redirect(user_home_url())
                    else:
                        # Password is incorrect. Re-display the login form, keeping
                        # the username provided by the user so they don't need to re-enter it. 
                        flash("Incorrect username or password", constants.FLASH_MESSAGE_DANGER)
                        return render_template(constants.TEMPLATE_LOGIN,
                                            username=username)
                else:
                    # No matching username found in the database.
                    flash("Incorrect username or password", constants.FLASH_MESSAGE_DANGER)
                    return render_template(constants.TEMPLATE_LOGIN,username=username)
        except Exception as e:
            print(e)
            flash("An error occurred while processing your request. Please try again", constants.FLASH_MESSAGE_DANGER)

            return render_template(constants.TEMPLATE_LOGIN), constants.HTTP_STATUS_CODE_500

    # This was a GET request, or an invalid POST (no username and/or password),
    # so we just render the login form with no pre-populated details or flags.
    return render_template(constants.TEMPLATE_LOGIN)

# Default role assigned to new users upon registration.
DEFAULT_PROFILE_IMAGE = None
DEFAULT_PERSONAL_DESCRIPTION = None
DEFAULT_ROLE = 'traveller'
DEFAULT_SHAREABLE = '1'
DEFAULT_STATUS = 'active'

@app.route('/signup', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@if_logged_in_redirect
def signup():
    """Signup (registration) page endpoint.

    Methods:
    - get: Renders the signup page.
    - post: Attempts to create a new user account using the details supplied
        via the signup form, then renders the signup page again with a welcome
        message (if successful) or one or more error message(s) explaining why
        signup could not be completed.

    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """

    # if the account has already login, redirect to user's role home page
    if constants.SESSION_LOGGED_IN in session:
        return redirect(user_home_url())

    if request.method == constants.HTTP_METHOD_POST and constants.USERNAME in request.form and constants.EMAIL in request.form and constants.PASSWORD in request.form and constants.FIRST_NAME in request.form and constants.LAST_NAME in request.form and constants.LOCATION in request.form:
        # Get the details submitted via the form on the signup page, and store
        # the values in temporary local variables for ease of access.
        username = request.form[constants.USERNAME]
        email = request.form[constants.EMAIL]
        password = request.form[constants.PASSWORD]
        confirm_password = request.form[constants.FORM_FIELD_CONFIRM_PASSWORD]
        first_name = request.form[constants.FIRST_NAME]
        last_name = request.form[constants.LAST_NAME]
        location = request.form[constants.LOCATION]

        # We start by assuming that everything is okay. If we encounter any
        # errors during validation, we'll store an error message in one or more
        # of these variables so we can pass them through to the template.
        username_error = None
        email_error = None
        password_error = None
        confirm_password_error = None
        last_name_error = None
        first_name_error = None
        location_error = None

        # Validate the username, email, password and confirm password
        # to ensure they meet the constraints of our web app.
        username_error = validate_username(username)
        email_error = validate_email(email, constants.URL_SIGNUP, '')
        password_error = validate_password(password)
        confirm_password_error =  validate_repassword(password, confirm_password)
        
        # First name, last name and location are optional. If user provided, 
        # validate each of them to ensure they meet the constraints.
        if first_name:
            first_name_error = validate_firstname(first_name)
        if last_name:
            last_name_error = validate_lastname(last_name)
        if location:
            location_error = validate_location(location)

        # One or more errors were encountered, so send the user back to the
        # signup page with their username, email, first name, last name and location pre-populated.
        # For security reasons, we never send back the password they chose.
        # Error messages will also be returned to display on the form.
        if username_error or password_error or confirm_password_error or email_error or first_name_error or last_name_error or location_error:
            return render_template('signup.html',
                                   username = username,
                                   email = email,
                                   first_name = first_name,
                                   last_name = last_name,
                                   location = location,

                                   username_error = username_error,
                                   email_error = email_error,
                                   password_error = password_error,
                                   confirm_password_error = confirm_password_error,
                                   first_name_error = first_name_error,
                                   last_name_error = last_name_error,
                                   location_error = location_error,
                                   )

        else:
            # The new account details are valid. Hash the user's new password
            # and create their account in the database.
            password_hash = flask_bcrypt.generate_password_hash(password)

            with db.get_cursor() as cursor:
                cursor.execute('''
                            INSERT INTO users (username, password_hash, email, first_name, last_name, location, profile_image, personal_description, role, shareable, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                            ''',
                            (username, password_hash, email, first_name.strip() if first_name else "", last_name.strip() if last_name else "", location.strip() if location else "", DEFAULT_PROFILE_IMAGE, DEFAULT_PERSONAL_DESCRIPTION, DEFAULT_ROLE, DEFAULT_SHAREABLE, DEFAULT_STATUS,))
            
            # Registration is complete, send the user back to the signup page.
            # We set the `signup_successful` flag to display a post-signup message.
            return render_template(constants.TEMPLATE_SIGN_UP, signup_successful=True)
        
    # This was a GET request, or an invalid POST (no username, email, and/or
    # password). Render the signup page with no pre-populated form fields or
    # error messages.
    return render_template(constants.TEMPLATE_SIGN_UP)


@app.route('/profile', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def profile():
    """User Profile page endpoint.

    Methods:
    - get: Renders the user profile page for the current user.

    If the user is not logged in, requests will redirect to the login page.
    """
    if request.method == constants.HTTP_METHOD_GET:
        # Retrieve user profile from the database.
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, email, first_name, last_name, location, profile_image, role, personal_description, subscription_status, subscription_end_date, is_trial_used FROM users WHERE user_id = %s;",
                (session[constants.USER_ID],))
            profile = cursor.fetchone()
            return render_template(constants.TEMPLATE_PROFILE, profile=profile)
    elif request.method == constants.HTTP_METHOD_POST:
        user_id = request.form.get(constants.USER_ID)
        username = request.form.get(constants.USERNAME)
        email = request.form.get(constants.EMAIL)
        first_name = request.form.get(constants.FIRST_NAME)
        last_name = request.form.get(constants.LAST_NAME)
        location = request.form.get(constants.LOCATION)
        personal_description = request.form.get(constants.USER_PERSONAL_DESCRIPTION)
        email_error = validate_email(email, constants.URL_PROFILE, user_id)
        firstname_error = validate_firstname(first_name)
        lastname_error = validate_lastname(last_name)
        location_error = validate_location(location)
        personal_description_error = validate_personal_description(personal_description)

        if (email_error or firstname_error or lastname_error or location_error or personal_description_error):
            profile = {
                constants.USER_ID: user_id,
                constants.USERNAME: username,
                constants.EMAIL: email,
                constants.FIRST_NAME: first_name,
                constants.LAST_NAME: last_name,
                constants.LOCATION: location,
                constants.USER_ROLE: session.get(constants.USER_ROLE), 
                constants.USER_PERSONAL_DESCRIPTION: personal_description
            }
            return render_template(constants.TEMPLATE_PROFILE,
                                   user_id=user_id,
                                   profile=profile,
                                   email_error=email_error,
                                   firstname_error=firstname_error,
                                   lastname_error=lastname_error,
                                   location_error=location_error,
                                   personal_description_error=personal_description_error)
        else:
            with db.get_cursor() as cursor:
                cursor.execute("UPDATE users SET first_name=%s, last_name=%s, email=%s, location=%s, personal_description=%s WHERE user_id=%s;",
                               (first_name.strip() if first_name else "", last_name.strip() if last_name else "", email, location.strip() if location else "", personal_description.strip() if personal_description else "", user_id))

            # retrieve new profile details again
            with db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT user_id, username, email, first_name, last_name, location, profile_image, role, personal_description, subscription_status, is_trial_used FROM users WHERE user_id = %s;",
                    (session[constants.USER_ID],))
                profile = cursor.fetchone()

            return render_template(constants.TEMPLATE_PROFILE, profile=profile, profile_update_successful=True)


@app.route('/profile/change_password', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def change_password():
    user_id = session[constants.USER_ID]

    # Initialize error variables
    current_password_error = None
    new_password_error = None
    confirm_password_error = None

    if request.method == constants.HTTP_METHOD_POST:
        current_password = request.form.get(constants.FORM_FIELD_CURRENT_PASSWORD)
        new_password = request.form.get(constants.FORM_FIELD_NEW_PASSWORD)
        confirm_password = request.form.get(constants.FORM_FIELD_CONFIRM_PASSWORD)

        # Check if the entered current password matches the password in the database
        with db.get_cursor() as cursor:
            cursor.execute('SELECT password_hash FROM users WHERE user_id = %s;', (user_id,))
            user = cursor.fetchone()

            if not user:
                current_password_error = "User not found."
            else:
                old_hashed_password = user[constants.PASSWORD_HASH]

                # Check if the current password is correct
                if not flask_bcrypt.check_password_hash(old_hashed_password, current_password):
                    current_password_error = "Current password is incorrect."
                else:
                    # Validate new password and confirm password
                    new_password_error = validate_password(new_password)
                    confirm_password_error = validate_password(confirm_password)
                    confirm_password_error = validate_repassword(new_password, confirm_password)

                    # Check if new password is the same as the current password
                    if flask_bcrypt.check_password_hash(old_hashed_password, new_password):
                        new_password_error = 'The new password cannot be the same as the current password. Please enter a new password.'
                    if flask_bcrypt.check_password_hash(old_hashed_password, confirm_password):
                        confirm_password_error = 'The new password cannot be the same as the current password. Please enter a new password.'

        # If there are any errors, return the form with errors
        if current_password_error or new_password_error or confirm_password_error:
            return render_template(
                constants.TEMPLATE_CHANGE_PASSWORD,
                current_password=current_password,
                new_password=new_password,
                confirm_password=confirm_password,
                current_password_error=current_password_error,
                new_password_error=new_password_error,
                confirm_password_error=confirm_password_error
            )

        # If no errors, update the password
        if not (current_password_error or new_password_error or confirm_password_error):
            password_hash = flask_bcrypt.generate_password_hash(new_password)

            with db.get_cursor() as cursor:
                cursor.execute("UPDATE users SET password_hash=%s WHERE user_id=%s;", (password_hash, user_id))

            return render_template(constants.TEMPLATE_CHANGE_PASSWORD, user_id=user_id, update_successful=True)

    return render_template(constants.TEMPLATE_CHANGE_PASSWORD)

@app.route('/profile/subscription', methods=[constants.HTTP_METHOD_GET])
@login_required
def profile_subscription():
    user_id = session[constants.USER_ID]
    profile = user_details(user_id)
    return render_template(constants.TEMPLATE_PROFILE_SUBSCRIPTION, profile=profile)

@app.route('/logout')
def logout():
    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
    # Note that nothing actually happens on the server when a user logs out: we
    # just remove the cookie from their web browser. They could technically log
    # back in by manually restoring the cookie we've just deleted. In a high-
    # security web app, you may need additional protections against this (e.g.
    # keeping a record of active sessions on the server side).
    session.pop(constants.SESSION_LOGGED_IN, None)
    session.pop(constants.USER_ID, None)
    session.pop(constants.USERNAME, None)
    session.pop(constants.USER_ROLE, None)
    session.pop(constants.USER_SUBSCRIPTION_STATUS, None)
    session.pop(constants.USER_IS_TRIAL_USED, None)
    session.pop(constants.USER_SUBSCRIPTION_END_DATE, None)

    return redirect(url_for(constants.URL_ROOT))


app.config[constants.IMAGE_UPLOAD_FOLDER] = os.path.join(app.root_path, constants.IMAGE_UPLOAD_FOLDER_URL)
@app.route('/profile/upload_image', methods=[constants.HTTP_METHOD_GET,constants.HTTP_METHOD_POST])
@login_required
def upload_image():
    user_id = session.get(constants.USER_ID)
    image_error = None

    # access the image file
    if request.method == constants.HTTP_METHOD_POST:
        profile_image = request.files[constants.USER_PROFILE_IMAGE]

        # validate if the image extension is valid
        if not allowed_file(profile_image.filename):
            image_error = 'Invalid file type. Please choose an image.'

            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
                profile = cursor.fetchone()

            return render_template(constants.TEMPLATE_PROFILE, user_id = user_id, profile = profile, image_error = image_error)

        file_type = get_image_extension(profile_image.mimetype)

        profile_image_name = f"avatar_{user_id}.{file_type}"

        # save image to the folder
        profile_image_path = os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], profile_image_name)
        profile_image.save(profile_image_path)

        with db.get_cursor() as cursor:
            cursor.execute("UPDATE users SET profile_image=%s WHERE user_id = %s;",(profile_image_name, user_id))
            session[constants.USER_PROFILE_IMAGE] = profile_image_name

        return redirect(url_for(constants.URL_PROFILE))

    return render_template(constants.TEMPLATE_PROFILE, user_id = user_id)


@app.route('/profile/remove_image', methods=[constants.HTTP_METHOD_POST])
@login_required
def remove_image():
    user_id = session.get(constants.USER_ID)

    # query the user's profile image file name
    with db.get_cursor() as cursor:
        cursor.execute("SELECT profile_image FROM users WHERE user_id = %s;", (user_id,))
        profile_image = cursor.fetchone()
        profile_image = profile_image[constants.USER_PROFILE_IMAGE]

    if profile_image is not None:
        try:
            os.remove(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], profile_image))
        except FileNotFoundError:
            pass  # Ignore if file doesn't exist

        with db.get_cursor() as cursor:
            cursor.execute("UPDATE users SET profile_image = NULL WHERE user_id = %s;", (user_id,))

    return redirect(url_for(constants.URL_PROFILE))

@app.route('/user/follow', methods=[constants.HTTP_METHOD_POST])
@subscription_required
@login_required
def follow_user():
    user_id = session.get(constants.USER_ID)

    # Try get followed_id from form data or URL query
    followed_id_str = request.form.get(constants.FOLLOWED_ID) or request.args.get(constants.FOLLOWED_ID)
    try:
        followed_id = int(followed_id_str)
    except (TypeError, ValueError):
        flash("Invalid user ID.", constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('edit_user', user_id=user_id))

    # Can't follow yourself
    if user_id == followed_id:
        flash("You cannot follow yourself.", constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('edit_user', user_id=followed_id))

    with db.get_cursor() as cursor:
        # Check if followed user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (followed_id,))
        if not cursor.fetchone():
            flash("User does not exist.", constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('edit_user', user_id=user_id))

        # Check if already following
        cursor.execute("""
            SELECT 1 FROM user_follows
            WHERE user_id = %s AND followed_id = %s AND follow_type = 'user'
        """, (user_id, followed_id))
        if cursor.fetchone():
            flash("You are already following this user.", constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('edit_user', user_id=followed_id))

        # Insert follow relationship
        cursor.execute("""
            INSERT INTO user_follows (user_id, followed_id, follow_type)
            VALUES (%s, %s, 'user')
        """, (user_id, followed_id))

    flash("You are now following this user.", constants.FLASH_MESSAGE_SUCCESS)
    return redirect(url_for('edit_user', user_id=followed_id))

@app.route('/user/unfollow', methods=[constants.HTTP_METHOD_GET])
@subscription_required
@login_required
def unfollow_user():
    user_id = session.get(constants.USER_ID)
    followed_id = request.args.get(constants.FOLLOWED_ID)

    # Can't unfollow yourself
    if str(user_id) == str(followed_id):
        flash("You cannot unfollow yourself.", constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('edit_user', user_id=followed_id))

    with db.get_cursor() as cursor:
        # Delete only if follow_type is 'user'
        cursor.execute(
            "DELETE FROM user_follows WHERE user_id = %s AND followed_id = %s AND follow_type = 'user';",
            (user_id, followed_id)
        )

    return redirect(url_for('edit_user', user_id=followed_id))