# Used to indicate whether the user is logged in in the session
SESSION_LOGGED_IN = 'loggedin'

HTTP_METHOD_POST = 'POST'
HTTP_METHOD_GET = 'GET'
HTTP_METHOD_DELETE = 'DELETE'

# Role to new users upon registration.
USER_ROLE_TRAVELLER = 'traveller'
USER_ROLE_EDITOR = 'editor'
USER_ROLE_ADMIN = 'admin'
USER_ROLE_MODERATOR = 'moderator'

# User information fields
USER_ID = 'user_id'
FOLLOWED_ID = 'followed_id'
USERNAME = 'username' 
USER_ROLE = 'role'
EMAIL = 'email'
PASSWORD_HASH = 'password_hash'
RE_PASSWORD = 'repassword'
PASSWORD = 'password'
FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
LOCATION = 'location'
USER_STATUS='status'
USER_PROFILE_IMAGE='profile_image'
USER_FULL_NAME = 'full_name'
USER_PERSONAL_DESCRIPTION='personal_description'
USER_SUBSCRIPTION_STATUS = 'subscription_status'
USER_IS_TRIAL_USED = 'is_trial_used'
USER_SHAREABLE = 'shareable'
USER_SUBSCRIPTION_END_DATE = 'subscription_end_date'
USER_REMAINING_MONTHS = 'remaining_months'

DEFAULT_USER_ROLE = 'traveller'
DEFAULT_STATUS = 'active'

# user status
USER_STATUS_ACTIVE = 'active'
USER_STATUS_BANNED = 'banned'

# User subscription status
USER_SUBSCRIPTION_FREE = 'Free'
USER_SUBSCRIPTION_TRIAL = 'Trial'
USER_SUBSCRIPTION_PREMIUM = 'Premium'

USER_IS_ADMIN_GRANTABLE_NO = 0
USER_IS_ADMIN_GRANTABLE_YES = 1

# Indicates the user has not used the free trial yet
USER_IS_TRIAL_USED_NO = 0
# Indicates the user has already used the free trial
USER_IS_TRIAL_USED_YES = 1


IMAGE_UPLOAD_FOLDER = 'IMAGE_UPLOAD_FOLDER'
IMAGE_UPLOAD_FOLDER_URL = 'static/uploads'

# URL endpoint names
URL_LOGIN = 'login'  # URL for the login page
URL_SIGNUP = 'signup'  # URL for the login page
URL_TRAVELLER_HOME = 'traveller_home'
URL_EDITOR_HOME = 'editor_home'
URL_ADMIN_HOME = 'admin_home'
URL_MODERATOR_HOME = 'moderator_home'
URL_PROFILE = 'profile'
URL_MYJOURNEY = 'myjourney'
URL_PUBLIC_JOURNEY = 'public_journeys'
URL_HOME = 'home'
URL_ROOT = 'root'
URL_ANNOUNCEMENTS = 'announcements_list'
URL_DEPARTURE_BOARD = 'departure_board'
URL_HIDDEN_JOURNEY = 'hidden_journeys'
URL_SUBSCRIPTION = 'subscription'
URL_ALL_USERS = 'all_users'

# Template file names
TEMPLATE_HOME = 'home.html'
TEMPLATE_ACCESS_DENIED = 'access_denied.html'  # Template displayed when a user is denied access to a resource
TEMPLATE_ADMIN_HOME = 'admin_home.html'  # Template for the admin home page
TEMPLATE_EDITOR_HOME = 'editor_home.html'  # Template for the editor home page
TEMPLATE_TRAVELLER_HOME = 'traveller_home.html'  # Template for the traveller home page
TEMPLATE_MODERATOR_HOME = 'moderator_home.html' # Template for the moderator home page
TEMPLATE_LOGIN= 'login.html'
TEMPLATE_USER = 'users.html'
TEMPLATE_USER_EDIT = 'user_edit.html'
TEMPLATE_SIGN_UP = 'signup.html'
TEMPLATE_PROFILE = 'profile.html'
TEMPLATE_CHANGE_PASSWORD = 'change_password.html'
TEMPLATE_RESTRICTED_USERS = 'restricted_users.html'
TEMPLATE_PROFILE_SUBSCRIPTION = 'profile_subscription.html'

# Journey templates
TEMPLATE_MYJOURNEY = 'myjourney.html'
TEMPLATE_ADD_JOURNEY = 'add_journey.html'
TEMPLATE_EDIT_JOURNEY = 'edit_journey.html'
TEMPLATE_PUBLIC_JOURNEY = 'public_journeys.html'
TEMPLATE_VIEW_JOURNEY = 'view_journey.html'
TEMPLATE_VIEW_HOMEPAGE_JOURNEY = 'view_homepage_journey.html'
TEMPLATE_DELETE_JOURNEY = 'delete_journey.html'
TEMPLATE_HIDDEN_JOURNEY = 'hidden_journeys.html'

# Event templates
TEMPLATE_EVENTS = 'events.html'
TEMPLATE_ADD_EVENT = 'add_event.html'
TEMPLATE_EDIT_EVENT = 'edit_event.html'
TEMPLATE_DELETE_EVENT = 'delete_event.html'

# Announcement templates
TEMPLATE_ANNOUNCEMENTS = 'announcements.html'
TEMPLATE_ADD_ANNOUNCEMENT = 'add_announcement.html'
TEMPLATE_VIEW_ANNOUNCEMENTS = 'view_announcement.html'

