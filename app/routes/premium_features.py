from app import app
from flask import redirect, render_template, request, session, url_for, flash, make_response
from app.config import constants
from app.utils.decorators import login_required, login_and_role_required
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from app.utils.helpers import user_details
from io import BytesIO

from app.db import db

@app.route('/subscription')
@login_required
def subscription():
    user_id = session[constants.USER_ID]
    user_role = session[constants.USER_ROLE]
    logged_in = session[constants.SESSION_LOGGED_IN]

    # Query subscription details
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM subscriptions WHERE is_admin_grantable = %s 
        """, (constants.USER_IS_ADMIN_GRANTABLE_NO,))
        subscriptions = cursor.fetchall()
    
    # Check if user has used free trial
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT subscription_status, is_trial_used FROM USERS WHERE user_id = %s 
        """, (user_id,))
        subDetails = cursor.fetchone()
        
    return render_template(constants.TEMPLATE_SUBSCRIPTION, subscriptions=subscriptions, subDetails = subDetails, user_role = user_role, logged_in = logged_in)

@app.route('/start_trial')
@login_and_role_required([constants.USER_ROLE_TRAVELLER])
def start_trial():
    if session.get(constants.USER_IS_TRIAL_USED) == 1:
        flash("You have already used the free trial.", constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for(constants.URL_SUBSCRIPTION))
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT subscription_id FROM subscriptions WHERE name = %s 
            """, (constants.SUBSCRIPTIONS_NAME_FREE_TRIAL,))
            subscription = cursor.fetchone()

            if not subscription:
                flash("No free trial available.", constants.FLASH_MESSAGE_DANGER)
                return redirect(url_for(constants.URL_SUBSCRIPTION))
        process_subscription(constants.USER_SUBSCRIPTION_TRIAL, constants.USER_IS_TRIAL_USED_YES, None, subscription[constants.SUBSCRIPTION_ID], constants.SUBSCRIPTIONS_DURATION_MONTHS_ONE, 
                         None, None, None, None, None, None, None, None)
    except Exception as e:
        flash("An error occurred. Please try again later.", constants.FLASH_MESSAGE_DANGER)
        print("Error:", e)
        return render_template(constants.TEMPLATE_PAYMENT, subscription=subscription)
    return redirect(url_for(constants.URL_SUBSCRIPTION))

def process_subscription(subscription_status, is_trial_used, is_admin_grantable, subscription_id, duration_months, 
                         billing_country, billing_address, card_number, expiry_date, cvv, amount_paid, price_nzd_excl_gst, recipient_id):
    with db.get_cursor() as cursor:
        user_id_to_query = recipient_id if recipient_id else session.get(constants.USER_ID)
        cursor.execute("""
            SELECT subscription_end_date, remaining_months FROM users WHERE user_id = %s
        """, (user_id_to_query,))
        user = cursor.fetchone()

        sql = "UPDATE users SET subscription_status = %s, subscription_end_date = %s, remaining_months = %s"
        subscription_end_date = user[constants.USER_SUBSCRIPTION_END_DATE]
        if subscription_end_date is None:
            subscription_end_date = date.today()
        new_remaining_months = user.get(constants.USER_REMAINING_MONTHS) + duration_months
        new_end_date = subscription_end_date + relativedelta(months=+duration_months)
        params = [subscription_status, new_end_date, new_remaining_months]
        
        if is_trial_used is not None:
            sql += ", is_trial_used = %s"
            params.append(is_trial_used)
        sql += " WHERE user_id = %s"
        if is_admin_grantable is not None:
            params.append(recipient_id)
        else:
            params.append(session.get(constants.USER_ID))
        cursor.execute(sql, tuple(params))

        start_date = date.today()
        end_date = start_date + relativedelta(months=+duration_months)
        if is_admin_grantable is not None:
            cursor.execute("""
                INSERT INTO user_subscriptions (user_id, subscription_id, start_date, end_date, gifted_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (recipient_id, subscription_id, start_date, end_date, session.get(constants.USER_ID)))
        else:
            cursor.execute("""
                INSERT INTO user_subscriptions (user_id, subscription_id, start_date, end_date)
                VALUES (%s, %s, %s, %s)
            """, (session.get(constants.USER_ID), subscription_id, start_date, end_date))
        user_subscription_id = cursor.lastrowid

        if is_trial_used is not None or is_admin_grantable is not None:
            if is_trial_used is not None:
                session[constants.USER_IS_TRIAL_USED] = constants.USER_IS_TRIAL_USED_YES
                session[constants.USER_SUBSCRIPTION_END_DATE] = new_end_date.strftime('%d/%m/%Y')
                flash(f"Your {duration_months}-month{'s' if duration_months != 1 else ''} free trial has started!", constants.FLASH_MESSAGE_SUCCESS)
            else:
                flash(f"{duration_months}-month{'s' if duration_months != 1 else ''} subscription gifted successfully!", constants.FLASH_MESSAGE_SUCCESS)
        else:
            subscription_payment(billing_country, billing_address, card_number, expiry_date, cvv, price_nzd_excl_gst,amount_paid, user_subscription_id, cursor)
            flash(f"Your {duration_months}-month{'s' if duration_months != 1 else ''} subscription activated successfully.!", constants.FLASH_MESSAGE_SUCCESS)
            session[constants.USER_SUBSCRIPTION_END_DATE] = new_end_date.strftime('%d/%m/%Y')
        
        cursor.execute("""
                DELETE FROM announcements WHERE recipient_id = %s
                    AND subscription_end_date = %s
            """, (session.get(constants.USER_ID), subscription_end_date))
