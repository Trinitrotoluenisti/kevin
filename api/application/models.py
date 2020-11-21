from re import search
from os import mkdir
from datetime import datetime
from sqlalchemy.exc import OperationalError

from . import app, db
from .errors import APIErrors



class User(db.Model):
    """
    A person that is registered in the kevin's database.

    - username (str): that thing that starts with @
    - email (str): the email that the user used to register
    - public_email (bool): if True, anyone can see user's email
    - password (str): that thing used to login
    - name (str): the user's first name
    - surname (str): the user's surname
    - bio (str): the user's bio
    - perms (int): indicates the authorizations that the user has (0 => common user; 1 => moderator; 2 => admin)
    """

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
        """
        Returns the user as a dict
        """

        return {"id": self.id,
                "perms": self.perms,
                "username": self.username,
                "email": self.email,
                "isEmailPublic": self.public_email,
                "name": self.name,
                "surname": self.surname,
                "bio": self.bio}

    def save(self):
        """
        Saves the user in the database
        """

        db.session.add(self)
        db.session.commit()

    def check(self, password=True):
        """
        Checks if an user is valid, otherwise raise an APIError.

        - password (bool): if True, it checks also user's password.
                           If the password is already hashed, it must be set to False.
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
    """
    A place where users write posts.

    - id (int): community's unique id
    - name (str): the name of the community
    """

    __tablename__ = "communities"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column("name", db.String, nullable=False, unique=True)

    def json(self):
        """
        Returns the community as a dict.
        """

        return {"id": self.id, "name": self.name}

    def save(self):
        """
        Saves the community in the database.
        """

        db.session.add(self)
        db.session.commit()

    def check(self):
        """
        Checks if a community is valid, otherwise raises an APIError.
        """

        # Name (5 < lenght <= 20; chars in A-Z, a-z, 0-9, "_")
        if len(self.name) < 5:
            raise APIErrors[331]
        elif len(self.name) > 20:
            raise APIErrors[332]
        elif not all(ord(c) in (*range(48, 58), *range(65, 91), 95, *range(97, 123)) for c in self.name):
            raise APIErrors[333]

class Post(db.Model):
    """
    A thing written by an user in a community.

    - id (int): post's unique identifier
    - author_id (int): the id of the user who wrote the post
    - community_id (int): the id of the community where the post has been published
    - title (str): the title of the post
    - content (str): the content of the post
    - timestamp (datetime.datetime): the time at which the post has been published
    """

    __tablename__ = "posts"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    author_id = db.Column("author_id", db.Integer, nullable=False)
    community_id = db.Column("community_id", db.Integer, nullable=False)
    title = db.Column("title", db.String)
    content = db.Column("content", db.String, nullable=False)
    timestamp = db.Column("timestamp", db.DateTime, nullable=False)

    def json(self):
        """
        Returns the post as a dict.
        """

        return {"id": self.id,
                "authorId": self.author_id,
                "communityId": self.community_id,
                "title": self.title,
                "content": self.content,
                "timestamp": self.timestamp}

    def save(self):
        """
        Saves the post in the database.
        """

        db.session.add(self)
        db.session.commit()

class Like(db.Model):
    """
    A like or a dislike left on a post.

    - value (int): +1 for like and -1 for dislike
    - user_id (int): the id of the user who put the like
    - post_id (int): the id of the post where the like has been left
    """

    __tablename__ = "likes"
    user_id = db.Column("user_id", db.Integer, primary_key=True, unique=False, nullable=False)
    post_id = db.Column("post_id", db.Integer, nullable=False)
    value = db.Column("value", db.Integer, nullable=False)

    def json(self):
        """
        Returns the like as a dict.
        """

        return {"value": self.value, "userId": self.user_id, "postId": self.post_id}

    def save(self):
        """
        Saves the like in the database.
        """

        db.session.add(self)
        db.session.commit()

class Follow(db.Model):
    """
    When an user follows another user or a community.

    - follower_id (int): the id of the user who followed an user/community
    - user_id (int): the id of the followed user (0 if a community has been followed)
    - community_id (int): the id of the followed community (0 if an user has been followed)
    """

    __tablename__ = "follows"
    follower_id = db.Column("follower_id", db.Integer,  primary_key=True, unique=False)
    user_id = db.Column("user_id", db.Integer)
    community_id = db.Column("community_id", db.Integer)

    def json(self):
        """
        Returns the follow as a dict.
        """

        return {"followerId": self.follower_id, "userId": self.user_id, "communityId": self.community_id}

    def save(self):
        """
        Saves the follow in the db.
        """

        db.session.add(self)
        db.session.commit()

class RevokedTokens(db.Model):
    """
    A token that has been revoked by the user.

    - jti (str): the unique token's id
    - exp (int): the timestamp at which the token will expire
    """

    __tablename__ = "revoked_tokens"
    jti = db.Column("jti", db.String, primary_key=True)
    exp = db.Column("exp", db.Integer)

    def json(self):
        """
        Returns the token as a dict.
        """

        return {"jti": self.jti, "exp": self.exp}

    def save(self):
        """
        Saves the token in the database.
        """

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def clean():
        """
        Removes from the database all the tokens revoked by
        the user that has also been expired.
        """

        # Fetch current informations
        now = datetime.now().timestamp()

        # Delete all the expired tokens
        RevokedTokens.query.filter(RevokedTokens.exp and RevokedTokens.exp <= now).delete()
        db.session.commit()


# Create the database path if it doesn't exist
try:
    mkdir(app.config['DATABASE_PATH'])
except FileExistsError:
    pass

# Delete the revoked tokens' table if exists
try:
    RevokedTokens.__table__.drop(db.engine)
except OperationalError:
    pass

# Create the db if it doesn't exist
db.create_all()
