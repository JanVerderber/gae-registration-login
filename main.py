from flask import Flask
from handlers.public import main as public_main
from utils.environment import is_local


app = Flask(__name__)

# PUBLIC URLS

# HOME PAGE (LOGIN)
app.add_url_rule(rule="/", endpoint="public.main.login", view_func=public_main.login, methods=["GET", "POST"])

if __name__ == '__main__':
    if is_local():
        app.run(port=8080, host="localhost", debug=True)  # localhost
    else:
        app.run(debug=False)  # production
