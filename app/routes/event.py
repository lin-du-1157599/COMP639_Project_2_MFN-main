"""
Module: Event Management Routes

This module defines the endpoints for event management in the travel journal application.
It includes functionality for adding, editing, deleting, and viewing events.
"""
from app import app
from flask import redirect, render_template, request, session, url_for, flash
from app.config import constants
from app.utils.decorators import login_required, role_required, login_and_role_required
from app.db import db
from app.utils.helpers import allowed_file
from app.utils.achievement import AchievementUtils
from werkzeug.utils import secure_filename
import os
from datetime import datetime

@app.route('/journey/<int:journey_id>/events')
@login_required
def view_events(journey_id):
    """View all events for a specific journey.
    
    Args:
        journey_id (int): The ID of the journey to view events for.
    """
    with db.get_cursor() as cursor:
        # Get journey details
        cursor.execute("""
            SELECT j.*, u.username 
            FROM journeys j 
            JOIN users u ON j.user_id = u.user_id 
            WHERE j.journey_id = %s
        """, (journey_id,))
        journey = cursor.fetchone()
        
        if not journey:
            flash('Journey not found', 'error')
            return redirect(url_for('traveller_home'))
            
        # Get all events for this journey
        cursor.execute("""
            SELECT * FROM events 
            WHERE journey_id = %s 
            ORDER BY start_time ASC
        """, (journey_id,))
        events = cursor.fetchall()
        
    return render_template('event/events.html', journey=journey, events=events)


@app.route('/journey/<int:journey_id>/event/add', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def add_event(journey_id):
    """Add a new event to a journey.

    Args:
        journey_id (int): The ID of the journey to add the event to.
    """
    user_id = session[constants.USER_ID]

    # Get journey and location data needed for both GET and POST methods
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT j.*, u.username 
            FROM journeys j 
            JOIN users u ON j.user_id = u.user_id 
            WHERE j.journey_id = %s
        """, (journey_id,))
        journey = cursor.fetchone()

        if not journey:
            flash('Journey not found', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('traveller_home'))

        cursor.execute("""
                       SELECT *
                       FROM locations
                       """)
        locations = cursor.fetchall()

        if request.method == constants.HTTP_METHOD_GET:
            return render_template('event/add_event.html', journey=journey, user_id=user_id, locations=locations)

        elif request.method == constants.HTTP_METHOD_POST:
            form_data = {
                'title': request.form.get('title', ''),
                'description': request.form.get('description', ''),
                'start_time': request.form.get('start_time', ''),
                'end_time': request.form.get('end_time', ''),
                'location_name': request.form.get('location_name', ''),
                'latitude': request.form.get('latitude', ''),
                'longitude': request.form.get('longitude', '')
            }

            if not form_data['title'] or not form_data['start_time'] or not form_data['location_name']:
                flash('Title, start time, and location are required', constants.FLASH_MESSAGE_DANGER)
                return render_template('event/add_event.html', journey=journey, user_id=user_id, form_data=form_data)

            cursor.execute("""
                SELECT start_date FROM journeys
                WHERE journey_id = %s
            """, (journey_id,))
            journey_data = cursor.fetchone()

            if not journey_data:
                flash('Journey not found', constants.FLASH_MESSAGE_DANGER)
                return redirect(url_for('traveller_home'))

            event_start_dt = datetime.strptime(form_data['start_time'], '%Y-%m-%dT%H:%M')
            journey_start_dt = journey_data['start_date']

            if event_start_dt < journey_start_dt:
                flash('Event start time cannot be earlier than journey start date', constants.FLASH_MESSAGE_DANGER)
                return render_template('event/add_event.html', journey=journey, user_id=user_id, form_data=form_data)

            if form_data['end_time'] and form_data['end_time'].strip():
                start_dt = event_start_dt
                end_dt = datetime.strptime(form_data['end_time'], '%Y-%m-%dT%H:%M')
                if end_dt <= start_dt:
                    flash('End time must be after start time', constants.FLASH_MESSAGE_DANGER)
                    return render_template('event/add_event.html', journey=journey, user_id=user_id, form_data=form_data)
            else:
                form_data['end_time'] = None
            
            # Handle multiple image uploads
            uploaded_filenames = []
            if 'event_images' in request.files:
                files = request.files.getlist('event_images')  # Get list of uploaded files
                for file in files:
                    if file and file.filename:
                        if allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            save_path = os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], filename)
                            file.save(save_path)
                            uploaded_filenames.append(filename)
                        else:
                            flash(f'Invalid file type for {file.filename}. Only JPG, PNG, GIF allowed.', constants.FLASH_MESSAGE_DANGER)
                            return render_template('event/add_event.html',
                                                journey=journey,
                                                user_id=user_id,
                                                form_data=form_data)

            # Get or insert location and retrieve location_id
            cursor.execute("""
                SELECT location_id FROM locations
                WHERE name = %s AND latitude = %s AND longitude = %s
            """, (form_data['location_name'], form_data['latitude'], form_data['longitude']))
            result = cursor.fetchone()

            if result:
                location_id = result['location_id']
            else:
                cursor.execute("""
                    INSERT INTO locations (name, latitude, longitude)
                    VALUES (%s, %s, %s)
                """, (form_data['location_name'], form_data['latitude'], form_data['longitude']))
                location_id = cursor.lastrowid

            # Insert event into database
            cursor.execute("""
                INSERT INTO events (journey_id, title, description, start_time, end_time, location, location_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (journey_id, form_data['title'], form_data['description'],
                  form_data['start_time'], form_data['end_time'], form_data['location_name'], location_id))
            event_id = cursor.lastrowid 
            
            # Insert each uploaded image
            for filename in uploaded_filenames:
                cursor.execute("""
                    INSERT INTO event_images (event_id, image_path)
                    VALUES (%s, %s)
                """, (event_id, filename))

            # Check for Event Creator achievement
            if AchievementUtils.check_event_creator_achievement(user_id):
                achievement = AchievementUtils.get_achievement_notification('Event Creator')
                if achievement:
                    flash(f'Congratulations! You earned the {achievement["name"]} achievement!', 'success')
            # Check for Location Explorer achievement (5 unique locations)
            AchievementUtils.check_location_explorer_achievement(user_id)
            # Check for Long Voyager achievement (journey > 30 days)
            AchievementUtils.check_long_voyager_achievement(user_id, journey_id)

            # Update the `update_date` of a journey
            cursor.execute("""
                UPDATE journeys SET update_date = CURRENT_TIMESTAMP WHERE journey_id = %s
            """, (journey_id,))

            flash('Event added successfully', constants.FLASH_MESSAGE_SUCCESS)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=constants.MODE_ALL))


