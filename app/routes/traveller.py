"""
Module: Traveller Home Route

This module defines the endpoint for the traveller homepage in the login application.
It includes role-based access control to ensure only traveller users can access this page.
Unauthorized users are either redirected or shown a 403 error.
"""
from app.config import constants
from flask import redirect, render_template, session, url_for
from app import app
# Importing decorators from the current package
from app.utils.decorators import role_required

@app.route('/traveller/home')
@role_required(constants.USER_ROLE_TRAVELLER)
def traveller_home():
     """Traveller Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current traveller, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     return render_template(constants.TEMPLATE_TRAVELLER_HOME)