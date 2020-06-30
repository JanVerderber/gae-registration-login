import logging
from utils.environment import is_local
from models.settings import Settings
from sendgrid import SendGridAPIClient, Mail


def send_email(email_params):
    if is_local():
        # localhost (not really sending the email)

        logging.warning("***********************")
        logging.warning("You are on localhost, so no e-mail will be sent. This is message:")
        logging.warning(email_params["message_body"])
        logging.warning("+++++++++++++++++++++++")
    else:
        # production (sending the email via SendGrid)

        # SendGrid setup
        sg_api_key = Settings.get_by_name("SendGrid-Mail")
        sg = SendGridAPIClient(api_key=sg_api_key.value)

        # E-mail setup
        sender_email = Settings.get_by_name("APP_EMAIL").value
        recipient = email_params["recipient_email"]
        subject = email_params["message_title"]
        msg_html = email_params["message_html"]

        email_message = Mail(from_email=sender_email, to_emails=recipient, subject=subject,
                             html_content=msg_html)

        try:
            response = sg.send(email_message)
            logging.info(response.status_code)
            logging.info(response.body)
            logging.info(response.headers)
        except Exception as e:
            logging.error(str(e))
