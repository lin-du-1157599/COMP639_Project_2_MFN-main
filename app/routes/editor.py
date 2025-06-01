"""
Module: Editor Home Route

This module defines the endpoint for the editor homepage in the login application.
It includes role-based access control to ensure only editor users can access this page.
Unauthorized users are either redirected or shown a 403 error.
"""
from app.config import constants
from app import app
from flask import redirect, render_template, session, url_for
# Importing decorators from the current package
from app.utils.decorators import role_required

@app.route('/editor/home')
@role_required(constants.USER_ROLE_EDITOR)
def editor_home():
     """Editor Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current editor user, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     return render_template(constants.TEMPLATE_EDITOR_HOME)