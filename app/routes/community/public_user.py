"""
Module: Community Features Routes

This module defines endpoints for community features, including public user profiles
and user discovery functionality.
"""
from app.config import constants

from app import app
from flask import redirect, render_template, request, session, url_for, flash, jsonify
from app.config import constants
from app.utils.decorators import login_required
from app.db import db
from datetime import datetime, timedelta
from app.utils.helpers import user_details

@app.route('/users/public')
@login_required
def public_users():
    """Display public user listing with search functionality.

    Allows logged-in users to browse and search through public user profiles.
    """
    search_term = request.args.get('search', '').strip()

    with db.get_cursor() as cursor:
        if search_term:
            # Search by username with case-insensitive matching
            cursor.execute("""
                SELECT u.user_id, u.username, u.first_name, u.last_name, 
                       u.profile_image, u.personal_description, u.location,
                       COUNT(DISTINCT uf_followers.user_id) as follower_count,
                       COUNT(DISTINCT uf_following.followed_id) as following_count
                FROM users u
                LEFT JOIN user_follows uf_followers ON u.user_id = uf_followers.followed_id 
                    AND uf_followers.follow_type = 'user'
                LEFT JOIN user_follows uf_following ON u.user_id = uf_following.user_id 
                    AND uf_following.follow_type = 'user'
                WHERE u.is_public_profile = 1 
                AND u.status = 'active'
                AND LOWER(u.username) LIKE LOWER(%s)
                GROUP BY u.user_id
                ORDER BY u.username
            """, (f'%{search_term}%',))
        else:
            # Get all public users
            cursor.execute("""
                SELECT u.user_id,u.username,u.first_name,u.last_name,
                       u.profile_image,u.personal_description,u.location,
                       COUNT(DISTINCT uf_followers.user_id)     as follower_count,
                       COUNT(DISTINCT uf_following.followed_id) as following_count
                FROM users u
                         LEFT JOIN user_follows uf_followers ON u.user_id = uf_followers.followed_id 
                    AND uf_followers.follow_type = 'user'
                         LEFT JOIN user_follows uf_following ON u.user_id = uf_following.user_id 
                    AND uf_following.follow_type = 'user'
                WHERE u.is_public_profile = 1 
                AND u.status = 'active'
                GROUP BY u.user_id
                ORDER BY u.username
            """)

        users = cursor.fetchall()

    return render_template(constants.TEMPLATE_PUBLIC_USERS,
                          users=users,
                          search_term=search_term)


