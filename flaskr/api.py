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
from flaskr.auth import login_required

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

    elif request.method == "POST":

        title = request.json.get("title")
        body = request.json.get("body")

        if not title:
            abort(make_response({"error": "Title is required."}, 400))

        elif not body:
            abort(make_response({"error": "Invalid data request"}, 400))

        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, 
                body, 
                g.user["id"]),
            )
            db.commit()

            return make_response({"report": "post created"}, 201)


def get_post(id, check_author=True):
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

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>", methods=("GET", "PUT", "DELETE"))
def api_detail(id):
    if request.method == "GET":
        post = get_post(id)

        print(post["id"])
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

            post = get_post(id)

            response = {
                "id": post["id"],
                "title": post["title"],
                "body": post["body"],
            }
            return make_response(response, 200)

    if request.method == "DELETE":
        get_post(id)
        db = get_db()
        db.execute("DELETE FROM post WHERE id = ?", (id,))
        db.commit()
        return make_response(jsonify({"report": "post {} deleted".format(id)}), 204)
