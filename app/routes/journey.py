from app import app
from flask import redirect, render_template, request, session, url_for, flash, jsonify
from app.config import constants
from app.utils.decorators import login_required, login_and_role_required, subscription_required
from app.utils.sidebar import user_profile_sidebar
from app.utils.achievement import AchievementUtils
from app.utils.helpers import user_details

from app.db import db
from app.utils.validators import validate_journey
from datetime import datetime
import re, os
from markupsafe import Markup
from rapidfuzz import fuzz
from app.utils.helpers import allowed_file
from werkzeug.utils import secure_filename

@app.route('/myjourney', methods=[constants.HTTP_METHOD_GET])
@login_required
def myjourney():
    # session[constants.USER_ID] = account[constants.USER_ID]
    user_id = session[constants.USER_ID]
    profile = user_details(user_id)

    # if personal_descprition is None, set it to empty string
    if profile[constants.USER_PERSONAL_DESCRIPTION] is None:
        profile[constants.USER_PERSONAL_DESCRIPTION] = ''

    with db.get_cursor() as cursor:
        cursor.execute('''
                       SELECT journey_id, title, description, status, is_hidden, start_date, update_date, cover_image
                       FROM journeys
                       WHERE user_id = %s
                       ORDER BY start_date DESC;''',
                       (user_id,))
        journeyList = cursor.fetchall()
    return render_template(constants.TEMPLATE_MYJOURNEY, journeyList = journeyList, user_id = user_id, profile = profile)


@app.route('/journey/add', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def add_journey():
    user_id = session[constants.USER_ID]

    # Retrieve if user are allowed to public shared journeys
    with db.get_cursor() as cursor:
        cursor.execute("SELECT shareable FROM users WHERE user_id = %s;", (user_id,))
        shareableResult = cursor.fetchone()
    
    shareable = shareableResult['shareable']

    if request.method == constants.HTTP_METHOD_GET:
        return render_template(constants.TEMPLATE_ADD_JOURNEY, shareable = shareable)
    print (request.form)
    
    title = request.form[constants.TITLE]
    description = request.form[constants.DESCRIPTION]
    start_date = request.form[constants.START_DATE]
    status = request.form.get(constants.STATUS)

    if status is None:
        status = constants.JOURNEY_STATUS_PRIVATE

    # Restricted if the user are allowed to share journey
    if shareable == 0:
        status = constants.JOURNEY_STATUS_PRIVATE

    # Validate journey data
    is_valid, errors = validate_journey(title, description, start_date, status)

    if not is_valid:
        # Flash validation errors and return to form
        for error in errors:
            flash(error, constants.FLASH_MESSAGE_DANGER)
        return render_template(constants.TEMPLATE_ADD_JOURNEY,
                               title=title,
                               description=description,
                               start_date=start_date,
                               status=status,
                               shareable=shareable)

    # Handle image upload if provided
    file = request.files['cover_image']
    if session.get('subscription_status') in ['Trial', 'Premium'] or session.get('role') in ['editor', 'admin', 'moderator']:
        cover_image = None
        if 'cover_image' in request.files:
            if file and file.filename:  # Check if a file was actually selected
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], filename))
                    cover_image = filename
                else:
                    flash('Invalid file type. Please upload a JPG, PNG, or GIF.', constants.FLASH_MESSAGE_DANGER)
                    # Re-render the form with submitted data instead of redirecting
                    return render_template(constants.TEMPLATE_ADD_JOURNEY, 
                                title=title,
                               description=description,
                               start_date=start_date,
                               status=status,
                               shareable=shareable)
    elif file:
        flash("You are not allowed to upload a cover image.", "danger")
        return render_template(constants.TEMPLATE_ADD_JOURNEY, 
                                title=title,
                               description=description,
                               start_date=start_date,
                               status=status,
                               shareable=shareable)
    
    with db.get_cursor() as cursor:
        cursor.execute('''
                        INSERT INTO journeys (user_id, title, description, start_date, status, cover_image)
                        VALUES(%s, %s, %s, %s, %s, %s)
                        ''',
                        (user_id, title, description, start_date, status, cover_image)
                        )
        
        # Check for "First Journey" achievement
        if AchievementUtils.check_first_journey_achievement(user_id):
            achievement = AchievementUtils.get_achievement_notification('Journey Beginner')
            if achievement:
                flash(f'Congratulations! You earned the {achievement["name"]} achievement!', constants.FLASH_MESSAGE_SUCCESS)

        # Check for "First Share" achievement
        if status == 'public':
            if AchievementUtils.check_first_share_achievement(user_id):
                achievement = AchievementUtils.get_achievement_notification('First Share')
                if achievement:
                    flash(f'Congratulations! You earned the {achievement["name"]} achievement!', constants.FLASH_MESSAGE_SUCCESS)

    flash('Journey created successfully!', constants.FLASH_MESSAGE_SUCCESS)
    return redirect(url_for(constants.URL_MYJOURNEY))
    