# Departure Board templates
TEMPLATE_DEPARTURE_BOARD = 'departure_board.html'

TEMPLATE_SUBSCRIPTION = 'subscription.html'
TEMPLATE_PAYMENT = 'payment.html'
TEMPLATE_SUBSCRIPTION_HISTORY = 'subscription_history.html'
TEMPLATE_RECEIPT_DETAIL = 'receipt_detail.html'

# HTTP status codes
# User permission-related issues
HTTP_STATUS_CODE_403 = 403  # Forbidden: User does not have permission to access the requested resource
# Database errors or other internal server issues
HTTP_STATUS_CODE_500 = 500  # Internal Server Error: A generic error indicating that something went wrong on the server side
HTTP_STATUS_CODE_404 = 404

# Flash message types for different scenarios
FLASH_MESSAGE_DANGER = 'danger' # Used for error messages or warnings
FLASH_MESSAGE_SUCCESS = 'success' # Used for error messages or warnings

SEARCH_TERM = 'searchterm'  # Query parameter for the search term
SEARCH_CATEGORY = 'searchcat'  # Query parameter for the search category

FORM_FIELD_CURRENT_PASSWORD = 'current_password'  # Form field for the user's current password
FORM_FIELD_NEW_PASSWORD = 'new_password'  # Form field for the user's new password
FORM_FIELD_CONFIRM_PASSWORD = 'confirm_password'  # Form field to confirm the new password
FORM_FIELD_FIRSTNAME = 'firstname'
FORM_FIELD_LASTNAME = 'lastname'
FORM_FIELD_CONFIRM_PASSWORD = 'confirm_password'

# Journey information fields
JOURNEY_ID = 'journey_id'  # Unique identifier for the journey
TITLE = 'title'
DESCRIPTION = 'description'
STATUS = 'status'
IS_HIDDEN = 'is_hidden'
START_DATE = 'start_date'
UPDATE_DATE = 'update_date'
JOURNEY_STATUS_PRIVATE = 'private'
JOURNEY_STATUS_PUBLISHED = 'published'
JOURNEY_TEXT = 'journey_text' # including title & description

REQUEST_PRICE_TO_PAY = 'price_to_pay'
REQUEST_BILLING_COUNTRY_NZ = 'NZ'
REQUEST_ADMIN_GRANTED = 'admin_granted'
REQUEST_TRUE = 'true'
REQUEST_FALSE = 'false'
REQUEST_MODE = 'mode'
MODE_PUBLIC='public'
MODE_ALL = 'all'
MODE_DEPARTURE_BOARD = 'departure_board'
MODE_SUBSCRIBE= 'subscribe'

# Announcement information fields
ANNOUNCEMENT_ID = 'announcement_id'
TITLE = "title"
CONTENT = 'content'
CREATED_TIME = 'created_time'

VIEW_TYPE_ALL = 'all'
VIEW_TYPE_STAFF = 'staff'
VIEW_TYPE_RESTRICTED = 'restricted'

#subscriptions information fields
SUBSCRIPTION_ID = 'subscription_id'
SUBSCRIPTION_DURATION_MONTHS = 'duration_months'
SUBSCRIPTION_PRICE_NZD_EXCL_GST = 'price_nzd_excl_gst'
SUBSCRIPTION_IS_ADMIN_GRANTABLE = 'is_admin_grantable'

SUBSCRIPTIONS_NAME_FREE_TRIAL = 'Free Trial'
SUBSCRIPTIONS_DURATION_MONTHS_ONE = 1

# subscription_payments information fields
PAYMENT_ID = 'payment_id'
PAYMENT_BILLING_COUNTRY = 'billing_country'
PAYMENT_BILLING_ADDRESS = 'billing_address'
PAYMENT_AMOUNT_PAID = 'amount_paid'
PAYMENT_GST_AMOUNT = 'gst_amount'
PAYMENT_CURRENCY = 'currency'
PAYMENT_CARD_NUMBER = 'card_number'
PAYMENT_EXPIRY_DATE = 'expiry_date'
PAYMENT_CVV = 'cvv'
PAYMENT_USER_SUBSCRIPTION_ID = 'user_subscription_id'

# messages
MAX_MESSAGE_LENGTH = 1000
UNREAD_MESSAGE_CHECK_INTERVAL = 30000

# Community-related constants
URL_PUBLIC_USERS = 'public_users'
URL_VIEW_PUBLIC_PROFILE = 'view_public_profile'
URL_COMMUNITY_SETTINGS = 'community_settings'
TEMPLATE_PUBLIC_USERS = 'community/public_users.html'
TEMPLATE_PUBLIC_PROFILE = 'community/public_profile.html'
TEMPLATE_COMMUNITY_SETTINGS = 'community/settings.html'

# Additional user fields
USER_IS_PUBLIC_PROFILE = 'is_public_profile'
USER_FOLLOWER_COUNT = 'follower_count'
USER_FOLLOWING_COUNT = 'following_count'

# Activity types
ACTIVITY_TYPE_LIKE = 'like'
ACTIVITY_TYPE_COMMENT = 'comment'
ACTIVITY_TYPE_JOURNEY_UPDATE = 'journey_update'

IS_READ_YES = 1
IS_READ_NO = 0