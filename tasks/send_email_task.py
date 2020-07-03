import json
import logging
from flask import request
from sendgrid import SendGridAPIClient, Mail
from models.settings import Settings
from utils.environment import is_local


def send_email_via_sendgrid():
    """A background task that sends an email via SendGrid."""
    data = json.loads(request.get_data(as_text=True))

    recipient_email = data.get("recipient_email")
    sender_email = data.get("sender_email")
    email_subject = data.get("email_subject")
    email_body = data.get("email_body")
    non_html_message = data.get("non_html_message")

    if is_local():
        # localhost (not really sending the email)

        logging.warning("***********************")
        logging.warning("You are on localhost, so no e-mail will be sent. This is message:")
        logging.warning("Recipient: " + recipient_email)
        logging.warning("Sender: " + sender_email)
        logging.warning("Subject: " + email_subject)
        logging.warning("Body: " + non_html_message)
        logging.warning("+++++++++++++++++++++++")

        return "{sender_email} {email_subject}".format(sender_email=sender_email, email_subject=email_subject)
    else:
        # production (sending the email via SendGrid)
        if request.headers.get("X-AppEngine-QueueName"):
            # If the request has this header (X-AppEngine-QueueName), then it really came from Google Cloud Tasks.
            # Third-party requests that contain headers started with X are stripped of these headers once they hit GAE
            # servers. That's why no one can fake these headers.

            # SendGrid setup
            sg_api_key = Settings.get_by_name("SendGrid-Mail")
            sg = SendGridAPIClient(api_key=sg_api_key.value)

            # Set up email message
            email_message = Mail(from_email=sender_email, to_emails=recipient_email, subject=email_subject,
                                 html_content=email_body)

            try:
                response = sg.send(email_message)
                logging.info(response.status_code)
                logging.info(response.body)
                logging.info(response.headers)
            except Exception as e:
                logging.error(str(e))

        return "true"
