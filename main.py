from flask import Flask
from handlers.admin import users
from handlers.public import main as public_main, auth
from handlers.profile.auth import logout, change_password
from utils.environment import is_local


app = Flask(__name__)

# PUBLIC URLS

# HOME PAGE (LOGIN)
app.add_url_rule(rule="/", endpoint="public.main.login", view_func=public_main.login, methods=["GET", "POST"])

# REGISTRATION
app.add_url_rule(rule="/registration", endpoint="public.auth.registration", view_func=auth.registration,
                 methods=["GET", "POST"])

# EMAIL VERIFICATION
app.add_url_rule(rule="/email-verification/<code>", endpoint="public.auth.email_verification",
                 view_func=auth.email_verification, methods=["GET"])


# PRIVATE URLS (NEED TO BE LOGGED IN)

# USERS LIST
app.add_url_rule(rule="/admin/users", endpoint="admin.users.users_list", view_func=users.users_list, methods=["GET"])

# LOG OUT
app.add_url_rule(rule="/logout", endpoint="profile.auth.logout", view_func=logout, methods=["POST"])

# CHANGE USER PASSWORD
app.add_url_rule(rule="/change-password", endpoint="profile.auth.change_password", view_func=change_password,
                 methods=["GET", "POST"])


# FOR RUNNING THE APP

if __name__ == '__main__':
    if is_local():
        app.run(port=8080, host="localhost", debug=True)  # localhost
    else:
        app.run(debug=False)  # production
