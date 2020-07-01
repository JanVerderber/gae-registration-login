from flask import request

from models.user import User
from utils.environment import is_local


def remove_unverified_users_cron():
    # only run this cron if it was called by the GAE Cron Service (header X-AppEngine-Cron) or if it's on
    # localhost (tests)
    if request.headers.get("X-AppEngine-Cron") or is_local():
        User.remove_unverified_users()
        return "Success"
