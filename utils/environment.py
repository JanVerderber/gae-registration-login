from models.settings import Settings


def is_local():
    setting = Settings.get_by_name("PROD_ENV")

    if not setting:
        return True

    if setting.value:
        return False
    else:
        return True