@app.route('/journey/edit', methods=[constants.HTTP_METHOD_GET, constants.HTTP_METHOD_POST])
@login_required
def edit_journey():
    user_id = session[constants.USER_ID]
    user_role = session.get(constants.USER_ROLE)
    
    if request.method == constants.HTTP_METHOD_GET:
        journey_id = request.args.get(constants.JOURNEY_ID)
        mode = request.args.get(constants.REQUEST_MODE)
        with db.get_cursor() as cursor:
            cursor.execute("SELECT title, description, start_date, status, is_hidden, cover_image FROM journeys WHERE journey_id=%s;", (journey_id,))
            journey = cursor.fetchone()

        # Check if the user is the owner of the journey.
        # If not, it will be denied to access and redirect
        # to my journey page with error message. Ensure the
        # journey only visible edit page for the owner
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT j.user_id, u.shareable
                FROM journeys j
                JOIN users u ON j.user_id = u.user_id
                WHERE journey_id = %s""",
                (journey_id,))
            journey_owner = cursor.fetchone()
            shareable = journey_owner['shareable']
            print('journey_owner: ', journey_owner)

        if mode == (constants.MODE_ALL and user_id != journey_owner['user_id']) or (mode == constants.MODE_PUBLIC and session[constants.USER_ROLE]==constants.USER_ROLE_TRAVELLER):
            flash('You do not have permission to edit this journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_MYJOURNEY))

        return render_template(constants.TEMPLATE_EDIT_JOURNEY, journey_id = journey_id, mode = mode, journey = journey, user_role = user_role, shareable = shareable)

    elif request.method == constants.HTTP_METHOD_POST:

        # Retrieve the d
        # Get the details submitted via the form on the signup page, and store
        # the values in temporary local variables for ease of access.
        journey_id = request.form[constants.JOURNEY_ID]
        title = request.form[constants.TITLE]
        description = request.form[constants.DESCRIPTION]
        start_date = request.form[constants.START_DATE]
        status = request.form[constants.STATUS]
        is_hidden = request.form[constants.IS_HIDDEN]
        mode = request.form[constants.REQUEST_MODE]
        remove_image = request.form.get('remove_image') == 'on'

        with db.get_cursor() as cursor:
            cursor.execute("SELECT cover_image FROM journeys WHERE journey_id=%s;", (journey_id,))
            journey = cursor.fetchone()

        # Validate input data
        is_valid, errors = validate_journey(title, description, start_date, status)
        if not is_valid:
            # Flash validation errors and return to form
            for error in errors:
                flash(error, constants.FLASH_MESSAGE_DANGER)
            return render_template(constants.TEMPLATE_EDIT_JOURNEY,
                                   journey_id=journey_id,
                                   journey={'title': title, 'description': description, 'start_date': start_date,
                                            'status': status, 'is_hidden': is_hidden},
                                   user_role = user_role)

        # When a journey is marked as hidden by ediotr/aadmin,
        # its status will also be set to 'private'
        if is_hidden == '1':
            status = 'private'
        
        # Handle image upload if provided
        cover_image = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:  # Check if a file was actually selected
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], filename))
                    cover_image = filename

                    # Delete old image if replacing
                    if journey['cover_image']:
                        try:
                            os.remove(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], journey['cover_image']))
                        except:
                            pass  # Ignore errors if file doesn't exist
                else:
                    flash('Invalid file type. Please upload a JPG, PNG, or GIF.', constants.FLASH_MESSAGE_DANGER)
                    return render_template(constants.TEMPLATE_EDIT_JOURNEY,
                                   journey_id=journey_id,
                                   journey={'title': title, 'description': description, 'start_date': start_date,
                                            'status': status, 'is_hidden': is_hidden},
                                   user_role = user_role)

        # Handle image removal
        if remove_image and journey['cover_image']:
            try:
                os.remove(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], journey['cover_image']))
            except:
                pass  # Ignore errors if file doesn't exist

        image_value = journey['cover_image']
        if cover_image:
            image_value = cover_image
        elif remove_image:
            image_value = None

        # Update journey with validated data
        with db.get_cursor() as cursor:
            # Include status in the update if it was provided
            if status:
                cursor.execute("""
                    UPDATE journeys 
                    SET title=%s, description=%s, start_date=%s, status=%s, is_hidden=%s, cover_image=%s 
                    WHERE journey_id=%s;
                    """,
                    (title, description, start_date, status, is_hidden, image_value, journey_id))
            else:
                cursor.execute("""
                                      UPDATE journeys 
                                      SET title=%s, description=%s, start_date=%s, cover_image=%s
                                      WHERE journey_id=%s;
                                      """,
                               (title, description, start_date, image_value, journey_id))

        flash('Journey updated successfully.', constants.FLASH_MESSAGE_SUCCESS)
    
        redirect_url = url_for(constants.URL_MYJOURNEY) if mode == constants.MODE_ALL else url_for(constants.URL_PUBLIC_JOURNEY)

        return redirect(redirect_url)

@app.route('/journey/<int:journey_id>/delete', methods=[constants.HTTP_METHOD_GET])
@login_required
def delete_journey(journey_id):
    """Delete a journey and all its associated events and images.

    Args:
        journey_id (int): The ID of the journey to delete.

    Returns:
        A redirect to the user's journey list page.
    """
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE)

    # Check if the journey exists
    with db.get_cursor() as cursor:
        cursor.execute("SELECT journey_id, title FROM journeys WHERE journey_id=%s;", (journey_id,))
        journey = cursor.fetchone()

        if not journey:
            flash('Journey not found', 'error')
            return redirect(url_for(constants.URL_MYJOURNEY))

        # Check if the user is the owner of the journey or an admin
        cursor.execute("SELECT user_id FROM journeys WHERE journey_id=%s;", (journey_id,))
        journey_owner = cursor.fetchone()

        # Only allow the owner to delete the journey
        if user_id != journey_owner['user_id'] and session['role'] != 'admin':
            flash('You do not have permission to delete this journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_MYJOURNEY))

    # Since we're handling the confirmation in the modal, go straight to deletion
    with db.get_cursor() as cursor:
        # Get all event images from this journey
        cursor.execute("SELECT event_id, event_image FROM events WHERE journey_id = %s", (journey_id,))
        journey_events = cursor.fetchall()

        # For each event's image, check if it's used elsewhere before deleting
        for event in journey_events:
            if event['event_image']:
                # Check if the image is used by any other events
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM events 
                    WHERE event_image = %s AND event_id != %s
                """, (event['event_image'], event['event_id']))

                result = cursor.fetchone()

                # Only delete if this is the only event using this image
                if result['count'] == 0:
                    try:
                        os.remove(os.path.join(app.config[constants.IMAGE_UPLOAD_FOLDER], event['event_image']))
                    except FileNotFoundError:
                        pass  # Ignore if file doesn't exist

        # Delete the journey (cascades to events due to foreign key constraint)
        cursor.execute("DELETE FROM journeys WHERE journey_id = %s", (journey_id,))

    flash('Journey has been deleted successfully', constants.FLASH_MESSAGE_SUCCESS)

    # Redirect based on mode
    if mode == 'public':
        return redirect(url_for('public_journeys'))
    else:
        return redirect(url_for(constants.URL_MYJOURNEY))
    
