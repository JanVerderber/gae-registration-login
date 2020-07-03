import os
from models.settings import Settings
from flask import request, render_template, url_for
from utils.task_helper import run_background_task


def send_email(recipient_email, email_template, email_params, email_subject, non_html_message, sender_email=None):
    if not sender_email:
        if Settings.get_by_name("APP_EMAIL"):
            sender_email = Settings.get_by_name("APP_EMAIL").value  # reads from settings
        else:
            sender_email = "info@your.webapp"

    # send web app URL data by default to email template
    email_params["app_root_url"] = request.url_root

    # render the email HTML body
    email_body = render_template(email_template, **email_params)

    # params sent to the background task
    payload = {"recipient_email": recipient_email, "email_subject": email_subject, "sender_email": sender_email,
               "email_body": email_body, "non_html_message": non_html_message}

    run_background_task(relative_path=url_for("tasks.send_email_task.send_email_via_sendgrid"),
                        payload=payload, queue="email", project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                        location="europe-west1")
