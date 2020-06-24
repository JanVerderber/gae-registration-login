import os


def is_local():
    if os.getenv('PROD_ENV', '').startswith('production'):
        return False
    else:
        return True
