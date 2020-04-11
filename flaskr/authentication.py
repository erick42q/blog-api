import functools
import jwt
import uuid
from flask import (
    Blueprint,
    flash,
    g,
    abort,
    redirect,
    render_template,
    request,
    session,
    jsonify,
    url_for,
    make_response,
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_users():
    db = get_db()
    users = db.execute("SELECT id, username, public_id FROM user").fetchall()

    response = []
    for user in users:
        user_json = {
            "id": str(user["id"]),
            "username": user["username"],
            "public_id": user["public_id"]
        }
        
        response.append(user_json)

    print(response)
    print(users)

    return response


@bp.route("/register", methods=("POST", "GET"))
def register():
    if request.method == "POST":
        username = request.json.get("username")
        password = request.json.get("password")
        db = get_db()

        if not username:
            abort(make_response({"error": "username is required."}, 400))

        elif not password:
            abort(make_response({"error": "password is required."}, 400))

        elif (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            abort(
                make_response(
                    {"error": "User {} is already registered.".format(username)}
                )
            )

        else:
            db.execute(
                "INSERT INTO user (username, password, public_id) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), str(uuid.uuid4())),
            )
            db.commit()

            users = get_users()

            return jsonify(users)


@bp.route("/login", methods=("POST", "GET"))
def login():
    if request.method == "POST":
        auth = request.authorization
        db = get_db()

        if not auth or not auth.username or not auth.password:
            return make_response(
                "could not verify",
                401,
                {"WWW.Authentication": 'Basic realm: "login required"'},
            )

        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (auth["username"],),
        ).fetchone()

        print(user['id'])

        if check_password_hash(user["password"], auth.password):
            pass
            # token = jwt.encode(
            #     {
            #         "public_id": user["public_id"],
            #         # "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            #     },
            #     app.config["SECRET_KEY"],
            # )
            # token = jwt.encode({"public_id": user["public_id"]}, app.config["SECRET_KEY"])

        # username = request.json.get("username")
        # password = request.json.get("password")
        # db = get_db()
        # error = None

        # user = db.execute(
        #     "SELECT * FROM user WHERE username = ?", (username,),
        # ).fetchone()

        # if user is None:
        #     error = "Incorrect username."

        # elif not check_password_hash(user["password"], password):
        #     error = "Incorrect password."

        # if error is None:

        #     pass
        # else:
        #     abort(make_response(error, 404))
