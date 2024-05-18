import flask
from flask import request, jsonify
from flask.views import MethodView

from models import User, Ad, Session

app = flask.Flask('app')

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

def get_add(ad_id:int):
    ad = request.session.query(Ad).get(ad_id)
    return ad

class UserView(MethodView):

    def post(self):
        user_data = request.json
        user = User(**user_data)
        add_db_obj(user)
        return jsonify(user.dict)

class AdView(MethodView):

    def get(self, ad_id: int):
        ad = get_add(ad_id)
        return jsonify(ad.dict)

    def post(self):
        ad_data = request.json
        ad = Ad(**ad_data)
        add_db_obj(ad)
        return jsonify(ad.dict)

    def delete(self, ad_id: int):
        ad = get_add(ad_id)
        request.session.delete(ad)
        request.session.commit()
        return jsonify({"status": "deleted"})

user_view = UserView.as_view('user')
ad_view = AdView.as_view('ad')

app.add_url_rule("/user/", methods=["POST"], view_func=user_view)
app.add_url_rule("/ads/", methods=["POST"], view_func=ad_view)
app.add_url_rule("/ads/<int:ad_id>/", methods=["GET", "DELETE"], view_func=ad_view)


app.run(port=8080)


