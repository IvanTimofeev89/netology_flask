from typing import Union

import flask
from flask import jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy import select

from errors import AuthenticationError, HttpError
from models import Ad, Session, User

app = flask.Flask("app")
bcrypt = Bcrypt(app)


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response: flask.Response):
    request.session.close()
    return response


def add_db_obj(obj):
    request.session.add(obj)
    request.session.commit()
    return obj


@app.errorhandler(HttpError)
@app.errorhandler(AuthenticationError)
def error_handler(err: Union[HttpError, AuthenticationError]):
    json_response = jsonify({"status": "error", "message": err.message})
    json_response.status_code = err.status_code
    return json_response


def get_add(ad_id: int):
    ad = request.session.query(Ad).get(ad_id)
    if ad is None:
        raise HttpError(status_code=404, message="Ad doesn't exist")
    return ad


def hash_password(password: str) -> str:
    password = password.encode()
    password = bcrypt.generate_password_hash(password)
    password = password.decode()
    return password


def check_password(hashed_password: str, password: str) -> bool:
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.check_password_hash(hashed_password, password)


def is_authorizated_user(request: flask.Request):
    headers = request.headers
    user_email = headers.get("email")
    user_password = headers.get("password")
    user = request.session.scalars(select(User).where(User.email == user_email)).first()
    if user and check_password(user.password, user_password):
        return user.id
    raise AuthenticationError(
        status_code=404, message="User not found or invalid email/password"
    )


def is_owner(ad, user_id: int):
    if ad.owner_id != user_id:
        raise AuthenticationError(status_code=409, message="Only owner can remove ad")


class UserView(MethodView):

    def post(self):
        user_data = request.json
        user_data["password"] = hash_password(user_data["password"])
        user = User(**user_data)
        add_db_obj(user)
        return jsonify(user.dict)


class AdView(MethodView):

    def get(self, ad_id: int):
        ad = get_add(ad_id)
        return jsonify(ad.dict)

    def post(self):
        user_id = is_authorizated_user(request)
        if user_id:
            ad_data = request.json
            ad_data["owner_id"] = user_id
            ad = Ad(**ad_data)
            add_db_obj(ad)
            return jsonify(ad.dict)

    def delete(self, ad_id: int):
        ad = get_add(ad_id)
        user_id = is_authorizated_user(request)
        is_owner(ad, user_id)
        request.session.delete(ad)
        request.session.commit()
        return jsonify({"status": "deleted"})


user_view = UserView.as_view("user")
ad_view = AdView.as_view("ad")

app.add_url_rule("/user/", methods=["POST"], view_func=user_view)
app.add_url_rule("/ads/", methods=["POST"], view_func=ad_view)
app.add_url_rule("/ads/<int:ad_id>/", methods=["GET", "DELETE"], view_func=ad_view)

app.run(port=8080)
