import pytest
from flask import g, json, session
from flaskr.db import get_db
from base64 import b64encode
from werkzeug.security import check_password_hash, generate_password_hash


def test_register(client, app):
    assert client.get("/auth/register").status_code == 200
    response = client.post("/auth/register", json={"username": "a", "password": "a"})
    client.post("/auth/register", json={"username": "test1", "password": "teste1"})
    client.post("/auth/register", json={"username": "test2", "password": "teste2"})
    client.post("/auth/register", json={"username": "test3", "password": "teste3"})
    # assert "http://localhost/auth/login" == response.headers["Location"]

    with app.app_context():
        assert (
            get_db().execute("select * from user where username = 'a'",).fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", json={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth, app):

    assert client.get,('/auth/login').status_code == 200

    response = auth.login()

    assert b"authorization" in response.data

    
def get_token(auth, username="test", password="teste123"):
    
    response = auth.login()
    data = json.loads(response.data)
    token = data['authorization'].split()[1]

    return token


def test_list_users(client, auth):

    token = get_token(auth)
    user_list = client.post("/auth/users", headers={"authorization": token})
    
    assert user_list.status_code == 200
    # assert b"token is invalid" not in user_list.data


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username or password'),
    ('test', 'a', b'Incorrect username or password'),
    # ('test', 'teste123', b'jwt'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session