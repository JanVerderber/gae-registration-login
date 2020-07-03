from flask import Flask
from cron.remove_unverified_users import remove_unverified_users_cron
from handlers.admin import users
from handlers.public import main as public_main, auth
from handlers.profile.auth import logout, change_password, change_password_confirmation
from tasks.send_email_task import send_email_via_sendgrid
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

# CHANGE PASSWORD CONFIRMATION
app.add_url_rule(rule="/change-password-confirmation/<code>", endpoint="profile.auth.change_password_confirmation",
                 view_func=change_password_confirmation, methods=["GET", "POST"])

# FORGOT PASSWORD
app.add_url_rule(rule="/forgot-password", endpoint="public.auth.forgot_password", view_func=auth.forgot_password,
                 methods=["GET", "POST"])

# FORGOT PASSWORD CONFIRMATION
app.add_url_rule(rule="/forgot-password-confirmation/<code>", endpoint="public.auth.forgot_password_confirmation",
                 view_func=auth.forgot_password_confirmation, methods=["GET", "POST"])


# CRON JOBS
app.add_url_rule(rule="/cron/remove_unverified_users_cron", view_func=remove_unverified_users_cron, methods=["GET"])


# TASKS
app.add_url_rule(rule="/tasks/send-email", endpoint="tasks.send_email_task.send_email_via_sendgrid",
                 view_func=send_email_via_sendgrid, methods=["POST"])


# FOR RUNNING THE APP

if __name__ == '__main__':
    if is_local():
        app.run(port=8080, host="localhost", debug=True)  # localhost
    else:
        app.run(debug=False)  # production