@app.route('/journeys/public', methods=[constants.HTTP_METHOD_GET])
@login_required
def public_journeys():
    # Query to get all public journeys ordered by most recently updated
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT j.journey_id, j.title, j.description, j.update_date, j.user_id, 
                   u.username, u.first_name, u.last_name
            FROM journeys j
            JOIN users u ON j.user_id = u.user_id
            WHERE j.status = 'public' AND j.is_hidden = 0
            ORDER BY j.update_date DESC
        """)
        public_journeys = cursor.fetchall()

    return render_template(constants.TEMPLATE_PUBLIC_JOURNEY, journeyList=public_journeys)


@app.route('/journey/view/<int:journey_id>', methods=[constants.HTTP_METHOD_GET])
@login_required
def view_journey(journey_id):
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE)
    user_role = session[constants.USER_ROLE]

    with db.get_cursor() as cursor:
        # Get journey details
        cursor.execute("""
            SELECT j.*, u.username, u.first_name, u.last_name, u.profile_image,
                   MIN(e.start_time) as journey_start,
                   EXISTS(
                     SELECT 1
                     FROM user_follows uf
                     WHERE uf.user_id = %s
                       AND uf.followed_id = j.journey_id
                       AND uf.follow_type = 'journey'
                   ) AS is_following
            FROM journeys j
            JOIN users u ON j.user_id = u.user_id
            LEFT JOIN events e ON j.journey_id = e.journey_id
            WHERE j.journey_id = %s
            GROUP BY j.journey_id
        """, (user_id, journey_id))
        journey = cursor.fetchone()

        if not journey:
            flash('Journey not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        # Check permissions
        if journey['status'] == 'private' and journey['user_id'] != user_id:
            flash('You do not have permission to view this journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        if journey['is_hidden'] == 1:
            with db.get_cursor() as role_cursor:
                role_cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
                user_role = role_cursor.fetchone()['role']

            if user_role not in [constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN]:
                flash('This journey is not available.', constants.FLASH_MESSAGE_DANGER)
                return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        # Record view if journey is public and user is not the owner
        if journey['status'] == 'public' and journey['user_id'] != user_id:
            cursor.execute("""
                INSERT INTO journey_views (journey_id, user_id, viewed_at)
                VALUES (%s, %s, %s)
            """, (journey_id, user_id, datetime.now()))
            
            # Check for Discovery Pioneer achievement
            if AchievementUtils.check_discovery_pioneer_achievement(user_id, journey_id):
                achievement = AchievementUtils.get_achievement_notification('Discovery Pioneer')
                flash(f'Congratulations! You earned the {achievement["name"]} achievement!', 'success')

        # Get all event details for this journey with location following status
        cursor.execute("""SELECT e.*,
                                GROUP_CONCAT(ei.image_path) AS image_paths,
                                 CASE
                                     WHEN j.user_id != %s THEN
                                         EXISTS (SELECT 1
                                                 FROM user_follows uf
                                                 WHERE uf.user_id = %s
                                                   AND uf.follow_type = 'location'
                                                   AND uf.followed_id = e.location_id)
                                     ELSE FALSE
                                     END AS is_following_location
                          FROM events e
                                   JOIN journeys j ON e.journey_id = j.journey_id
                          LEFT JOIN 
                                event_images ei ON e.event_id = ei.event_id
                          WHERE e.journey_id = %s
                          GROUP BY e.event_id
                          ORDER BY e.start_time ASC;
                       """, (user_id, user_id, journey_id))
        raw_events = cursor.fetchall()
        events = []
        for row in raw_events:
            if row['image_paths']:
                row['image_paths'] = row['image_paths'].split(',') if row['image_paths'] else []
            events.append(row)

        cursor.execute("""
            SELECT DISTINCT location FROM events
            WHERE location IS NOT NULL AND location != ''
            ORDER BY location
        """)
        all_locations = [row['location'] for row in cursor.fetchall()]

    return render_template(constants.TEMPLATE_VIEW_JOURNEY,
                           journey=journey,
                           events=events,
                           all_locations=all_locations,
                           user_role=user_role,
                           mode=mode,
                           user_id=user_id)

@app.route('/journey/view/homepage/<int:journey_id>', methods=[constants.HTTP_METHOD_GET])
def view_homepage_journey(journey_id):
    # Retrieve journey details with author information
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT j.*, u.username, u.first_name, u.last_name, u.profile_image,
                   MIN(e.start_time) as journey_start
            FROM journeys j
            JOIN users u ON j.user_id = u.user_id
            LEFT JOIN events e ON j.journey_id = e.journey_id
            WHERE j.journey_id = %s
            GROUP BY j.journey_id
        """, (journey_id, ))
        journey = cursor.fetchone()

        # Check if journey exists and user has permission to view it
        if not journey:
            flash('Journey not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        # Get all event details for this journey
        cursor.execute("""SELECT e.*
                        FROM events e
                        JOIN journeys j ON e.journey_id = j.journey_id
                        WHERE e.journey_id = %s
                        ORDER BY e.start_time ASC;
                       """, (journey_id, ))
        events = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT location FROM events
            WHERE location IS NOT NULL AND location != ''
            ORDER BY location
        """)
        all_locations = [row['location'] for row in cursor.fetchall()]

    return render_template(constants.TEMPLATE_VIEW_HOMEPAGE_JOURNEY,
                           journey=journey,
                           events=events,
                           all_locations=all_locations)

@app.route('/journeys/search', methods=[constants.HTTP_METHOD_GET])
@login_required
def search_public_journey():
    keyword = request.args.get('keyword', '').strip()
    searchcat = request.args.get(constants.SEARCH_CATEGORY)

    if not keyword:
        flash('Please enter a keyword to search.', constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for('public_journeys'))

    query = f"%{keyword}%"
    with db.get_cursor() as cursor:
        if searchcat == constants.JOURNEY_TEXT:
            cursor.execute("""
                SELECT j.journey_id, j.title, j.description, j.update_date, j.user_id,
                       u.username, u.first_name, u.last_name
                FROM journeys j
                JOIN users u ON j.user_id = u.user_id
                WHERE j.status = 'public' AND j.is_hidden = 0
                AND (LOWER(j.title) LIKE LOWER(%s) OR LOWER(j.description) LIKE LOWER(%s))
                ORDER BY j.update_date DESC
            """, (query, query))
        elif searchcat == constants.LOCATION:
            cursor.execute("""
                SELECT DISTINCT
                           j.journey_id, j.title, j.description, j.update_date, j.user_id,
                           u.username, u.first_name, u.last_name
                FROM journeys j
                JOIN users u ON j.user_id = u.user_id
                JOIN events e ON j.journey_id = e.journey_id
                WHERE j.status = 'public' AND j.is_hidden = 0
                    AND LOWER(e.location) LIKE LOWER(%s)
                ORDER BY j.update_date DESC"""
                ,(query,))
        search_results = cursor.fetchall()

        # Retrieve all public journeys along with their associated event locations.
        # Locations are merged into a single string using GROUP_CONCAT for fuzzy comparison.
        if not search_results and searchcat == constants.LOCATION:
            cursor.execute("""
                SELECT j.journey_id, j.title, j.description, j.update_date, j.user_id,
                    u.username, u.first_name, u.last_name,
                    GROUP_CONCAT(DISTINCT e.location) AS locations
                FROM journeys j
                JOIN users u ON j.user_id = u.user_id
                JOIN events e ON j.journey_id = e.journey_id
                WHERE j.status = 'public' AND j.is_hidden = 0
                GROUP BY j.journey_id
                ORDER BY j.update_date DESC
            """)
            all_journeys = cursor.fetchall()

            # Fuzzy search by event location.
            # Compare the input keyword from the user with each journey's event location,
            # both converted to lowercase and stripped of whitespace.
            # If the similarity score is greater than or equal to 90,
            # append the journey to the result list and skip remaining locations.
            search_results = []
            for journey in all_journeys:
                location_list = journey.get('locations')
                if not location_list:
                    continue
                
                for location in location_list.split(','):
                    score = fuzz.partial_ratio(keyword.lower(), location.strip().lower())
                    if score >= 90:
                        search_results.append(journey)
                        break

    if not search_results:
        return render_template(constants.TEMPLATE_PUBLIC_JOURNEY, keyword = keyword, searchcat = searchcat)

    # Using if statement to check the selected search category.
    # If the type is JOURNEY_TEXT, highlight the matching keywords
    # to help users recognize them more esaily in the search results.
    # Since location details are not displayed on the journeys listing page,
    # keyword highlighting is not applied in the LOCATION search results.
    highlighted_results = []
    if searchcat == constants.JOURNEY_TEXT:
        for journey in search_results:
            highlighted_title = re.sub(f"({re.escape(keyword)})", r'<mark>\1</mark>', journey['title'], flags=re.IGNORECASE)
            highlighted_description = re.sub(f"({re.escape(keyword)})", r'<mark>\1</mark>', journey['description'], flags=re.IGNORECASE)
            journey['title'] = Markup(highlighted_title)
            journey['description'] = Markup(highlighted_description)
            highlighted_results.append(journey)
    else:
        highlighted_results = search_results

    return render_template(constants.TEMPLATE_PUBLIC_JOURNEY, journeyList = highlighted_results, keyword = keyword, searchcat = searchcat)

@app.route('/journeys/hidden', methods=[constants.HTTP_METHOD_GET])
@login_and_role_required([constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN])
def hidden_journeys():
    user_role = session[constants.USER_ROLE]
    
    # Query to get all hidden journeys ordered by most recently updated
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT j.journey_id, j.title, j.description, j.update_date, j.user_id,
                u.username, u.status, u.shareable
            FROM journeys j
            JOIN users u ON j.user_id = u.user_id
            WHERE j.is_hidden = 1
            ORDER BY u.username, j.update_date DESC
        """)
        hiddenJourneys = cursor.fetchall()

        # Grouped hidden journeys by username to ensure editor/admin can clearly 
        # review all publicly-shared journeys that have been hidden for each user. 
        
        # Using for loop to retrieve hidden journey list from the database. 
        # For each journey, check if username exists in the groupedJourneys dict. 
        # If not, create a new list for that users. Then append the journey to 
        # the corresponding list. Each username corresponds to a list of their hidden journeys.
        groupedJourneys = {}

        for journey in hiddenJourneys:
            username = journey['username']
            if username not in groupedJourneys:
                groupedJourneys[username] = []
            groupedJourneys[username].append(journey)

        # count the total hidden journey of the user
        hiddenCounts = {}
        for username, journeys in groupedJourneys.items():
            hiddenCounts[username] = len(journeys)

        return render_template(constants.TEMPLATE_HIDDEN_JOURNEY, groupedJourneys = groupedJourneys, hiddenCounts = hiddenCounts, user_role = user_role)
    
    