def subscription_payment(billing_country, billing_address, card_number, expiry_date, cvv, price_nzd_excl_gst, amount_paid, user_subscription_id, cursor):
    if(billing_country == constants.REQUEST_BILLING_COUNTRY_NZ):
        gst_amount = (amount_paid - price_nzd_excl_gst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        gst_amount = 0.00
    cursor.execute("""
            INSERT INTO subscription_payments (user_id, billing_country, billing_address, amount_paid, gst_amount, card_number, expiry_date, cvv, user_subscription_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session.get(constants.USER_ID), billing_country, billing_address, amount_paid, gst_amount, card_number, expiry_date, cvv, user_subscription_id))

@app.route('/payment/<int:subscription_id>')
@login_and_role_required([constants.USER_ROLE_TRAVELLER])
def payment_page(subscription_id):
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM subscriptions WHERE subscription_id = %s 
        """, (subscription_id,))
        subscription = cursor.fetchone()
    if not subscription:
        flash("Subscription plan not found.", constants.FLASH_MESSAGE_DANGER)
        return redirect(url_for(constants.URL_SUBSCRIPTION))
    return render_template(constants.TEMPLATE_PAYMENT, subscription=subscription)

@app.route('/process_payment', methods=[constants.HTTP_METHOD_POST])
@login_and_role_required([constants.USER_ROLE_TRAVELLER])
def process_payment():
    subscription_id = request.form.get(constants.SUBSCRIPTION_ID)
    card_number = request.form.get(constants.PAYMENT_CARD_NUMBER).replace('-', '')
    expiry_date = request.form.get(constants.PAYMENT_EXPIRY_DATE)
    cvv = request.form.get(constants.PAYMENT_CVV)
    billing_country = request.form.get(constants.PAYMENT_BILLING_COUNTRY)
    billing_address = request.form.get(constants.PAYMENT_BILLING_ADDRESS)
    price_nzd_excl_gst = Decimal(request.form.get(constants.SUBSCRIPTION_PRICE_NZD_EXCL_GST))
    price_to_pay = Decimal(request.form.get(constants.REQUEST_PRICE_TO_PAY))
    duration_months_str = request.form.get(constants.SUBSCRIPTION_DURATION_MONTHS)
    duration_months = int(duration_months_str) if duration_months_str else None
    subscription = {
            constants.SUBSCRIPTION_ID: subscription_id,
        constants.PAYMENT_CARD_NUMBER: card_number,
        constants.PAYMENT_EXPIRY_DATE: expiry_date,
        constants.PAYMENT_CVV: cvv,
        constants.PAYMENT_BILLING_COUNTRY: billing_country,
        constants.PAYMENT_BILLING_ADDRESS: billing_address,
        constants.SUBSCRIPTION_DURATION_MONTHS: duration_months,
        constants.SUBSCRIPTION_PRICE_NZD_EXCL_GST: price_nzd_excl_gst,
        constants.REQUEST_PRICE_TO_PAY: price_to_pay
    }

    if not (card_number and expiry_date and cvv and billing_country and billing_address):
        flash("Please fill in all payment details.",constants.FLASH_MESSAGE_DANGER)
        return render_template(constants.TEMPLATE_PAYMENT, subscription=subscription)
    try:
        process_subscription(constants.USER_SUBSCRIPTION_PREMIUM, None, None, subscription_id, duration_months, 
                             billing_country, billing_address, card_number, expiry_date, cvv, price_to_pay, price_nzd_excl_gst, None)
    except Exception as e:
        flash("An error occurred. Please try again later.", constants.FLASH_MESSAGE_DANGER)
        print("Error:", e)
        return render_template(constants.TEMPLATE_PAYMENT, subscription=subscription)
    return redirect(url_for(constants.URL_SUBSCRIPTION))

from flask import request

@app.route('/subscription_history', methods=[constants.HTTP_METHOD_GET])
@login_required
def subscription_history():
    user_id = request.args.get(constants.USER_ID)
    if not user_id:
        user_id = session.get(constants.USER_ID)
    admin_granted_param = request.args.get(constants.REQUEST_ADMIN_GRANTED)
    profile = user_details(user_id)

    query = """
        SELECT us.user_subscription_id, us.start_date, us.end_date, us.created_at, s.name AS subscription_name, s.duration_months, 
               s.is_free_trial, s.discount_percent, s.is_admin_grantable, sp.card_number, 
               sp.amount_paid, sp.gst_amount, sp.billing_country, sp.billing_address
        FROM user_subscriptions us
        LEFT JOIN subscription_payments sp ON sp.user_subscription_id = us.user_subscription_id
        LEFT JOIN subscriptions s ON s.subscription_id = us.subscription_id
        WHERE us.user_id = %s
    """
    params = [user_id]
    if admin_granted_param == constants.REQUEST_TRUE:
        query += " AND s.is_admin_grantable = TRUE"
    elif admin_granted_param == constants.REQUEST_FALSE:
        query += " AND (s.is_admin_grantable IS NULL OR s.is_admin_grantable = FALSE)"
    query += " ORDER BY us.start_date DESC"
    with db.get_cursor() as cursor:
        cursor.execute(query, params)
        subscriptions = cursor.fetchall()

    return render_template(constants.TEMPLATE_SUBSCRIPTION_HISTORY, subscriptions=subscriptions, profile=profile)

@app.route('/gift_subscription', methods=[constants.HTTP_METHOD_GET])
@login_and_role_required([constants.USER_ROLE_ADMIN])
def gift_subscription():
    recipient_id = request.args.get(constants.USER_ID)
    duration_months_str = request.args.get(constants.SUBSCRIPTION_DURATION_MONTHS)
    duration_months = int(duration_months_str)

    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT subscription_id FROM subscriptions WHERE is_admin_grantable = %s AND duration_months = %s 
            """, (constants.USER_IS_ADMIN_GRANTABLE_YES, duration_months))
            subscription = cursor.fetchone()

            if not subscription:
                flash("No free trial available.", constants.FLASH_MESSAGE_DANGER)
                return redirect(url_for(constants.URL_SUBSCRIPTION))
            process_subscription(constants.USER_SUBSCRIPTION_PREMIUM, None, constants.USER_IS_ADMIN_GRANTABLE_YES, subscription[constants.SUBSCRIPTION_ID], duration_months, 
                         None, None, None, None, None, None, None, recipient_id)
            
            title = 'You have Received a Gift Subscription!'
            plural = 's' if duration_months > 1 else ''
            content = f"An administrator has gifted you a premium subscription for {duration_months} month{plural}."
            cursor.execute("""
                INSERT INTO announcements (user_id, title, content, recipient_id)
                VALUES(%s, %s, %s, %s)
                """,
                (session.get(constants.USER_ID), title, content, recipient_id)
                )
    except Exception as e:
        flash("An error occurred. Please try again later.", constants.FLASH_MESSAGE_DANGER)
        print("Error:", e)
        return redirect(url_for(constants.URL_ALL_USERS))
    return redirect(url_for(constants.URL_ALL_USERS))

@app.route('/receipt/<int:user_subscription_id>')
@login_required
def view_receipt(user_subscription_id):
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT us.start_date, us.end_date, us.created_at, s.name AS subscription_name, s.duration_months, 
                s.discount_percent, sp.card_number, 
                sp.amount_paid, sp.gst_amount, sp.billing_country, sp.billing_address
                FROM user_subscriptions us
                LEFT JOIN subscription_payments sp ON sp.user_subscription_id = us.user_subscription_id
                LEFT JOIN subscriptions s ON s.subscription_id = us.subscription_id
                WHERE us.user_subscription_id = %s
            """, (user_subscription_id,))
        subscription = cursor.fetchone()
        subscription[constants.USER_ID] = request.args.get(constants.USER_ID)

    return render_template(constants.TEMPLATE_RECEIPT_DETAIL, subscription=subscription)

