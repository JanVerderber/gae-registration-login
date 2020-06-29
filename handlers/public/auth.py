from flask import request, render_template
from models.user import User


def registration(**params):
    if request.method == "GET":
        token = request.cookies.get('my-simple-app-session')
        success, user, message = User.verify_session(token)

        if success:
            params["current_user"] = user
            return render_template("public/auth/logged_in.html", **params)
        else:
            return render_template("public/auth/registration.html", **params)

    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            success, user, message = User.create(email=email, password=password)

            if success:
                send_success = User.send_verification_code(user)

                if send_success:
                    return render_template("public/auth/verify_email.html", **params)
            else:
                params["error_message"] = message
                return render_template("public/auth/error_page.html", **params)


def email_verification(code, **params):
    if request.method == "GET":
        token = request.cookies.get('my-simple-app-session')
        success, user, message = User.verify_session(token)

        if success:
            params["current_user"] = user
            return render_template("public/auth/logged_in.html", **params)
        else:
            verify_success, verify_message = User.verify_verification_code(code)

            if verify_success:
                return render_template("public/auth/registration_success.html", **params)
            else:
                params["error_message"] = verify_message
                return render_template("public/auth/error_page.html", **params)