@app.route('/user/<int:user_id>/update_shareable', methods=[constants.HTTP_METHOD_POST])
@login_and_role_required([constants.USER_ROLE_EDITOR, constants.USER_ROLE_ADMIN])
def update_user_shareable(user_id):
    shareable = request.form[constants.USER_SHAREABLE]

    with db.get_cursor() as cursor:
        cursor.execute("UPDATE users SET shareable = %s WHERE user_id = %s;", (shareable, user_id))
        flash('Updated successfully.', constants.FLASH_MESSAGE_SUCCESS)

    return redirect(url_for(constants.URL_HIDDEN_JOURNEY))


@app.route('/journey/<int:journey_id>/follow', methods=[constants.HTTP_METHOD_POST])
@subscription_required
@login_required
def follow_journey(journey_id):
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE)

    with db.get_cursor() as cursor:
        # Get journey information, including the owner
        cursor.execute("SELECT journey_id, user_id FROM journeys WHERE journey_id = %s", (journey_id,))
        journey = cursor.fetchone()

        # Check if the journey exists
        if not journey:
            flash('Journey not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        # Prevent users from following their own journey
        if journey['user_id'] == user_id:
            flash('You cannot follow your own journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Check if the user is already following this journey
        cursor.execute("""
            SELECT 1 FROM user_follows 
            WHERE user_id = %s AND followed_id = %s AND follow_type = 'journey'
        """, (user_id, journey_id))
        already_following = cursor.fetchone()

        if already_following:
            flash('You are already following this journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Insert follow relationship into the database
        cursor.execute("""
            INSERT INTO user_follows (user_id, followed_id, follow_type)
            VALUES (%s, %s, 'journey')
        """, (user_id, journey_id))

        flash('You are now following this journey.', constants.FLASH_MESSAGE_SUCCESS)
        return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))



@app.route('/journey/<int:journey_id>/unfollow', methods=['GET'])
@subscription_required
@login_required
def unfollow_journey(journey_id):
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE)

    with db.get_cursor() as cursor:
        # Prevent users from unfollowing their own journey
        cursor.execute("SELECT user_id FROM journeys WHERE journey_id = %s", (journey_id,))
        journey_owner = cursor.fetchone()
        if journey_owner and journey_owner['user_id'] == user_id:
            flash('You cannot unfollow your own journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Check if the journey exists
        cursor.execute("SELECT journey_id FROM journeys WHERE journey_id = %s", (journey_id,))
        journey = cursor.fetchone()
        if not journey:
            flash('Journey not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        # Check if the user is following this journey
        cursor.execute("""
            SELECT * FROM user_follows
            WHERE user_id = %s AND followed_id = %s AND follow_type = 'journey'
        """, (user_id, journey_id))
        existing_follow = cursor.fetchone()
        if not existing_follow:
            flash('You are not following this journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Remove the follow relationship from the database
        cursor.execute("""
            DELETE FROM user_follows
            WHERE user_id = %s AND followed_id = %s AND follow_type = 'journey'
        """, (user_id, journey_id))

        flash('You have unfollowed this journey.', constants.FLASH_MESSAGE_SUCCESS)
        return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

@app.route('/journey/<int:journey_id>/follow_location', methods=[constants.HTTP_METHOD_POST])
@subscription_required
@login_required
def follow_location(journey_id):
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE)

    with db.get_cursor() as cursor:
        # Get journey information, including the owner
        cursor.execute("SELECT journey_id, user_id FROM journeys WHERE journey_id = %s", (journey_id,))
        journey = cursor.fetchone()

        # Check if the journey exists
        if not journey:
            flash('Journey not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))

        # Prevent users from following locations in their own journey
        if journey['user_id'] == user_id:
            flash('You cannot follow locations in your own journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Get the location from the form
        location_id = request.form.get('location_id')
        if not location_id:
            flash('Location is required to follow.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode
                                    ))
        # Check if the user is already following this location
        cursor.execute("""
                       SELECT 1
                       FROM user_follows
                       WHERE user_id = %s
                         AND followed_id = %s
                         AND follow_type = 'location'
                       """, (user_id, location_id))
        already_following = cursor.fetchone()
        if already_following:
            flash('You are already following this location.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode))

        # Insert follow relationship into the database
        cursor.execute("""
                       INSERT INTO user_follows (user_id, followed_id, follow_type)
                       VALUES (%s, %s, 'location')
                       """, (user_id, location_id))
        flash('You are now following this location.', constants.FLASH_MESSAGE_SUCCESS)
        return redirect(url_for('view_journey', journey_id=journey_id, mode=mode
                                ))

# unfollow_location
@app.route('/journey/<int:journey_id>/unfollow_location/<int:location_id>')
@subscription_required
@login_required
def unfollow_location(journey_id, location_id):
    user_id = session[constants.USER_ID]
    mode = request.args.get(constants.REQUEST_MODE)

    with db.get_cursor() as cursor:
        # Get the location from the form
        if not location_id:
            flash('Location is required to unfollow.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode
                                    ))
        # Check if the journey exists
        cursor.execute("SELECT journey_id FROM journeys WHERE journey_id = %s", (journey_id,))
        journey = cursor.fetchone()
        if not journey:
            flash('Journey not found.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for(constants.URL_PUBLIC_JOURNEY))
        # Prevent users from unfollowing locations in their own journey
        cursor.execute("SELECT user_id FROM journeys WHERE journey_id = %s", (journey_id,))
        journey_owner = cursor.fetchone()
        if journey_owner and journey_owner['user_id'] == user_id:
            flash('You cannot unfollow locations in your own journey.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode
                                    ))
        # Check if the user is following this location
        cursor.execute("""
                       SELECT * 
                       FROM user_follows 
                       WHERE user_id = %s AND followed_id = %s AND follow_type = 'location'
                       """, (user_id, location_id))
        existing_follow = cursor.fetchone()
        if not existing_follow:
            flash('You are not following this location.', constants.FLASH_MESSAGE_DANGER)
            return redirect(url_for('view_journey', journey_id=journey_id, mode=mode
                                    ))
        # Remove the follow relationship from the database
        cursor.execute("""
                       DELETE FROM user_follows 
                       WHERE user_id = %s AND followed_id = %s AND follow_type = 'location'
                       """, (user_id, location_id))
        flash('You have unfollowed this location.', constants.FLASH_MESSAGE_SUCCESS)
        return redirect(url_for('view_journey', journey_id=journey_id, mode=mode
                                ))


@app.route('/update_status/<int:journey_id>', methods=['POST'])
@login_required
def update_journey_status(journey_id):
    """Update journey status (public/private)"""
    user_id = session[constants.USER_ID]
    new_status = request.form.get('status')
    
    if new_status not in ['public', 'private']:
        flash('Invalid status', 'error')
        return redirect(url_for('view_journey', journey_id=journey_id))
    
    with db.get_cursor() as cursor:
        # Check if user owns the journey
        cursor.execute("""
            SELECT user_id 
            FROM journeys 
            WHERE journey_id = %s
        """, (journey_id,))
        journey = cursor.fetchone()
        
        if not journey or journey['user_id'] != user_id:
            flash('Unauthorized', 'error')
            return redirect(url_for('view_journey', journey_id=journey_id))
        
        # Update status
        cursor.execute("""
            UPDATE journeys 
            SET status = %s,
                updated_at = %s
            WHERE journey_id = %s
        """, (new_status, datetime.now(), journey_id))
        
        # Check for First Share achievement if making public
        if new_status == 'public':
            if AchievementUtils.check_first_share_achievement(user_id):
                achievement = AchievementUtils.get_achievement_notification('First Share')
                flash(f'Congratulations! You earned the {achievement["name"]} achievement!', 'success')
            
            # Check for Sharing Guru achievement
            if AchievementUtils.check_sharing_guru_achievement(user_id):
                achievement = AchievementUtils.get_achievement_notification('Sharing Guru')
                flash(f'Congratulations! You earned the {achievement["name"]} achievement!', 'success')
        
        flash('Journey status updated successfully', 'success')
        return redirect(url_for('view_journey', journey_id=journey_id))


