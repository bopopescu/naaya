from functools import wraps
from django.shortcuts import render, redirect

from tach.settings import HOSTNAME

def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user:
            login_page = "/login/login_form?disable_cookie_login__=1&came_from=%s" % HOSTNAME
            return redirect(login_page)
        return func(*args, **kwargs)
    return wrapper


def auth_details_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.country:
            return redirect('overview')
        return func(*args, **kwargs)
    return wrapper


