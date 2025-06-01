"""
Module: Comments Routes

This module defines the endpoints for comments on events.
"""
from app import app
from flask import jsonify, request, session, redirect, url_for, flash
from app.config import constants
from app.utils.decorators import login_required
from app.db import db
from app.utils.achievement import AchievementUtils
from datetime import datetime


@app.route('/api/comments/<int:event_id>', methods=[constants.HTTP_METHOD_GET])
def get_event_comments(event_id):
    """Get all comments for a specific event.

    Args:
        event_id (int): The ID of the event to get comments for.
    """
    with db.get_cursor() as cursor:
        # Check if event exists
        cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()
        if not event:
            return jsonify({'success': False, 'message': 'Event not found'}), 404

        # Get all comments for this event that are not hidden
        cursor.execute("""
                       SELECT c.comment_id,
                              c.content,
                              c.created_at,
                              c.user_id,
                              c.is_hidden,
                              u.username,
                              u.profile_image
                       FROM event_comments c
                                JOIN users u ON c.user_id = u.user_id
                       WHERE c.event_id = %s
                         AND c.is_hidden = 0
                       ORDER BY c.created_at DESC
                       """, (event_id,))
        comments = cursor.fetchall()

        # Get reaction counts for each comment
        comment_reactions = {}
        if comments:
            comment_ids = [comment['comment_id'] for comment in comments]
            placeholders = ', '.join(['%s'] * len(comment_ids))
            cursor.execute(f"""
                SELECT target_id, reaction_type, COUNT(*) as count
                FROM user_reactions
                WHERE target_type = 'comment' AND target_id IN ({placeholders})
                GROUP BY target_id, reaction_type
            """, comment_ids)

            for row in cursor.fetchall():
                if row['target_id'] not in comment_reactions:
                    comment_reactions[row['target_id']] = {'like': 0, 'dislike': 0}
                comment_reactions[row['target_id']][row['reaction_type']] = row['count']

        # Get user's reactions to these comments if logged in
        user_reactions = {}
        if 'user_id' in session:
            user_id = session['user_id']
            if comments:
                cursor.execute(f"""
                    SELECT target_id, reaction_type
                    FROM user_reactions
                    WHERE target_type = 'comment' AND target_id IN ({placeholders}) AND user_id = %s
                """, comment_ids + [user_id])

                for row in cursor.fetchall():
                    user_reactions[row['target_id']] = row['reaction_type']

    # Format the comments for the response
    formatted_comments = []
    for comment in comments:
        comment_id = comment['comment_id']
        formatted_comments.append({
            'id': comment_id,
            'content': comment['content'],
            'created_at': comment['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': comment['user_id'],
            'username': comment['username'],
            'profile_image': comment['profile_image'],
            'reactions': comment_reactions.get(comment_id, {'like': 0, 'dislike': 0}),
            'user_reaction': user_reactions.get(comment_id)
        })

    return jsonify({
        'success': True,
        'event_id': event_id,
        'comments': formatted_comments
    })


@app.route('/api/comments', methods=[constants.HTTP_METHOD_POST])
@login_required
def add_comment():
    """Add a new comment to an event.

    JSON payload should include:
    - event_id: ID of the event to comment on
    - content: Text content of the comment
    """
    data = request.json
    event_id = data.get('event_id')
    content = data.get('content')
    user_id = session[constants.USER_ID]

    # Validate inputs
    if not all([event_id, content]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Check if content is too long (500 characters limit)
    if len(content) > 500:
        return jsonify({'success': False, 'message': 'Comment is too long (maximum 500 characters)'}), 400

    # Check if event exists
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()
        if not event:
            return jsonify({'success': False, 'message': 'Event not found'}), 404

    # Insert the comment
    with db.get_cursor() as cursor:
        cursor.execute("""
                       INSERT INTO event_comments (event_id, user_id, content, created_at)
                       VALUES (%s, %s, %s, %s)
                       """, (event_id, user_id, content, datetime.now()))

        # Get the inserted comment ID
        comment_id = cursor.lastrowid

        # Check for First Comment achievement
        if AchievementUtils.check_first_comment_achievement(user_id):
            achievement = AchievementUtils.get_achievement_notification('First Comment')
            if achievement:
                flash(f'Congratulations! You earned the {achievement["name"]} achievement!', constants.FLASH_MESSAGE_SUCCESS)

    # Get the comment details to return
    with db.get_cursor() as cursor:
        cursor.execute("""
                       SELECT c.comment_id,
                              c.content,
                              c.created_at,
                              c.user_id,
                              u.username,
                              u.profile_image
                       FROM event_comments c
                                JOIN users u ON c.user_id = u.user_id
                       WHERE c.comment_id = %s
                       """, (comment_id,))
        comment = cursor.fetchone()

    # Format the comment for the response
    formatted_comment = {
        'id': comment['comment_id'],
        'content': comment['content'],
        'created_at': comment['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': comment['user_id'],
        'username': comment['username'],
        'profile_image': comment['profile_image'],
        'reactions': {'like': 0, 'dislike': 0},
        'user_reaction': None
    }

    return jsonify({
        'success': True,
        'comment': formatted_comment
    })


@app.route('/api/comments/<int:comment_id>', methods=[constants.HTTP_METHOD_DELETE])
@login_required
def delete_comment(comment_id):
    """Delete a comment.

    Only the comment author or admin/editor can delete a comment.

    Args:
        comment_id (int): The ID of the comment to delete.
    """
    user_id = session[constants.USER_ID]
    user_role = session.get(constants.USER_ROLE)

    # Check if comment exists and if user has permission to delete it
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM event_comments WHERE comment_id = %s", (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({'success': False, 'message': 'Comment not found'}), 404

        # Check if user is the comment author or has admin/editor role
        if comment['user_id'] != user_id and user_role not in ['admin', 'editor', 'moderator']:
            return jsonify({'success': False, 'message': 'Permission denied'}), 403

    # Delete the comment
    with db.get_cursor() as cursor:
        # First delete any reactions to this comment
        cursor.execute("DELETE FROM user_reactions WHERE target_type = 'comment' AND target_id = %s", (comment_id,))

        # Then delete the comment itself
        cursor.execute("DELETE FROM event_comments WHERE comment_id = %s", (comment_id,))

    return jsonify({
        'success': True,
        'message': 'Comment deleted successfully'
    })


@app.route('/api/comments/<int:comment_id>/report', methods=[constants.HTTP_METHOD_POST])
@login_required
def report_comment(comment_id):
    """Report a comment as abusive, offensive, or spam.

    JSON payload should include:
    - reason: 'abusive', 'offensive', or 'spam'

    Args:
        comment_id (int): The ID of the comment to report.
    """
    data = request.json
    reason = data.get('reason')
    user_id = session[constants.USER_ID]

    # Validate inputs
    if not reason:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    if reason not in ['abusive', 'offensive', 'spam']:
        return jsonify({'success': False, 'message': 'Invalid reason'}), 400

    # Check if comment exists
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM event_comments WHERE comment_id = %s", (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({'success': False, 'message': 'Comment not found'}), 404

    # Check if user has already reported this comment
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM comment_reports WHERE comment_id = %s AND reported_by = %s",
            (comment_id, user_id)
        )
        existing_report = cursor.fetchone()

        if existing_report:
            return jsonify({'success': False, 'message': 'You have already reported this comment'}), 400

    # Insert the report
    with db.get_cursor() as cursor:
        cursor.execute("""
                       INSERT INTO comment_reports (comment_id, reported_by, reason, report_time)
                       VALUES (%s, %s, %s, %s)
                       """, (comment_id, user_id, reason, datetime.now()))

    return jsonify({
        'success': True,
        'message': 'Comment reported successfully'
    })