@app.route('/event/<int:event_id>/edit', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def edit_event(event_id):
    """Edit an existing event.

    Args:
        event_id (int): The ID of the event to edit.
    """

    if request.method == constants.HTTP_METHOD_GET:
        journey_id = request.args.get(constants.JOURNEY_ID)
        mode = request.args.get(constants.REQUEST_MODE)

        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT e.*, GROUP_CONCAT(ei.image_path) AS image_paths, j.journey_id, j.title as journey_title, u.username,
                       l.latitude, l.longitude, l.location_id
                FROM events e
                JOIN journeys j ON e.journey_id = j.journey_id
                JOIN users u ON j.user_id = u.user_id
                LEFT JOIN locations l ON e.location_id = l.location_id
                LEFT JOIN event_images ei ON e.event_id = ei.event_id
                WHERE e.event_id = %s
                GROUP BY e.event_id
            """, (event_id,))
            event = cursor.fetchone()
            if not event:
                flash('Event not found', constants.FLASH_MESSAGE_DANGER)
                return redirect(url_for('traveller_home'))
            if event['image_paths']:
                event['image_paths'] = event['image_paths'].split(',') if event['image_paths'] else []

            cursor.execute("""
                           SELECT *
                           FROM locations
                           """)
            locations = cursor.fetchall()

        return render_template('event/edit_event.html', event=event, journey_id=journey_id, mode=mode, locations=locations)

    elif request.method == constants.HTTP_METHOD_POST:
        form_data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'start_time': request.form.get('start_time', ''),
            'end_time': request.form.get('end_time', ''),
            'location_name': request.form.get('location_name', ''),
            'latitude': request.form.get('latitude', ''),
            'longitude': request.form.get('longitude', ''),
            'journey_id': request.form.get(constants.JOURNEY_ID),
            'mode': request.form.get('mode', constants.MODE_ALL),
            'remove_image': request.form.get('remove_image') == 'on'
        }

        if not form_data['title'] or not form_data['start_time'] or not form_data['location_name']:
            flash('Title, start time, and location are required', constants.FLASH_MESSAGE_DANGER)
            return redirect(request.url)

        try:
            event_start_dt = datetime.strptime(form_data['start_time'], '%Y-%m-%dT%H:%M')
            if form_data['end_time']:
                end_dt = datetime.strptime(form_data['end_time'], '%Y-%m-%dT%H:%M')
                if end_dt <= event_start_dt:
                    flash('End time must be after start time', constants.FLASH_MESSAGE_DANGER)
                    return redirect(request.url)
            else:
                form_data['end_time'] = None
        except ValueError:
            flash('Invalid date format', constants.FLASH_MESSAGE_DANGER)
            return redirect(request.url)

        with db.get_cursor() as cursor:
            cursor.execute("SELECT start_date FROM journeys WHERE journey_id = %s", (form_data['journey_id'],))
            journey_data = cursor.fetchone()

            if not journey_data:
                flash('Journey not found', constants.FLASH_MESSAGE_DANGER)
                return redirect(url_for('traveller_home'))

            journey_start_dt = journey_data['start_date']
            if event_start_dt < journey_start_dt:
                flash('Event start time cannot be earlier than journey start date', constants.FLASH_MESSAGE_DANGER)
                return redirect(request.url)

        # Get or insert location and retrieve location_id
        # with db.get_cursor() as cursor:
        #     # cursor.execute("""
        #     #     SELECT location_id FROM locations
        #     #     WHERE name = %s AND latitude = %s AND longitude = %s
        #     # """, (form_data['location_name'], form_data['latitude'], form_data['longitude']))
        #     # result = cursor.fetchone()

        #     if result:
        #         location_id = result['location_id']
        #     else:
        #         cursor.execute("""
        #             INSERT INTO locations (name, latitude, longitude)
        #             VALUES (%s, %s, %s)
        #         """, (form_data['location_name'], form_data['latitude'], form_data['longitude']))
        #         location_id = cursor.lastrowid

        # Handle image upload
        event_image = None
        if 'event_image' in request.files:
            file = request.files['event_image']
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], filename))
                    event_image = filename
                else:
                    flash('Invalid file type. Please upload a JPG, PNG, or GIF.', constants.FLASH_MESSAGE_DANGER)
                    return redirect(request.url)

        # Remove old image if requested
        with db.get_cursor() as cursor:
            cursor.execute("SELECT event_image FROM events WHERE event_id = %s", (event_id,))
            current_image = cursor.fetchone()['event_image']

        if form_data['remove_image'] and current_image:
            try:
                os.remove(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], current_image))
            except:
                pass
            event_image = None
        elif not event_image:
            event_image = current_image

        # Update the event
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE events
                SET title = %s, description = %s, start_time = %s, end_time = %s,
                    location = %s,  event_image = %s
                WHERE event_id = %s
            """, (form_data['title'], form_data['description'], form_data['start_time'],
                  form_data['end_time'], form_data['location_name'], event_image, event_id))

        # Update journey update timestamp
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE journeys SET update_date = CURRENT_TIMESTAMP WHERE journey_id = %s
            """, (form_data['journey_id'],))

        flash('Event updated successfully', constants.FLASH_MESSAGE_SUCCESS)
        return redirect(url_for('view_journey', journey_id=form_data['journey_id'], mode=form_data['mode']))

