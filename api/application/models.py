from sqlalchemy.exc import OperationalError
from datetime import datetime
from os import mkdir
from re import search

from . import app, db
from .errors import APIErrors
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
        db.session.add(self)
        db.session.commit()

    def check(self, password=True):
        """
        Check if an user is valid
        """

        # Username (5 < lenght <= 20; chars in A-Z, a-z, 0-9, "_")
        if len(self.username) < 5:
            raise APIErrors[241]
        elif len(self.username) > 20:
            raise APIErrors[242]
        elif not all(ord(c) in (*range(48, 58), *range(65, 91), 95, *range(97, 123)) for c in self.username):
            raise APIErrors[243]

        # Password (8 < lenght <= 35; chars in ascii table)
        elif password and len(self.password) < 8:
            raise APIErrors[251]
        elif password and len(self.password) > 35:
            raise APIErrors[252]
        elif password and not all(ord(c) in range(33, 127) for c in self.password):
            raise APIErrors[253]

        # Email
        elif not search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', self.email):
            raise APIErrors[261]

        # isEmailPublic (in True, False)
        elif not (self.public_email in (True, False)):
            raise APIErrors[263]

        # Name (2 < length <= 15)
        elif len(self.name) < 2:
            raise APIErrors[271]
        elif len(self.name) > 15:
            raise APIErrors[272]

        # Surname (2 < length <= 15)
        elif len(self.surname) < 2:
            raise APIErrors[281]
        elif len(self.surname) > 15:
            raise APIErrors[282]

        # Bio (length <= 200)
        elif len(self.bio) > 200:
            raise APIErrors[291]


class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column("name", db.String, nullable=False, unique=True)

    def json(self):
        return {"id": self.id, "name": self.name}

    def save(self):
        db.session.add(self)
        db.session.commit()

    def check(self):
        """
        Check if a community is valid.
        """

        # Name (5 < lenght <= 20; chars in A-Z, a-z, 0-9, "_")
        if len(self.name) < 5:
            raise APIErrors[331]
        elif len(self.name) > 20:
            raise APIErrors[332]
        elif not all(ord(c) in (*range(48, 58), *range(65, 91), 95, *range(97, 123)) for c in self.name):
            raise APIErrors[333]


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
        now = datetime.now().timestamp()

        # Delete all the expired tokens
        RevokedTokens.query.filter(RevokedTokens.exp and RevokedTokens.exp <= now).delete()
        db.session.commit()


try:
    mkdir(app.config['DATABASE_PATH'])
except FileExistsError:
    pass

# Delete the revoked tokens' table if exists
try:
    RevokedTokens.__table__.drop(db.engine)
except OperationalError:
    pass

# create the db if it doesn't exist
db.create_all()
