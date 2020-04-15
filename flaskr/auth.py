from functools import wraps
import jwt
import uuid
import datetime
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
    current_app,
)
from werkzeug.security import check_password_hash, generate_password_hash
import flaskr
from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        db = get_db()
        if "authorization" in request.headers:
            token = request.headers["authorization"]

        if not token:
            return make_response(jsonify({"message": "a valid token is missing"}), 400)

        try:

            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=['HS256'])
            current_user = db.execute(
                "SELECT * FROM user WHERE public_id = ?", (data["public_id"],)
            ).fetchone()
            # print(current_user["username"])
            return f(current_user, *args, **kwargs)

            # current_user = Users.query.filter_by(public_id=data["public_id"]).first()
        except:
            return make_response(jsonify({"message": "token is invalid"}), 400)


    return decorator

def get_users():
    db = get_db()
    users = db.execute("SELECT id, username, public_id FROM user").fetchall()

    response = []
    for user in users:
        user_json = {
            "id": str(user["id"]),
            "username": user["username"],
            "public_id": user["public_id"],
        }

        response.append(user_json)

    return response


@bp.route("/users", methods=("POST", "GET"))
@token_required
def users(*args, **kwargs):
    users = get_users()
    return make_response(jsonify(users), 200)

@bp.route("/register", methods=("POST", "GET"))
def register():
    if request.method == "POST":
        body = request.get_json()
        username = body['username']
        password = body['password']
        db = get_db()

        print(username)
        if not username:
            abort(make_response({"error": "Username is required."}, 400))

        elif not password:
            abort(make_response({"error": "Password is required."}, 400))
        elif (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            abort(
                make_response(
                    {"error": "already registered"}
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
    
    else:
        return make_response("invalid request", 200)


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

        if user == None or not check_password_hash(user["password"], auth.password):
            return make_response({"error": "Incorrect username or password"})

        if check_password_hash(user["password"], auth.password):
            token = jwt.encode(
                {
                    "public_id": user["public_id"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
                },
                current_app.config["SECRET_KEY"],
            )

            return make_response(
                {"authorization": "jwt {}".format(token.decode("utf8"))}
            )
    else:
        return make_response("invalid request", 200)