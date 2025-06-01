"""
Module: User Reactions Routes

This module defines the endpoints for user reactions (likes) to events in the travel journal application.
"""
from app import app
from flask import request, jsonify, session, redirect, url_for, flash
from app.config import constants
from app.utils.decorators import login_required
from app.db import db

@app.route('/api/reaction', methods=[constants.HTTP_METHOD_POST])
@login_required
def toggle_reaction():
    """Toggle a user's reaction (like/unlike, dislike/undislike) to an event.

    This endpoint handles following scenarios:
    1. If no reaction exists: Add new reaction
    2. If same reaction exists: Remove it (toggle off)
    3. If different reaction exists: Update to new reaction type

    This endpoint expects JSON data with:
    - target_type: The type of content being reacted to ('event')
    - target_id: The ID of the content
    - reaction_type: The type of reaction ('like' or 'dislike')

    Returns:
        JSON response with the new reaction count and status.
    """
    # Get the required data from the request
    data = request.json
    target_type = data.get('target_type')
    target_id = data.get('target_id')
    reaction_type = data.get('reaction_type', 'like')

    # Validate the required fields
    if not all([target_type, target_id]):
        return jsonify({
            'success': False,
            'message': 'Missing required fields'
        }), 400

    # Get the user ID from the session
    user_id = session[constants.USER_ID]

    # Check if the user has any reaction to this target
    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT reaction_id, reaction_type
            FROM user_reactions
            WHERE target_type = %s
              AND target_id = %s
              AND user_id = %s
            """,
            (target_type, target_id, user_id)
        )
        existing_reaction = cursor.fetchone()

        if existing_reaction:
            # User has an existing reaction
            existing_type = existing_reaction['reaction_type']

            if existing_type == reaction_type:
                # Same reaction type, so remove it (toggle off)
                cursor.execute(
                    """
                    DELETE
                    FROM user_reactions
                    WHERE reaction_id = %s
                    """,
                    (existing_reaction['reaction_id'],)
                )
                success_message = f'{reaction_type.capitalize()} removed'
                is_active = False
            else:
                # Different reaction type, so update it
                cursor.execute(
                    """
                    UPDATE user_reactions
                    SET reaction_type = %s
                    WHERE reaction_id = %s
                    """,
                    (reaction_type, existing_reaction['reaction_id'])
                )
                success_message = f'Changed from {existing_type} to {reaction_type}'
                is_active = True
        else:
            # User has not reacted, so add the reaction
            cursor.execute(
                """
                INSERT INTO user_reactions (target_type, target_id, user_id, reaction_type)
                VALUES (%s, %s, %s, %s)
                """,
                (target_type, target_id, user_id, reaction_type)
            )
            success_message = f'{reaction_type.capitalize()} added'
            is_active = True

        # Get the updated reaction count for the requested type
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM user_reactions
            WHERE target_type = %s
              AND target_id = %s
              AND reaction_type = %s
            """,
            (target_type, target_id, reaction_type)
        )
        count_result = cursor.fetchone()
        count = count_result['count'] if count_result else 0

        # 集成Popular Traveller成就检测
        if target_type == 'event' and reaction_type == 'like' and is_active:
            # 找到事件拥有者
            cursor.execute("SELECT j.user_id FROM events e JOIN journeys j ON e.journey_id = j.journey_id WHERE e.event_id = %s", (target_id,))
            event_owner = cursor.fetchone()
            if event_owner:
                from app.utils.achievement import AchievementUtils
                AchievementUtils.check_popular_traveller_achievement(event_owner['user_id'])

    # Return the response with the new count and status
    return jsonify({
        'success': True,
        'message': success_message,
        'count': count,
        'is_active': is_active
    })

@app.route('/api/reaction/status', methods=[constants.HTTP_METHOD_GET])
@login_required
def get_reaction_status():
    """Get the reaction status and count for a specific target.

    This endpoint expects query parameters:
    - target_type: The type of content ('event')
    - target_id: The ID of the content
    - reaction_type: The type of reaction ('like')

    Returns:
        JSON response with the reaction count and status.
    """
    # Get the required data from the query parameters
    target_type = request.args.get('target_type')
    target_id = request.args.get('target_id')
    reaction_type = request.args.get('reaction_type', 'like')

    # Validate the required fields
    if not all([target_type, target_id]):
        return jsonify({
            'success': False,
            'message': 'Missing required fields'
        }), 400

    # Get the user ID from the session
    user_id = session[constants.USER_ID]

    with db.get_cursor() as cursor:
        # Check if the user has already reacted to this target
        cursor.execute(
            """
            SELECT reaction_id 
            FROM user_reactions 
            WHERE target_type = %s AND target_id = %s AND user_id = %s AND reaction_type = %s
            """,
            (target_type, target_id, user_id, reaction_type)
        )
        is_active = cursor.fetchone() is not None

        # Get the total reaction count
        cursor.execute(
            """
            SELECT COUNT(*) as count 
            FROM user_reactions 
            WHERE target_type = %s AND target_id = %s AND reaction_type = %s
            """,
            (target_type, target_id, reaction_type)
        )
        count_result = cursor.fetchone()
        count = count_result['count'] if count_result else 0

    # Return the response with the count and status
    return jsonify({
        'success': True,
        'count': count,
        'is_active': is_active
    })