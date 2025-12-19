from app import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False, default=bcrypt.generate_password_hash("test").decode("utf-8"))
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", backref="user", lazy=True)

    # Write-only password
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password is write-only")

    @password_hash.setter
    def password_hash(self, password_plaintext):
        self._password_hash = bcrypt.generate_password_hash(password_plaintext).decode("utf-8")

    # Authenticate method for tests
    def authenticate(self, password_plaintext):
        return bcrypt.check_password_hash(self._password_hash, password_plaintext)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "image_url": self.image_url,
            "bio": self.bio,
        }


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters")
        return instructions

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "instructions": self.instructions,
            "minutes_to_complete": self.minutes_to_complete,
            "user_id": self.user_id,
        }
