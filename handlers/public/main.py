from flask import request, render_template


def login(**params):
    if request.method == "GET":
        return render_template('public/main/index.html', **params)
