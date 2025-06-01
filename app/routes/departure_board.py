from flask import render_template, session
from app import app
from app.config import constants
from app.db import db
from app.utils.decorators import login_required, subscription_required


@app.route('/departure_board', methods=[constants.HTTP_METHOD_GET])
@subscription_required
@login_required
def departure_board():
    user_id = session[constants.USER_ID]

    with db.get_cursor() as cursor:
        query = """
                WITH journey_follows AS (SELECT e.event_id,
                                                e.title,
                                                e.description,
                                                e.start_time,
                                                e.end_time,
                                                e.location,
                                                NULL      AS latitude,
                                                NULL      AS longitude,
                                                e.event_image,
                                                e.journey_id,
                                                j.update_date,
                                                j.title   AS journey_title,
                                                u.user_id AS creator_user_id,
                                                u.username,
                                                u.role,
                                                'journey' AS follow_type
                                         FROM user_follows uf
                                                  JOIN events e ON uf.followed_id = e.journey_id
                                                  JOIN journeys j ON j.journey_id = e.journey_id
                                                  JOIN users u ON u.user_id = j.user_id
                                         WHERE uf.user_id = %s
                                           AND uf.follow_type = 'journey'
                                           AND j.status = 'public'
                                           AND j.is_hidden = 0
                                           AND u.status = 'active'
                                           AND u.shareable = 1),

                     user_follows_events AS (SELECT e.event_id,
                                                    e.title,
                                                    e.description,
                                                    e.start_time,
                                                    e.end_time,
                                                    e.location,
                                                    NULL      AS latitude,
                                                    NULL      AS longitude,
                                                    e.event_image,
                                                    e.journey_id,
                                                    j.update_date,
                                                    j.title   AS journey_title,
                                                    u.user_id AS creator_user_id,
                                                    u.username,
                                                    u.role,
                                                    'user'    AS follow_type
                                             FROM user_follows uf
                                                      JOIN journeys j ON j.user_id = uf.followed_id
                                                      JOIN events e ON e.journey_id = j.journey_id
                                                      JOIN users u ON u.user_id = j.user_id
                                             WHERE uf.user_id = %s
                                               AND uf.follow_type = 'user'
                                               AND j.status = 'public'
                                               AND j.is_hidden = 0
                                               AND u.status = 'active'
                                               AND u.shareable = 1),

                     location_follows_events AS (SELECT e.event_id,
                                                        e.title,
                                                        e.description,
                                                        e.start_time,
                                                        e.end_time,
                                                        e.location,
                                                        l.latitude,
                                                        l.longitude,
                                                        e.event_image,
                                                        e.journey_id,
                                                        j.update_date,
                                                        j.title    AS journey_title,
                                                        u.user_id  AS creator_user_id,
                                                        u.username,
                                                        u.role,
                                                        'location' AS follow_type
                                                 FROM user_follows uf
                                                          JOIN events e ON uf.followed_id = e.location_id
                                                          JOIN journeys j ON j.journey_id = e.journey_id
                                                          JOIN users u ON u.user_id = j.user_id
                                                          LEFT JOIN locations l ON e.location_id = l.location_id
                                                 WHERE uf.user_id = %s
                                                   AND uf.follow_type = 'location'
                                                   AND j.status = 'public'
                                                   AND j.is_hidden = 0
                                                   AND u.status = 'active'
                                                   AND u.shareable = 1),

                     combined AS (SELECT *
                                  FROM journey_follows
                                  UNION ALL
                                  SELECT *
                                  FROM user_follows_events
                                  UNION ALL
                                  SELECT *
                                  FROM location_follows_events)

                SELECT event_id,
                       title,
                       description,
                       start_time,
                       end_time,
                       location,
                       latitude,
                       longitude,
                       event_image,
                       journey_id,
                       journey_title,
                       creator_user_id,
                       username,
                       role,
                       GROUP_CONCAT(DISTINCT follow_type) AS follow_types,
                       update_date
                FROM combined
                GROUP BY event_id,
                         title,
                         description,
                         start_time,
                         end_time,
                         update_date,
                         location,
                         latitude,
                         longitude,
                         event_image,
                         journey_id,
                         journey_title,
                         creator_user_id,
                         username,
                         role
                """

        cursor.execute(query, (user_id, user_id, user_id))
        events = cursor.fetchall()

        events.sort(key=lambda e: e['start_time'])

        for e in events:
            e['follow_types'] = e['follow_types'].split(',') if e.get('follow_types') else []

    return render_template(constants.TEMPLATE_DEPARTURE_BOARD, events=events)
