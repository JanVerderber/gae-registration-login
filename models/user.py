import bleach
import secrets
import datetime
import hashlib
import bcrypt
from operator import attrgetter
from google.cloud import ndb
from models import get_db
from flask import request
from utils.email_helper import send_email


client = get_db()


class Session(ndb.Model):
    token_hash = ndb.StringProperty()
    ip = ndb.StringProperty()
    platform = ndb.StringProperty()
    browser = ndb.StringProperty()
    country = ndb.StringProperty()
    user_agent = ndb.StringProperty()
    expired = ndb.DateTimeProperty()


class CSRFToken(ndb.Model):
    token = ndb.StringProperty()
    expired = ndb.DateTimeProperty()


class User(ndb.Model):
    email = ndb.StringProperty()
    verification_code = ndb.StringProperty()
    verification_code_expiration = ndb.DateTimeProperty()
    password = ndb.StringProperty()

    # connection with other two classes
    sessions = ndb.StructuredProperty(Session, repeated=True)
    csrf_tokens = ndb.StructuredProperty(CSRFToken, repeated=True)

    # HANDLER METHODS:
    # grouped by meaning

    # USERS:
    # creates a new user
    @classmethod
    def create(cls, email, password):
        with client.context():
            # sanitize email
            email = bleach.clean(email, strip=True)

            # checks if user with this email already exists
            user = cls.query(cls.email == email).get()

            if not user:  # if user does not yet exist, create one
                if password:
                    # use bcrypt to hash the password
                    hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
                    password_hash = hashed.decode('utf8')

                    # create the user object and store it into Datastore
                    user = cls(email=email, password=password_hash)
                    user.put()

                    return True, user, "Success"  # success, user, message
            else:
                return False, user, "User with this email address is already registered. Please go to the " \
                                    "Login page and try to log in."

    # updates user password
    @classmethod
    def update_password(cls, user, new_password):
        with client.context():
            if user and new_password:
                # use bcrypt to hash the new password
                hashed = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt())
                password_hash = hashed.decode('utf8')

                # set new password
                user.password = password_hash
                user.put()

                return True, "Successfully changed password"
            else:
                return False, "Unknown error"

    # CSRF TOKENS:
    # generates CSRF token
    @classmethod
    def generate_csrf_token(cls, user):
        with client.context():
            valid_tokens = []
            for csrf in user.csrf_tokens:
                if csrf.expired > datetime.datetime.now():
                    valid_tokens.append(csrf)

            # there should be maximum 10 CSRF tokens per user and not more, check and delete oldest one
            if len(valid_tokens) >= 10:
                oldest_token = min(valid_tokens, key=attrgetter("expired"))
                valid_tokens.remove(oldest_token)

            # generate csrf token and save it to CSRF table
            csrf_token = secrets.token_hex()

            csrf_object = CSRFToken(token=csrf_token, expired=(datetime.datetime.now() + datetime.timedelta(hours=3)))
            valid_tokens.append(csrf_object)

            # finally, store the new tokens list back in the user model
            user.csrf_tokens = valid_tokens
            user.put()

            return csrf_token

    # validates CSRF token
    @classmethod
    def validate_csrf_token(cls, user, csrf_token):
        with client.context():
            token_validity = False

            unused_tokens = []
            for csrf in user.csrf_tokens:  # loop through user's CSRF tokens
                if csrf.token == csrf_token:  # if tokens match, set validity to True
                    token_validity = True
                else:
                    unused_tokens.append(csrf)  # if not, add CSRF token to the unused_tokens list

            if unused_tokens != user.csrf_tokens:
                user.csrf_tokens = unused_tokens
                user.put()

            return token_validity

    # SESSIONS:
    # generates a new session
    @classmethod
    def generate_session(cls, user):
        with client.context():
            if user:
                # generate session token and its hash
                token = secrets.token_hex()
                token_hash = hashlib.sha256(str.encode(token)).hexdigest()

                session = Session(token_hash=token_hash, expired=datetime.datetime.now() + datetime.timedelta(days=30))
                if request:  # this separation is needed for tests which don't have the access to "request" variable
                    session.ip = request.access_route[-1]
                    session.platform = request.user_agent.platform
                    session.browser = request.user_agent.browser
                    session.user_agent = request.user_agent.string
                    session.country = request.headers.get("X-AppEngine-Country")

                if not user.sessions:
                    user.sessions = [session]
                else:
                    valid_sessions = [session]
                    for item in user.sessions:  # loop through sessions and remove the expired ones
                        if item.expired > datetime.datetime.now():
                            valid_sessions.append(item)

                    user.sessions = valid_sessions  # now only non-expired sessions are stored in the User object

                user.put()

                return token

    # verifies a session by session token
    @classmethod
    def verify_session(cls, session_token=None):
        with client.context():
            if session_token:
                token_hash = hashlib.sha256(str.encode(session_token)).hexdigest()

                user = cls.query(cls.sessions.token_hash == token_hash).get()

                if not user:
                    return False, None, "A user with this session token does not exist. Try to log in again."

                # important: you can't check for expiration in the cls.query() above, because it wouldn't only check the
                # expiration date of the session in question, but any expiration date which could give a false result
                for session in user.sessions:
                    if session.token_hash == token_hash:
                        if session.expired > datetime.datetime.now():
                            return True, user, "Success"

                return False, None, "Unknown error."
            else:
                return False, None, "Please login to access this page."

    # deletes session
    @classmethod
    def delete_session(cls, user, session_token):
        with client.context():
            cookie_token_hash = hashlib.sha256(str.encode(session_token)).hexdigest()

            valid_sessions = []
            for session in user.sessions:
                # delete session that has the same session token than browser's session cookie
                # (delete by not including in the new sessions list)
                if session.token_hash != cookie_token_hash:
                    valid_sessions.append(session)

            user.sessions = valid_sessions
            user.put()

        return True

    # VERIFICATION CODES:
    # generates and sends verification code
    @classmethod
    def send_verification_code(cls, user):
        with client.context():
            if user:
                # generate verification code
                code = secrets.token_hex()

                # store it in user
                user.verification_code = hashlib.sha256(str.encode(code)).hexdigest()
                user.verification_code_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
                user.put()

                url = request.url_root
                complete_url = url + "email-verification/" + code

                message_title = "Verify e-mail address - Moderately simple registration login"

                message_body = "Thank you for registering at our web app! Please verify your e-mail by " \
                               "clicking on the link below:\n" \
                               + complete_url + "\n"

                message_html = "<p>Thank you for registering at our web app! Please verify your e-mail by " \
                               "clicking on the link below:<br> " \
                               + "<a href='" + complete_url + "' target='_blank'>" + complete_url + "</a></p>"

                send_email(email_params={"recipient_email": user.email, "message_title": message_title,
                                         "message_body": message_body, "message_html": message_html})

                return True

    # verifies verification code
    @classmethod
    def verify_verification_code(cls, code):
        with client.context():
            if code:
                # verify verification code
                code_hash = hashlib.sha256(str.encode(code)).hexdigest()

                user = cls.query(cls.verification_code == code_hash).get()

                if not user:
                    return False, "That verification code is not valid."

                if user.verification_code_expiration > datetime.datetime.now():
                    user.verification_code = ""
                    user.verification_code_expiration = datetime.datetime.min
                    user.put()

                    url = request.url_root

                    message_title = "E-mail address confirmed - Moderately simple registration login"

                    message_body = "Your e-mail has been confirmed! Thank you, you can now login with " \
                                   "the link below:\n" + url + "\n"

                    message_html = "<p>Your e-mail has been confirmed! Thank you, you can now login " \
                                   "with the link below:" \
                                   "<br><a href='" + url + "' target='_blank'>" + url + "</a></p>"

                    send_email(email_params={"recipient_email": user.email, "message_title": message_title,
                                             "message_body": message_body, "message_html": message_html})

                    return True, "Success"
                else:
                    return False, "That verification code is not valid."

    # RETRIEVE DATA:
    # gets ID from itself
    @property
    def get_id(self):
        return self.key.id()

    # retrieves user by email
    @classmethod
    def get_user_by_email(cls, email):
        with client.context():
            user = cls.query(cls.email == email).get()

            return user

    # retrieves ALL verified users
    @classmethod
    def fetch(cls, verification_code=""):
        with client.context():
            users = cls.query(cls.verification_code == verification_code).fetch()

            return users
