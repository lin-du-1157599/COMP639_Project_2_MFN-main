"""
Module: Admin Home Route

This module defines the endpoint for the admin homepage in the login application.
It includes role-based access control to ensure only admin users can access this page.
Unauthorized users are either redirected or shown a 403 error.
"""
from app.config import constants
from app import app
from flask import request, redirect, render_template, session, url_for, flash
from app.db import db
from app.routes.user import login
# Importing decorators from the current package
from app.utils.decorators import role_required, login_required


@app.route('/admin/home')
@role_required(constants.USER_ROLE_ADMIN)
def admin_home():
     """Admin Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current admin user, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     return render_template(constants.TEMPLATE_ADMIN_HOME)


@app.route('/users')
def all_users():
     return users(view_type = constants.VIEW_TYPE_ALL)


@app.route('/users/staff')
def system_users():
     return users(view_type = constants.VIEW_TYPE_STAFF)


@app.route('/users/restricted')
def restricted_users():     
     return users(view_type = constants.VIEW_TYPE_RESTRICTED)


@login_required
@role_required(constants.USER_ROLE_ADMIN)
def users(view_type = constants.VIEW_TYPE_ALL):
    # Retrieve the selected fields from the users table
    # and sort the result by username, last name, and first name
    # for displaying user lists clearly across different queries.
     select_fields = "user_id, username, email, first_name, last_name, role, shareable, status, subscription_status"
     order_by = "ORDER BY username, last_name, first_name"

     # Using if/else to determine which query to execute
     # based on the selected user type
     if view_type == constants.VIEW_TYPE_RESTRICTED:
          sqlStr = f"SELECT {select_fields} FROM users WHERE shareable = 0 {order_by};"
     elif view_type == constants.VIEW_TYPE_STAFF:
          sqlStr = f"SELECT {select_fields} FROM users WHERE role IN ('editor', 'admin') {order_by};"
     elif view_type == constants.VIEW_TYPE_ALL:
          sqlStr = f"SELECT {select_fields} FROM users {order_by};"

     with db.get_cursor() as cursor:
          cursor.execute(sqlStr)
          userslist = cursor.fetchall()
          return render_template(constants.TEMPLATE_USER, userslist = userslist, view_type = view_type)


@app.route('/users/search_all_users', methods=[constants.HTTP_METHOD_GET])
@role_required(constants.USER_ROLE_ADMIN)
def search_all_users():
    return search_users(view_type = constants.VIEW_TYPE_ALL)


@app.route('/users/search_staff_users', methods=[constants.HTTP_METHOD_GET])
@role_required(constants.USER_ROLE_ADMIN)
def search_staff_users():
    return search_users(view_type = constants.VIEW_TYPE_STAFF)


@app.route('/users/search_restricted_users', methods=[constants.HTTP_METHOD_GET])
@role_required(constants.USER_ROLE_ADMIN)
def search_restricted_users():
    return search_users(view_type = constants.VIEW_TYPE_RESTRICTED)

def search_users(view_type = constants.VIEW_TYPE_ALL):
     searchterm = request.args.get(constants.SEARCH_TERM)
     sqlsearch = f'%{searchterm}%'
     searchcat = request.args.get(constants.SEARCH_CATEGORY)

     if view_type == constants.VIEW_TYPE_RESTRICTED:
          role_condition = "AND shareable = 0"
     elif view_type == constants.VIEW_TYPE_STAFF:
          role_condition = "AND role IN ('editor', 'admin')"
     else:
          role_condition = ""
          
     with db.get_cursor() as cursor:
          if searchcat == constants.USERNAME:
            cursor.execute(
                f"SELECT username, first_name, last_name, email, role, shareable, status, user_id FROM users WHERE username LIKE %s {role_condition} ORDER BY username, last_name, first_name;",
                (sqlsearch,))
          elif searchcat == constants.LAST_NAME:
               cursor.execute(
                    f"SELECT username, first_name, last_name, email, role, shareable, status, user_id FROM users WHERE last_name LIKE %s {role_condition} ORDER BY username, last_name, first_name;",
                    (sqlsearch,))
          elif searchcat == constants.FIRST_NAME:
            cursor.execute(
                f"SELECT username, first_name, last_name, email, role, shareable, status, user_id FROM users WHERE first_name LIKE %s {role_condition} ORDER BY username, last_name, first_name;",
                (sqlsearch,))
          elif searchcat == constants.USER_FULL_NAME:
               cursor.execute(
                    f"SELECT username, first_name, last_name, email, role, shareable, status, user_id FROM users WHERE CONCAT(first_name, ' ', last_name) LIKE %s {role_condition} ORDER BY username, last_name, first_name;",
                    (sqlsearch,))
          elif searchcat == constants.EMAIL:
            cursor.execute(
                f"SELECT username, first_name, last_name, email, role, shareable, status, user_id FROM users WHERE email LIKE %s {role_condition} ORDER BY username, last_name, first_name;",
                (sqlsearch,))

          userslist = cursor.fetchall()
          return render_template(constants.TEMPLATE_USER, userslist=userslist, view_type=view_type, keyword=searchterm, searchType=searchcat)


@app.route('/users/edit', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
@role_required(constants.USER_ROLE_ADMIN)
def edit_user():
     if request.method == constants.HTTP_METHOD_GET:
          user_id = request.args.get(constants.USER_ID)

          if not user_id:
              flash("User ID is required.", "danger")
              return redirect(url_for('home'))

          with db.get_cursor() as cursor:
              cursor.execute("""
                             SELECT username,
                                    user_id,
                                    email,
                                    first_name,
                                    last_name,
                                    role,
                                    status,
                                    location,
                                    personal_description,
                                    profile_image
                             FROM users
                             WHERE user_id = %s;
                             """, (user_id,))
              user = cursor.fetchone()

          if not user:
              flash("User not found.", constants.FLASH_MESSAGE_DANGER)
              return redirect(url_for('home'))

          user = {key: (value if value is not None else '') for key, value in user.items()}

          current_user_id = session['user_id']

          is_following = None
          # myself = False
          if str(current_user_id) != str(user_id):
              with db.get_cursor() as cursor:
                  cursor.execute("""
                                 SELECT EXISTS(SELECT 1
                                               FROM user_follows
                                               WHERE user_id = %s
                                                 AND followed_id = %s
                                                 AND follow_type = 'user') AS is_following_user;
                                 """, (current_user_id, user_id))

                  result = cursor.fetchone()
                  is_following = bool(result['is_following_user'])

          return render_template(
              constants.TEMPLATE_USER_EDIT,
              user=user,
              user_id=user_id,
              is_following=is_following
          )
     elif request.method == constants.HTTP_METHOD_POST:
          user_id = request.form.get(constants.USER_ID)
          role = request.form.get(constants.USER_ROLE)
          status = request.form.get(constants.USER_STATUS)

          with db.get_cursor() as cursor:
               cursor.execute("UPDATE users SET role=%s, status=%s WHERE user_id=%s;", (role, status, user_id,))

          with db.get_cursor() as cursor:
               cursor.execute(
                    "SELECT username, email, first_name, last_name, role, status FROM users WHERE user_id = %s;",
                    (user_id,))
               user = cursor.fetchone()

          return render_template(constants.TEMPLATE_USER_EDIT, user=user, user_id=user_id, profile_update_successful=True)


@app.route('/users/update', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
@role_required(constants.USER_ROLE_ADMIN)
def update_user_status():
     user_id = request.form.get(constants.USER_ID)
     user_new_role = request.form.get(constants.USER_ROLE)
     user_new_status = request.form.get(constants.USER_STATUS)
     user_new_shareable = request.form.get(constants.USER_SHAREABLE)

     with db.get_cursor() as cursor:
          cursor.execute("UPDATE users SET role=%s, status=%s, shareable=%s WHERE user_id=%s;",
                         (user_new_role, user_new_status, user_new_shareable, user_id,))
     return redirect(url_for('edit_user', user_id=user_id))