from flask import Flask, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

#  App setup 
app = Flask(__name__)
app.secret_key = b"Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#  Extensions 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import User, Recipe

#  Signup 
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    image_url = data.get("image_url")
    bio = data.get("bio")

    if not username or not password:
        return {"error": "Invalid username or password"}, 422

    user = User(username=username, image_url=image_url, bio=bio)
    user.password_hash = password
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 201


#  Login 
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.authenticate(password):
        return {"error": "Unauthorized"}, 401

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 200


#  Logout 
@app.route("/logout", methods=["DELETE"])
def logout():
    user_id = session.get("user_id")
    if not user_id:
        return {"error": "Unauthorized"}, 401

    session.pop("user_id")
    return {"message": "Logged out"}, 200


#  Check Session 
@app.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")
    if not user_id:
        return {"error": "Unauthorized"}, 401

    user = User.query.get(user_id)
    return jsonify(user.to_dict()), 200


#  Recipe Index 
@app.route("/recipes", methods=["GET", "POST"])
def recipe_index():
    user_id = session.get("user_id")
    if not user_id:
        return {"error": "Unauthorized"}, 401

    if request.method == "GET":
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return jsonify([r.to_dict() for r in recipes]), 200

    # POST
    data = request.get_json()
    title = data.get("title")
    instructions = data.get("instructions")
    minutes_to_complete = data.get("minutes_to_complete")

    try:
        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id,
        )
        db.session.add(recipe)
        db.session.commit()
    except (ValueError, Exception):
        db.session.rollback()
        return {"error": "Invalid recipe"}, 422

    return jsonify(recipe.to_dict()), 201


if __name__ == "__main__":
    app.run(debug=True)
