import bcrypt
import logging
from flask import request, render_template, redirect, url_for
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


def forgot_password(**params):
    if request.method == "GET":
        token = request.cookies.get('my-simple-app-session')
        success, user, message = User.verify_session(token)

        if success:
            params["current_user"] = user
            return render_template("public/auth/logged_in.html", **params)
        else:
            return render_template("public/auth/forgot_password.html", **params)

    elif request.method == "POST":
        email = request.form.get("email")

        if email:
            user = User.get_user_by_email(email)

            if user:
                success = User.forgot_password_code(user)

                if success:
                    return render_template("public/auth/forgot_password_confirmation.html", **params)
            else:
                params["error_message"] = "No user found with this e-mail."
                return render_template("public/auth/error_page.html", **params)


def forgot_password_confirmation(code, **params):
    if request.method == "GET":
        token = request.cookies.get('my-simple-app-session')
        success, user, message = User.verify_session(token)

        if success:
            params["current_user"] = user
            return render_template("public/auth/logged_in.html", **params)
        else:
            success, user, message = User.forgot_password_code_confirmation(code)

            if success:
                params["current_user"] = user
                return render_template("public/auth/forgot_password_form.html", **params)
            else:
                params["error_message"] = message
                return render_template("public/auth/error_page.html", **params)

    elif request.method == "POST":
        current_email = request.form.get("user_email")
        new_password = request.form.get("new_password")

        if current_email and new_password:
            # checks if user with this e-mail and password exists
            user = User.get_user_by_email(current_email)

            if user:
                if bcrypt.checkpw(new_password.encode("utf-8"), user.password.encode("utf-8")):
                    params["current_user"] = user
                    params["danger_message"] = "New password can not be the same as old one, please try again."
                    return render_template("public/auth/forgot_password_form.html", **params)
                else:
                    # hash the new password
                    hashed = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt())
                    new_password_hash = hashed.decode('utf8')

                    update_success, update_message = User.update_password(user, new_password_hash)

                    if update_success:
                        # delete all sessions from this user
                        User.delete_all_user_sessions(user)

                        # send e-mail that password was changed
                        User.forgot_password_success(user)

                        login_message = "Your password has been changed, please login again."
                        return redirect(url_for("public.main.login", info_message=login_message))
                    else:
                        params["error_message"] = update_message
                        return render_template("public/auth/error_page.html", **params)
            else:
                params["error_message"] = "No user found with this e-mail, please try again."
                return render_template("public/auth/error_page.html", **params)
