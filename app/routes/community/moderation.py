"""
Module: Moderation Routes

This module defines the endpoints for moderating reported comments.
"""
from app import app
from flask import render_template, redirect, request, session, url_for, flash, jsonify
from app.config import constants
from app.utils.decorators import login_required, login_and_role_required, role_required
from app.db import db
from datetime import datetime


@app.route('/moderator/home')
@role_required(constants.USER_ROLE_MODERATOR)
def moderator_home():
    """Moderator Homepage endpoint.

    Methods:
    - get: Renders the homepage for the current moderator user, or an "Access
         Denied" 403: Forbidden page if the current user has a different role.

    If the user is not logged in, requests will redirect to the login page.
    """
    return render_template(constants.TEMPLATE_MODERATOR_HOME)


@app.route('/moderation/reported_comments')
@login_and_role_required([constants.USER_ROLE_MODERATOR, constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN])
def reported_comments():
    """View all reported comments."""
    with db.get_cursor() as cursor:
        cursor.execute("""
                       SELECT r.report_id,
                              r.comment_id,
                              r.reported_by,
                              r.reason,
                              r.report_time,
                              r.reviewed_by,
                              r.review_action,
                              r.reviewed_at,
                              c.content,
                              c.event_id,
                              c.user_id    as comment_author_id,
                              c.created_at as comment_created_at,
                              u1.username  as reporter_username,
                              u2.username  as author_username,
                              u3.username  as reviewer_username,
                              e.title      as event_title
                       FROM comment_reports r
                                JOIN event_comments c ON r.comment_id = c.comment_id
                                JOIN users u1 ON r.reported_by = u1.user_id
                                JOIN users u2 ON c.user_id = u2.user_id
                                LEFT JOIN users u3 ON r.reviewed_by = u3.user_id
                                JOIN events e ON c.event_id = e.event_id
                       ORDER BY r.report_time DESC
                       """)
        reported_comments = cursor.fetchall()

    return render_template('moderation/reported_comments.html',
                           reported_comments=reported_comments)


@app.route('/api/moderation/review_comment', methods=[constants.HTTP_METHOD_POST])
@login_and_role_required([constants.USER_ROLE_MODERATOR, constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN])
def review_comment():
    """Review a reported comment.

    JSON payload should include:
    - report_id: ID of the report
    - action: 'keep', 'hidden', or 'escalated'
    """
    data = request.json
    report_id = data.get('report_id')
    action = data.get('action')
    user_id = session[constants.USER_ID]
    user_role = session.get(constants.USER_ROLE)

    # Validate inputs
    if not all([report_id, action]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Validate action based on user role
    valid_actions = ['keep', 'hidden']
    if user_role == constants.USER_ROLE_MODERATOR:
        valid_actions.append('escalated')
    elif user_role in [constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN]:
        # Editors and admins cannot escalate (they are the escalation target)
        pass

    if action not in valid_actions:
        return jsonify({'success': False, 'message': 'Invalid action for your role'}), 400

    # Check if a report exists and is not yet reviewed
    with db.get_cursor() as cursor:
        cursor.execute("""
                       SELECT r.*, c.comment_id
                       FROM comment_reports r
                                JOIN event_comments c ON r.comment_id = c.comment_id
                       WHERE r.report_id = %s
                       """, (report_id,))
        report = cursor.fetchone()

        if not report:
            return jsonify({'success': False, 'message': 'Report not found'}), 404

        if report['review_action']:
            return jsonify({'success': False, 'message': 'Report already reviewed'}), 400

    # Update the report with the review action
    with db.get_cursor() as cursor:
        cursor.execute("""
                       UPDATE comment_reports
                       SET review_action = %s,
                           reviewed_by   = %s,
                           reviewed_at   = %s
                       WHERE report_id = %s
                       """, (action, user_id, datetime.now(), report_id))

        # Handle different actions
        if action == 'hidden':
            # Hide the comment from public view
            cursor.execute("""
                           UPDATE event_comments
                           SET is_hidden = 1
                           WHERE comment_id = %s
                           """, (report['comment_id'],))

        elif action == 'escalated':
            # Create notifications for all admin users
            cursor.execute("""
                           INSERT INTO announcements (user_id, title, content, level, recipient_id)
                           SELECT %s, 
                                  'Comment Escalated for Review', 
                                  CONCAT('A comment has been escalated by moderator ', 
                                         (SELECT username FROM users WHERE user_id = %s), 
                                         ' for admin review. Report ID: ', %s, 
                                         '. Please review the reported comment and take appropriate action.'),
                                  'high', 
                                  u.user_id
                           FROM users u 
                           WHERE u.role = 'admin'
                           """, (user_id, user_id, report_id))

    # Return appropriate success message based on action
    if action == 'keep':
        message = 'Comment has been kept visible'
    elif action == 'hidden':
        message = 'Comment has been hidden from public view'
    elif action == 'escalated':
        message = 'Comment has been escalated to administrators. They have been notified.'

    return jsonify({
        'success': True,
        'message': message
    })