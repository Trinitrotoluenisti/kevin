from sqlalchemy.exc import OperationalError
from datetime import datetime
from os import mkdir
from re import search

from . import app, db
from .passwords import hash_password



class User(db.Model):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    perms = db.Column("perms", db.SmallInteger)
    username = db.Column("username", db.String, unique=True, nullable=False)
    email = db.Column("email", db.String, unique=True, nullable=False)
    public_email = db.Column("public_email", db.Boolean)
    password = db.Column("password", db.String, nullable=False)
    name = db.Column("name", db.String, nullable=False)
    surname = db.Column("surname", db.String, nullable=False)
    bio = db.Column("bio", db.String)

    def json(self):
        return {"id": self.id, "perms": self.perms, "username": self.username, "email": self.email, "isEmailPublic": self.public_email, "name": self.name, "surname": self.surname, "bio": self.bio}

    def save(self):
        # Hash password
        old_password = self.password
        self.password = hash_password(self.password)

        # Save user in the db
        db.session.add(self)
        db.session.commit()

        # "unhash" password
        self.password = old_password

    def check(self):
        """
        Check if the user fields are valid. if they aren't, it returns the reason,
        otherwise returns None.
        """

        # Username (5 < lenght <= 20; chars in A-Z, a-z, 0-9, "_")
        if len(self.username) < 5:
            return "Username too short"
        elif len(self.username) > 20:
            return "Username too long"
        elif not all(ord(c) in (*range(48, 58), *range(65, 91), 95, *range(97, 123)) for c in self.username):
            return "Username contains invalid character(s)"

        # Password (8 < lenght <= 35; chars in ascii table)
        elif len(self.password) < 8:
            return "Password too short"
        elif len(self.password) > 35:
            return "Password too long"
        elif not all(ord(c) in range(33, 127) for c in self.password):
            return "Password contains invalid character(s)"

        # Email
        elif not search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', self.email):
            return "Email is not an email"

        # isEmailPublic (in True, False)
        elif not (self.public_email in (True, False)):
            print(self.public_email, type(self.public_email))
            return "isEmailPublic is not a bool"

        # Name (2 < length <= 15)
        elif len(self.name) < 2:
            return "Name too short"
        elif len(self.name) > 15:
            return "Name too long"

        # Surname (2 < length <= 15)
        elif len(self.surname) < 2:
            return "Surname too short"
        elif len(self.surname) > 15:
            return "Surname too long"

        # Bio (length <= 50)
        elif len(self.bio) > 50:
            return "Bio too long"


class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column("name", db.String, nullable=False, unique=True)

    def json(self):
        return {"id": self.id, "name": self.name}

    def save(self):
        db.session.add(self)
        db.session.commit()


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    author_id = db.Column("author_id", db.Integer, nullable=False)
    title = db.Column("title", db.String)
    content = db.Column("content", db.String, nullable=False)
    datetime = db.Column("datetime", db.DateTime, nullable=False)
    community_id = db.Column("community_id", db.Integer, nullable=False)

    def json(self):
        return {"id": self.id, "authorId": self.author_id, "title": self.title, "content": self.content, "datetime": self.datetime, "communityId": self.community_id}

    def save(self):
        db.session.add(self)
        db.session.commit()


class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    value = db.Column("value", db.Integer, nullable=False)
    user_id = db.Column("user_id", db.Integer, nullable=False)
    post_id = db.Column("post_id", db.Integer, nullable=False)

    def json(self):
        return {"id": self.id, "value": self.value, "userId": self.user_id, "postId": self.post_id}

    def save(self):
        db.session.add(self)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = "follows"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    follower_id = db.Column("follower_id", db.Integer, nullable=False)
    user_id = db.Column("user_id", db.Integer)
    community_id = db.Column("community_id", db.Integer)

    def json(self):
        return {"id": self.id, "followerId": self.follower_id, "userId": self.user_id, "communityId": self.community_id}

    def save(self):
        db.session.add(self)
        db.session.commit()


class RevokedTokens(db.Model):
    __tablename__ = "revoked_tokens"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    jti = db.Column("jti", db.Integer, unique=True, nullable=False)
    exp = db.Column("exp", db.Integer, nullable=True)

    def json(self):
        return {"id": self.id , "jti": self.jti, "exp": self.exp}

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def clean():
        # Fetch current informations
        number = len(RevokedTokens.query.all())
        now = datetime.now().timestamp()

        # Delete all the expired tokens
        RevokedTokens.query.filter(RevokedTokens.exp and RevokedTokens.exp <= now).delete()
        db.session.commit()


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
