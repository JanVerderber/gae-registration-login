from google.cloud import ndb
from models import get_db


client = get_db()


class Settings(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.StringProperty()

    # retrieves a setting by name
    @classmethod
    def get_by_name(cls, name):
        with client.context():
            setting = cls.query(cls.name == name).get()

            return setting
