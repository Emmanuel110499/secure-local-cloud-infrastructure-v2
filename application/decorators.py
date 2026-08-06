from functools import wraps

from flask import redirect, request, session, url_for


def login_required(view):
    """Protège une route nécessitant une authentification."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(
                url_for(
                    "auth.login",
                    next=request.path,
                )
            )

        return view(*args, **kwargs)

    return wrapped_view