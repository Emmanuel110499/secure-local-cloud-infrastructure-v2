from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from decorators import login_required


auth_bp = Blueprint(
    "auth",
    __name__,
)


def is_safe_redirect(target: str | None) -> bool:
    """Empêche une redirection vers un site extérieur."""

    if not target:
        return False

    parsed = urlparse(target)

    return (
        parsed.scheme == ""
        and parsed.netloc == ""
        and target.startswith("/")
    )


def get_account_service():
    return current_app.extensions[
        "account_service"
    ]


@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():
    if session.get("authenticated"):
        return redirect(
            url_for("dashboard.home")
        )

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        account_service = get_account_service()

        if account_service.authenticate(
            username,
            password,
        ):
            session.clear()
            session["authenticated"] = True
            session["username"] = (
                account_service.get_username()
            )

            next_page = request.args.get("next")

            if is_safe_redirect(next_page):
                return redirect(next_page)

            return redirect(
                url_for("dashboard.home")
            )

        flash(
            "Identifiant ou mot de passe incorrect.",
            "danger",
        )

    return render_template("login.html")


@auth_bp.route(
    "/account",
    methods=["GET", "POST"],
)
@login_required
def account():
    account_service = get_account_service()

    if request.method == "POST":
        action = request.form.get(
            "action",
            "",
        )

        current_password = request.form.get(
            "current_password",
            "",
        )

        if not account_service.verify_password(
            current_password
        ):
            flash(
                "Le mot de passe actuel est incorrect.",
                "danger",
            )

            return redirect(
                url_for("auth.account")
            )

        try:
            if action == "username":
                new_username = request.form.get(
                    "new_username",
                    "",
                ).strip()

                account_service.update_username(
                    new_username
                )

                session["username"] = new_username

                flash(
                    "L’identifiant a été modifié.",
                    "success",
                )

            elif action == "password":
                new_password = request.form.get(
                    "new_password",
                    "",
                )

                confirmation = request.form.get(
                    "confirm_password",
                    "",
                )

                if new_password != confirmation:
                    flash(
                        "Les nouveaux mots de passe "
                        "ne correspondent pas.",
                        "danger",
                    )

                    return redirect(
                        url_for("auth.account")
                    )

                account_service.update_password(
                    new_password
                )

                flash(
                    "Le mot de passe a été modifié.",
                    "success",
                )

            else:
                flash(
                    "Action non reconnue.",
                    "danger",
                )

        except ValueError as error:
            flash(
                str(error),
                "danger",
            )

        return redirect(
            url_for("auth.account")
        )

    return render_template(
        "account.html",
        username=account_service.get_username(),
    )


@auth_bp.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("auth.login")
    )
