from sqlalchemy.exc import OperationalError
from datetime import datetime
from os import mkdir

from . import app, db, logging
from .passwords import hash_password



class User(db.Model):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    perms = db.Column("perms", db.SmallInteger, default=0)
    username = db.Column("username", db.String, unique=True, nullable=False)
    email = db.Column("email", db.String, unique=True, nullable=False)
    public_email = db.Column("public_email", db.Boolean, default=False)
    password = db.Column("password", db.String, nullable=False)
    name = db.Column("name", db.String, nullable=False)
    surname = db.Column("surname", db.String, nullable=False)
    bio = db.Column("bio", db.String, default="")

    def json(self):
        return {"id": self.id, "perms": self.perms, "username": self.username, "email": self.email, "isEmailPublic": self.public_email, "name": self.name, "surname": self.surname, "bio": self.bio}


class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column("name", db.String, nullable=False, unique=True)

    def json(self):
        return {"id": self.id, "name": self.name}


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    author_id = db.Column("author_id", db.Integer, nullable=False)
    approver_id = db.Column("approver_id", db.Integer)
    title = db.Column("title", db.String)
    content = db.Column("content", db.String, nullable=False)
    datetime = db.Column("datetime", db.DateTime)
    community_id = db.Column("community_id", db.Integer, nullable=False)

    def json(self):
        return {"id": self.id, "authorId": self.author_id, "approverId": self.approver_id, "title": self.title, "content": self.content, "datetime": self.datetime, "communityId": self.community_id}


class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    value = db.Column("value", db.Integer, nullable=False)
    user_id = db.Column("user_id", db.Integer, nullable=False)
    post_id = db.Column("post_id", db.Integer, nullable=False)

    def json(self):
        return {"id": self.id, "value": self.value, "userId": self.user_id, "postId": self.post_id}


class Follow(db.Model):
    __tablename__ = "follows"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    follower_id = db.Column("follower_id", db.Integer, nullable=False)
    user_id = db.Column("user_id", db.Integer)
    community_id = db.Column("community_id", db.Integer)

    def json(self):
        return {"id": self.id, "followerId": self.follower_id, "userId": self.user_id, "communityId": self.community_id}


class RevokedTokens(db.Model):
    __tablename__ = "revoked_tokens"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    jti = db.Column("jti", db.Integer, unique=True, nullable=False)
    exp = db.Column("exp", db.Integer, nullable=True)

    def json(self):
        return {"id": self.id , "jti": self.jti, "exp": self.exp}

    @staticmethod
    def clean():
        # Fetch current informations
        number = len(RevokedTokens.query.all())
        now = datetime.now().timestamp()

        # Delete all the expired tokens
        RevokedTokens.query.filter(RevokedTokens.exp and RevokedTokens.exp <= now).delete()
        db.session.commit()

        # Calculate how many have been deleted and log it
        number -= len(RevokedTokens.query.all())
        logging.debug(f"Cleaned tokens' blacklist ({number} tokens deleted)")


try:
    mkdir(app.config['DATABASE_PATH'])
except FileExistsError:
    pass

try:
    mkdir(app.config['DATABASE_PATH'] + '/posts')
except FileExistsError:
    pass

# Delete the revoked tokens' table if exists
try:
    RevokedTokens.__table__.drop(db.engine)
except OperationalError:
    pass

# create the db if it doesn't exist
db.create_all()
