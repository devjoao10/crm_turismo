from fastapi import Request
from fastapi.responses import RedirectResponse


def get_current_user(request: Request):

    user = request.session.get("user")

    if not user:
        raise Exception("not_logged")

    return user