@app.route('/receipt/<int:user_subscription_id>/pdf')
def download_receipt_pdf(user_subscription_id):
    from datetime import datetime

    # Retrieve subscription and payment info from the database
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT us.start_date, us.end_date, us.created_at, s.name AS subscription_name, s.duration_months, 
                s.discount_percent, sp.card_number, 
                sp.amount_paid, sp.gst_amount, sp.billing_country, sp.billing_address
            FROM user_subscriptions us
            LEFT JOIN subscription_payments sp ON sp.user_subscription_id = us.user_subscription_id
            LEFT JOIN subscriptions s ON s.subscription_id = us.subscription_id
            WHERE us.user_subscription_id = %s
        """, (user_subscription_id,))
        subscription = cursor.fetchone()

    # Create PDF buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Set margin and initial vertical position
    margin_left = 30
    current_y = height - 40

    # Utility: Draw section title
    def draw_title(text, size=20, bold=True, spacing=25):
        nonlocal current_y
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, size)
        c.drawString(margin_left, current_y, text)
        current_y -= spacing

    # Utility: Draw label and value with label in bold
    def draw_field(label, value, spacing=18):
        nonlocal current_y
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_left + 10, current_y, f"{label}:")
        c.setFont("Helvetica", 11)
        c.drawString(margin_left + 100, current_y, str(value))
        current_y -= spacing

    # ---------- Header ----------
    # Header section layout
    receipt_title = "Receipt"
    thank_you = "Thank you for your payment."
    receipt_date_label = "Receipt Date:"
    receipt_date_value = subscription['created_at'].strftime('%d %B, %Y at %H:%M')

    # 1. Draw the "Receipt" title on the left side
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin_left, current_y, receipt_title)

    # 2. Calculate the width of the label and the date value texts
    c.setFont("Helvetica-Bold", 11)
    label_width = c.stringWidth(receipt_date_label, "Helvetica-Bold", 11)
    c.setFont("Helvetica", 11)
    value_width = c.stringWidth(receipt_date_value, "Helvetica", 11)
    space_between = 8  # Space in pixels between the label and the date value, adjust as needed

    # 3. Calculate the x-coordinates for the date value (right-aligned) and the label (left-aligned)
    value_x = width - margin_left  # Right edge position for the date value text
    label_x = value_x - value_width - space_between - label_width  # Starting position for the label text

    # 4. Draw the receipt date label (left-aligned)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(label_x, current_y, receipt_date_label)

    # 5. Draw the receipt date value (right-aligned)
    c.setFont("Helvetica", 11)
    c.drawRightString(value_x, current_y, receipt_date_value)
    # Move the current y position down for the next line
    current_y -= 20

    # 6. Draw the thank you message below the title (left-aligned)
    c.setFont("Helvetica", 11)
    c.drawString(margin_left, current_y, thank_you)
    # Move the current y position down for the next line
    current_y -= 20

    # 7. Draw a horizontal line for visual separation
    c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Light gray color for the line
    c.setLineWidth(0.5)  # Thin line width
    c.line(margin_left, current_y, width - margin_left, current_y)
    # Move the current y position down after the line
    current_y -= 20

    # ---------- Subscription Plan Details ----------
    current_y -= 10
    draw_title("Subscription Plan", size=14)
    draw_field("Plan", subscription['subscription_name'])
    draw_field("Duration", f"{subscription['duration_months']} month{'s' if subscription['duration_months'] > 1 else ''}")
    draw_field("Start Date", subscription['start_date'].strftime('%d %B, %Y'))
    draw_field("End Date", subscription['end_date'].strftime('%d %B, %Y'))

    # ---------- Payment Information ----------
    current_y -= 5
    draw_title("Payment Information", size=14)
    card_display = f"**** **** **** {subscription['card_number'][-4:]}" if subscription['card_number'] else "N/A"
    draw_field("Card Number", card_display)
    draw_field("Amount Paid", f"NZD ${subscription['amount_paid']:.2f}")
    if subscription['billing_country'] == 'NZ':
        draw_field("GST (15%)", f"NZD ${subscription['gst_amount']:.2f}")

    # ---------- Billing Information ----------
    current_y -= 5
    draw_title("Billing Information", size=14)
    draw_field("Billing Country", subscription['billing_country'])
    draw_field("Billing Address", subscription['billing_address'])      

    # Finalize the PDF
    c.showPage()
    c.save()

    # Return PDF file as response
    pdf = buffer.getvalue()
    buffer.close()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=receipt_{user_subscription_id}.pdf'
    return response

