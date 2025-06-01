"""
Module: Private Messages Routes

This module handles private messaging functionality including sending, receiving,
and viewing messages between users with subscription-based restrictions.
"""
from app import app
from flask import redirect, render_template, request, session, url_for, flash, jsonify
from app.config import constants
from app.utils.decorators import login_required
from app.db import db


@app.route('/messages')
@login_required
def messages_inbox():
    """Display user's message inbox with conversation list"""
    user_id = session[constants.USER_ID]

    with db.get_cursor() as cursor:
        # Alternative approach for MySQL 5.7 compatibility
        # First get all conversation partners
        cursor.execute("""
                       SELECT DISTINCT CASE
                                           WHEN pm.sender_id = %s THEN pm.receiver_id
                                           ELSE pm.sender_id
                                           END as other_user_id
                       FROM private_messages pm
                       WHERE pm.sender_id = %s
                          OR pm.receiver_id = %s
                       """, (user_id, user_id, user_id))

        conversation_partners = cursor.fetchall()
        conversations = []

        # For each partner, get their details and latest message
        for partner in conversation_partners:
            other_user_id = partner['other_user_id']

            # Get user details
            cursor.execute("""
                           SELECT user_id, username, first_name, last_name, profile_image
                           FROM users
                           WHERE user_id = %s
                           """, (other_user_id,))
            user_info = cursor.fetchone()

            # Get latest message in conversation
            cursor.execute("""
                           SELECT content, sent_at
                           FROM private_messages
                           WHERE (sender_id = %s AND receiver_id = %s)
                              OR (sender_id = %s AND receiver_id = %s)
                           ORDER BY sent_at DESC
                           LIMIT 1
                           """, (user_id, other_user_id, other_user_id, user_id))
            latest_message = cursor.fetchone()

            # Get unread count
            cursor.execute("""
                           SELECT COUNT(*) as unread_count
                           FROM private_messages
                           WHERE sender_id = %s
                             AND receiver_id = %s
                             AND is_read = 0
                           """, (other_user_id, user_id))
            unread_result = cursor.fetchone()

            if user_info and latest_message:
                conversation = {
                    'other_user_id': other_user_id,
                    'username': user_info['username'],
                    'first_name': user_info['first_name'],
                    'last_name': user_info['last_name'],
                    'profile_image': user_info['profile_image'],
                    'last_message': latest_message['content'],
                    'last_message_time': latest_message['sent_at'],
                    'unread_count': unread_result['unread_count'] if unread_result else 0
                }
                conversations.append(conversation)

        # Sort by latest message time
        conversations.sort(key=lambda x: x['last_message_time'], reverse=True)

    return render_template('messages/inbox.html', conversations=conversations)


@app.route('/messages/<int:other_user_id>')
@login_required
def view_conversation(other_user_id):
    """Display conversation with specific user"""
    user_id = session[constants.USER_ID]
    user_subscription_status = session.get(constants.USER_SUBSCRIPTION_STATUS, 'Free')
    user_role = session.get(constants.USER_ROLE, 'traveller')

    # Check if user can send messages (premium subscribers and staff)
    can_send_messages = (user_subscription_status != 'Free' or
                         user_role in ['editor', 'admin', 'moderator'])

    with db.get_cursor() as cursor:
        # Get other user info
        cursor.execute("""
                       SELECT user_id, username, first_name, last_name, profile_image
                       FROM users
                       WHERE user_id = %s
                         AND status = 'active'
                       """, (other_user_id,))
        other_user = cursor.fetchone()

        if not other_user:
            flash('User not found', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('messages_inbox'))

        # Get conversation messages
        cursor.execute("""
                       SELECT pm.message_id,
                              pm.sender_id,
                              pm.receiver_id,
                              pm.content,
                              pm.sent_at,
                              u.username,
                              u.profile_image
                       FROM private_messages pm
                                JOIN users u ON pm.sender_id = u.user_id
                       WHERE (pm.sender_id = %s AND pm.receiver_id = %s)
                          OR (pm.sender_id = %s AND pm.receiver_id = %s)
                       ORDER BY pm.sent_at ASC
                       """, (user_id, other_user_id, other_user_id, user_id))

        messages = cursor.fetchall()

        # Mark messages as read for current user
        cursor.execute("""
                       UPDATE private_messages
                       SET is_read = 1
                       WHERE sender_id = %s
                         AND receiver_id = %s
                         AND is_read = 0
                       """, (other_user_id, user_id))

    return render_template('messages/conversation.html',
                           other_user=other_user,
                           messages=messages,
                           can_send_messages=can_send_messages)


@app.route('/messages/<int:other_user_id>/send', methods=['POST'])
@login_required
def send_message(other_user_id):
    """Send a private message to another user"""
    user_id = session[constants.USER_ID]
    user_subscription_status = session.get(constants.USER_SUBSCRIPTION_STATUS, 'Free')
    user_role = session.get(constants.USER_ROLE, 'traveller')

    # Check if user can send messages
    if user_subscription_status == 'Free' and user_role not in ['editor', 'admin', 'moderator']:
        flash('You need a premium subscription to send messages', constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('view_conversation', other_user_id=other_user_id))

    content = request.form.get('content', '').strip()

    if not content:
        flash('Message cannot be empty', constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('view_conversation', other_user_id=other_user_id))

    if len(content) > 1000:  # Message length limit
        flash('Message is too long (maximum 1000 characters)', constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('view_conversation', other_user_id=other_user_id))

    with db.get_cursor() as cursor:
        # Verify receiver exists and is active
        cursor.execute("""
                       SELECT user_id
                       FROM users
                       WHERE user_id = %s
                         AND status = 'active'
                       """, (other_user_id,))

        if not cursor.fetchone():
            flash('Recipient not found', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('messages_inbox'))

        # Insert message
        cursor.execute("""
                       INSERT INTO private_messages (sender_id, receiver_id, content)
                       VALUES (%s, %s, %s)
                       """, (user_id, other_user_id, content))

    flash('Message sent successfully', constants.FLASH_MESSAGE_SUCCESS)
    return redirect(url_for('view_conversation', other_user_id=other_user_id))


