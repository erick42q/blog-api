from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    request,
    url_for,
    jsonify,
    abort,
    make_response,
)

from flaskr.db import get_db

# from flaskr.auth import login_required
from flaskr.authentication import token_required

bp = Blueprint("api", __name__, url_prefix="/api/")


@bp.route("/", methods=("GET", "POST"))
def api_list():
    if request.method == "GET":
        db = get_db()
        posts = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()

        response = []
        for post in posts:
            post_json = {
                "id": post["id"],
                "title": post["title"],
                "body": post["body"],
                "created": post["created"].strftime("%Y-%m-%d"),
                "author_id": post["author_id"],
                "username": post["username"],
            }
            response.append(post_json)

        return jsonify(response)


@bp.route("/create-post", methods=("GET", "POST"))
@token_required
def create_post(user, *args, **kwargs):
    if request.method == "POST":

        title = request.json.get("title")
        body = request.json.get("body")

        if not title:
            abort(make_response({"error": "Title is required."}, 400))

        elif not body:
            abort(make_response({"error": "Invalid data request"}, 400))

        else:
            # print(user['id'])
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, user["id"]),
            )
            db.commit()

            return make_response({"report": "post created"}, 201)


def get_post(id, user_id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    # if post["author_id"] != user_id:
    #     abort(403)

    return post


@bp.route("/<int:id>", methods=("GET", "PUT", "DELETE"))
@token_required
def api_detail(user, id, *args, **kwargs):
    if request.method == "GET":

        post = get_post(id, user["id"])
        
        if post is None:
            return make_response("Post id {0} doesn't exist.".format(id) ,404)

        response = {
            "id": post["id"],
            "title": post["title"],
            "body": post["body"],
            "created": post["created"].strftime("%Y-%m-%d"),
            "author_id": post["author_id"],
            "username": post["username"],
        }
        return make_response(response, 200)

    if request.method == "PUT":

        title = request.json.get("title")
        body = request.json.get("body")
        error = None

        if not title:
            title = post["title"]

        if not body:
            body = post["body"]

        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id = ?", (title, body, id)
            )
            db.commit()

            post = get_post(id, user["id"])

            response = {
                "id": post["id"],
                "title": post["title"],
                "body": post["body"],
            }
            return make_response(response, 200)

    if request.method == "DELETE":
        # get_post(id, user["id"])
        db = get_db()
        db.execute("DELETE FROM post WHERE id = ?", (id,))
        db.commit()

        post = get_post(id, user["id"])

        if post is None:
            return make_response("post {} deleted".format(id), 204)

        return make_response("post not {} deleted", 400)
