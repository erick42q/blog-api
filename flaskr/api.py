from flask import Blueprint, flash, g, redirect, request, url_for, jsonify, abort, make_response
from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint("api", __name__)


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


@bp.route("/", methods=("GET", "POST"))
def index():
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

    # elif request.method == "POST":

    #     title = request.json.get("title")
    #     body = request.json.get("body")
    #     error = None

    #     if not title or not body:    
    #         abort(make_response({"error": "Invalid data request"}, 400))

    #     response = {
    #         "title": title,
    #         "body": body,
    #         "status": "response received"
    #     }
    #     return make_response(response, 201)

        