@app.route('/profile/<int:user_id>')
@login_required
def view_public_profile(user_id):
    """View a user's public profile with travel experiences and activities.

    Args:
        user_id (int): ID of the user whose profile to view
    """
    current_user_id = session[constants.USER_ID]

    with db.get_cursor() as cursor:
        # Get user basic information
        cursor.execute("""
            SELECT u.user_id,u.username,u.first_name,u.last_name,
                   u.profile_image,u.personal_description,u.location,
                   u.is_public_profile,u.role
            FROM users u
            WHERE u.user_id = %s AND u.status = 'active'
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            flash('User not found or profile is not available.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('public_users'))

        # Check if profile is public or if viewing own profile
        if not user['is_public_profile'] and user_id != current_user_id:
            flash('This profile is private.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('public_users'))

        # Get follower and following counts
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT uf_followers.user_id) as follower_count,
                COUNT(DISTINCT uf_following.followed_id) as following_count
            FROM users u
            LEFT JOIN user_follows uf_followers ON u.user_id = uf_followers.followed_id 
                AND uf_followers.follow_type = 'user'
            LEFT JOIN user_follows uf_following ON u.user_id = uf_following.user_id 
                AND uf_following.follow_type = 'user'
            WHERE u.user_id = %s
        """, (user_id,))

        follow_counts = cursor.fetchone()

        # Get recent activities (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Recent likes
        cursor.execute("""
            SELECT 'like' as activity_type, ur.created_at, 
                   CASE 
                       WHEN ur.target_type = 'event' THEN CONCAT('liked event "', e.title, '"')
                       WHEN ur.target_type = 'comment' THEN 'liked a comment'
                   END as description,
                   j.journey_id, j.title as journey_title
            FROM user_reactions ur
            LEFT JOIN events e ON ur.target_type = 'event' AND ur.target_id = e.event_id
            LEFT JOIN journeys j ON e.journey_id = j.journey_id
            WHERE ur.user_id = %s AND ur.reaction_type = 'like' 
            AND ur.created_at >= %s
            ORDER BY ur.created_at DESC
            LIMIT 10
        """, (user_id, thirty_days_ago))

        recent_likes = cursor.fetchall()

        # Recent comments
        cursor.execute("""
            SELECT 'comment'                                    as activity_type,ec.created_at,
                   CONCAT('commented on event "', e.title, '"') as description,
                   j.journey_id,j.title                         as journey_title,
                   LEFT(ec.content, 50)                         as comment_preview
            FROM event_comments ec
            JOIN events e ON ec.event_id = e.event_id
            JOIN journeys j ON e.journey_id = j.journey_id
            WHERE ec.user_id = %s AND ec.created_at >= %s
            ORDER BY ec.created_at DESC
            LIMIT 10
        """, (user_id, thirty_days_ago))

        recent_comments = cursor.fetchall()

        # Recent journey updates
        cursor.execute("""
            SELECT 'journey_update' as activity_type, j.update_date as created_at,
                   CONCAT('updated journey "', j.title, '"') as description,
                   j.journey_id, j.title as journey_title
            FROM journeys j
            WHERE j.user_id = %s AND j.update_date >= %s
            AND j.status IN ('public', 'published')
            ORDER BY j.update_date DESC
            LIMIT 10
        """, (user_id, thirty_days_ago))

        recent_journey_updates = cursor.fetchall()

        # Combine and sort recent activities
        all_activities = list(recent_likes) + list(recent_comments) + list(recent_journey_updates)
        all_activities.sort(key=lambda x: x['created_at'], reverse=True)
        recent_activities = all_activities[:15]  # Show top 15 most recent

        # Get places visited (from public journeys only)
        cursor.execute("""
            SELECT DISTINCT e.location, COUNT(*) as visit_count
            FROM events e
            JOIN journeys j ON e.journey_id = j.journey_id
            WHERE j.user_id = %s 
            AND j.status IN ('public', 'published')
            AND e.location IS NOT NULL 
            AND e.location != ''
            GROUP BY e.location
            ORDER BY visit_count DESC, e.location
            LIMIT 20
        """, (user_id,))

        places_visited = cursor.fetchall()

        # Get user achievements
        cursor.execute("""
            SELECT a.achievement_id, a.name, a.description, a.icon_url, a.is_premium_only,
                   a.condition_type, a.condition_value,
                   ua.unlocked_at, ua.is_unlocked,
                   CASE 
                       WHEN a.name = 'Location Explorer' THEN (
                           SELECT COUNT(DISTINCT location)
                           FROM events e
                           JOIN journeys j ON e.journey_id = j.journey_id
                           WHERE j.user_id = %s
                       )
                       WHEN a.name = 'Sharing Guru' THEN (
                           SELECT COUNT(*)
                           FROM journeys
                           WHERE user_id = %s AND status = 'public'
                       )
                       WHEN a.name = 'Popular Traveller' THEN (
                           SELECT COUNT(*)
                           FROM event_reactions er
                           JOIN events e ON er.event_id = e.event_id
                           JOIN journeys j ON e.journey_id = j.journey_id
                           WHERE j.user_id = %s AND er.reaction_type = 'like'
                       )
                       ELSE NULL
                   END as current_progress
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.achievement_id = ua.achievement_id AND ua.user_id = %s
            ORDER BY a.achievement_id
        """, (user_id, user_id, user_id, user_id))

        achievements = cursor.fetchall()

        # Check if current user is following this user
        is_following = False
        if user_id != current_user_id:
            cursor.execute("""
                SELECT 1 FROM user_follows 
                WHERE user_id = %s AND followed_id = %s AND follow_type = 'user'
            """, (current_user_id, user_id))
            is_following = cursor.fetchone() is not None

        # Get public journey count
        cursor.execute("""
            SELECT COUNT(*) as journey_count
            FROM journeys 
            WHERE user_id = %s AND status IN ('public', 'published')
        """, (user_id,))

        journey_count = cursor.fetchone()['journey_count']

    return render_template('community/public_profile.html',
                          user=user,
                          follow_counts=follow_counts,
                          recent_activities=recent_activities,
                          places_visited=places_visited,
                          achievements=achievements,
                          is_following=is_following,
                          journey_count=journey_count,
                          is_own_profile=(user_id == current_user_id))


@app.route('/community/settings', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def community_settings():
    """Manage community and privacy settings."""
    user_id = session[constants.USER_ID]
    profile = user_details(user_id)

    if request.method == constants.HTTP_METHOD_POST:
        is_public = request.form.get('is_public') == '1'

        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET is_public_profile = %s 
                WHERE user_id = %s
            """, (is_public, user_id))

        status = 'public' if is_public else 'private'
        flash(f'Your profile is now {status}.', constants.FLASH_MESSAGE_SUCCESS)

        return redirect(url_for('community_settings'))

    # GET request - show settings page
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT is_public_profile FROM users WHERE user_id = %s
        """, (user_id,))
        user_settings = cursor.fetchone()

    return render_template('community/settings.html',
                           user_settings=user_settings, profile = profile)
