"""
Module: Announcement Routes

This module defines the endpoints for announcement management in the travel journal application.
It includes functionality for adding and viewing announcements
"""

from app import app
from app.config import constants
from app.db import db
from app.utils.decorators import login_required, role_required
from flask import request, redirect, render_template, session, url_for, flash

from app.utils.validators import validate_announcement


@app.route('/announcements', methods=[constants.HTTP_METHOD_GET])
@login_required
def announcements_list():
    """
    Show all announcements related to the current user, including their own, those sent to them, and public ones.
    """
    user_role = session[constants.USER_ROLE]
    user_id = session[constants.USER_ID]

    import re
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM announcements 
            WHERE (user_id = %s OR recipient_id = %s OR recipient_id IS NULL)
            ORDER BY created_time DESC
        """, (user_id, user_id))
        announcementsList = cursor.fetchall()
        # If the announcement is about an achievement, pull out the achievement name for display
        for ann in announcementsList:
            if ann['title'] == 'Achievement Unlocked':
                match = re.search(r"'([^']+)' achievement", ann['content'])
                ann['achievement_name'] = match.group(1) if match else None
            else:
                ann['achievement_name'] = None
        return render_template(constants.TEMPLATE_ANNOUNCEMENTS, announcementsList=announcementsList, user_role=user_role)

@app.route('/announcements/view/<int:announcement_id>', methods=[constants.HTTP_METHOD_GET])
@login_required
def announcements_detail(announcement_id):
    """
    Show the details for a single announcement.
    """
    with db.get_cursor() as cursor:
        cursor.execute("""
                       SELECT * FROM announcements
                       WHERE announcement_id = %s
                       """, (announcement_id,))
        announcement = cursor.fetchone()

        return render_template(constants.TEMPLATE_VIEW_ANNOUNCEMENTS, announcement = announcement)

@app.route('/announcements/add', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@role_required(constants.USER_ROLE_ADMIN)
def add_announcement():
    """
    Create a new announcement. Only admins can access this route.
    """
    user_id = session[constants.USER_ID]
    if request.method == constants.HTTP_METHOD_GET:
        return render_template(constants.TEMPLATE_ADD_ANNOUNCEMENT)
    print (request.form)
    
    title = request.form[constants.TITLE]
    content = request.form[constants.CONTENT]

    # Validate announcement form fields
    is_valid, errors = validate_announcement(title, content)
    
    if not is_valid:
        for error in errors:
            flash(error, constants.FLASH_MESSAGE_DANGER)
        return render_template(constants.TEMPLATE_ADD_ANNOUNCEMENT, title = title, content = content)

    with db.get_cursor() as cursor:
        cursor.execute("""
                       INSERT INTO announcements (user_id, title, content)
                       VALUES(%s, %s, %s)
                       """,
                       (user_id, title, content)
                    )
    flash ('Announcement created successfully!', constants.FLASH_MESSAGE_SUCCESS)
    return redirect(url_for(constants.URL_ANNOUNCEMENTS))