@app.route('/journey/<int:journey_id>/event/<int:event_id>/delete', methods=[constants.HTTP_METHOD_GET])
@login_required
def delete_event(journey_id, event_id, mode='all'):
    """Delete an event from a journey.

    Args:
        journey_id (int): The ID of the journey containing the event.
        event_id (int): The ID of the event to delete.
        mode (str): The mode to return to after deletion (all or public).

    Returns:
        A redirect to the journey view page.
    """
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE, 'all')

    # Verify the event exists and belongs to the specified journey
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT e.*, j.user_id as journey_owner_id 
            FROM events e
            JOIN journeys j ON e.journey_id = j.journey_id
            WHERE e.event_id = %s AND j.journey_id = %s
        """, (event_id, journey_id))
        event = cursor.fetchone()

        if not event:
            flash('Event not found', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Check permission - only journey owner or admin/editor for public journeys can delete events
        if user_id != event['journey_owner_id'] and session['role'] not in ['editor', 'admin']:
            flash('You do not have permission to delete this event.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

    # Since we're handling the confirmation in the modal, we go straight to deletion
    with db.get_cursor() as cursor:
        # Get event image before deletion
        cursor.execute("SELECT event_image FROM events WHERE event_id = %s", (event_id,))
        result = cursor.fetchone()

        if result and result['event_image']:
            event_image = result['event_image']

            # Check if this image is used by any other events
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM events 
                WHERE event_image = %s AND event_id != %s
            """, (event_image, event_id))

            image_usage = cursor.fetchone()

            # Only delete the image if it's not used by any other events
            if image_usage['count'] == 0:
                try:
                    os.remove(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], event_image))
                except FileNotFoundError:
                    pass  # Ignore if file doesn't exist

        # Delete event from database
        cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        # Update the `update_date` of a journey
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE journeys SET update_date = CURRENT_TIMESTAMP WHERE journey_id = %s
            """, (journey_id,))

    flash('Event deleted successfully', constants.FLASH_MESSAGE_SUCCESS)
    return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

@app.route('/event/location', methods=[constants.HTTP_METHOD_POST])
@login_and_role_required([constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN])
def edit_event_location():
    """
    Edit the location of an event within public-shared journey.
    """
    # Get event ID from query parameters
    event_id = request.args.get('event_id')
    if not event_id:
        flash('Event ID is required.', constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('public_journeys'))

    # Get location from form
    new_location = request.form.get('location', '')

    # Get event details and check if journey is public
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT e.*, j.status, j.journey_id 
            FROM events e
            JOIN journeys j ON e.journey_id = j.journey_id
            WHERE e.event_id = %s
        """, (event_id,))
        event = cursor.fetchone()

        if not event:
            flash('Event not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('public_journeys'))

        # Check if journey is public
        if event['status'] != 'public':
            flash('You can only edit locations in publicly shared journeys.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('public_journeys'))

        # Update the location
        cursor.execute("UPDATE events SET location = %s WHERE event_id = %s", (new_location, event_id))

    flash('Location updated successfully!', constants.FLASH_MESSAGE_SUCCESS)
    return redirect(url_for('view_journey', journey_id=event['journey_id']))