@app.route('/api/messages/unread_count')
@login_required
def get_unread_count():
    """API endpoint to get unread message count for notifications"""
    user_id = session[constants.USER_ID]

    with db.get_cursor() as cursor:
        cursor.execute("""
                       SELECT COUNT(*) as unread_count
                       FROM private_messages
                       WHERE receiver_id = %s
                         AND is_read = 0
                       """, (user_id,))

        result = cursor.fetchone()
        unread_count = result['unread_count'] if result else 0

    return jsonify({'unread_count': unread_count})


@app.route('/api/users/search')
@login_required
def search_users():
    """API endpoint to search for users to start new conversations"""
    query = request.args.get('q', '').strip()
    current_user_id = session[constants.USER_ID]

    if not query or len(query) < 2:
        return jsonify({'users': []})

    with db.get_cursor() as cursor:
        # Search users by username, first name, or last name
        # Exclude current user and banned users
        cursor.execute("""
                       SELECT user_id, username, first_name, last_name, profile_image
                       FROM users
                       WHERE user_id != %s
                         AND status = 'active'
                         AND (
                           username LIKE %s
                               OR first_name LIKE %s
                               OR last_name LIKE %s
                               OR CONCAT(first_name, ' ', last_name) LIKE %s
                           )
                       ORDER BY username
                       LIMIT 10
                       """, (current_user_id, f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))

        users = cursor.fetchall()

        # Convert to list of dictionaries for JSON response
        user_list = []
        for user in users:
            user_dict = {
                'user_id': user['user_id'],
                'username': user['username'],
                'first_name': user['first_name'] or '',
                'last_name': user['last_name'] or '',
                'profile_image': user['profile_image'],
                'display_name': f"{user['first_name']} {user['last_name']}".strip() if user['first_name'] or user[
                    'last_name'] else user['username']
            }
            user_list.append(user_dict)

    return jsonify({'users': user_list})


@app.route('/messages/compose', methods=['POST'])
@login_required
def compose_message():
    """Send a new message to a user (can be first message or continuation)"""
    user_id = session[constants.USER_ID]
    user_subscription_status = session.get(constants.USER_SUBSCRIPTION_STATUS, 'Free')
    user_role = session.get(constants.USER_ROLE, 'traveller')

    # Check if user can send messages
    if user_subscription_status == 'Free' and user_role not in ['editor', 'admin', 'moderator']:
        return jsonify({'success': False, 'error': 'Premium subscription required to send messages'})

    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content', '').strip()

    if not recipient_id:
        return jsonify({'success': False, 'error': 'Recipient is required'})

    if not content:
        return jsonify({'success': False, 'error': 'Message cannot be empty'})

    if len(content) > 1000:
        return jsonify({'success': False, 'error': 'Message is too long (maximum 1000 characters)'})

    try:
        recipient_id = int(recipient_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid recipient'})

    if recipient_id == user_id:
        return jsonify({'success': False, 'error': 'You cannot send messages to yourself'})

    with db.get_cursor() as cursor:
        # Verify recipient exists and is active
        cursor.execute("""
                       SELECT user_id, username
                       FROM users
                       WHERE user_id = %s
                         AND status = 'active'
                       """, (recipient_id,))

        recipient = cursor.fetchone()
        if not recipient:
            return jsonify({'success': False, 'error': 'Recipient not found or inactive'})

        # Insert message
        cursor.execute("""
                       INSERT INTO private_messages (sender_id, receiver_id, content)
                       VALUES (%s, %s, %s)
                       """, (user_id, recipient_id, content))

    return jsonify({
        'success': True,
        'message': f'Message sent to @{recipient["username"]}',
        'redirect_url': url_for('view_conversation', other_user_id=recipient_id)
    })


@app.route('/api/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete a message (only for the recipient or sender)"""
    user_id = session[constants.USER_ID]

    with db.get_cursor() as cursor:
        # Get message details
        cursor.execute("""
                       SELECT message_id, sender_id, receiver_id, content
                       FROM private_messages
                       WHERE message_id = %s
                       """, (message_id,))

        message = cursor.fetchone()

        if not message:
            return jsonify({'success': False, 'error': 'Message not found'})

        # Check if user has permission to delete this message
        # Users can delete messages they sent OR received
        if user_id not in [message['sender_id'], message['receiver_id']]:
            return jsonify({'success': False, 'error': 'You do not have permission to delete this message'})

        # Delete the message
        cursor.execute("""
                       DELETE
                       FROM private_messages
                       WHERE message_id = %s
                       """, (message_id,))

    return jsonify({'success': True, 'message': 'Message deleted successfully'})


@app.route('/messages/start/<int:user_id>')
@login_required
def start_conversation(user_id):
    """Start a new conversation with a user (redirect to conversation view)"""
    current_user_id = session[constants.USER_ID]

    if current_user_id == user_id:
        flash('You cannot send messages to yourself', constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('messages_inbox'))

    return redirect(url_for('view_conversation', other_user_id=user_id))