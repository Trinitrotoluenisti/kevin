from sqlalchemy.exc import OperationalError
from datetime import datetime
from json import dump as json_dump
from os import mkdir

from . import app, db, logging
from .passwords import hash_password


# Initialize the databases
class User(db.Model):
    __tablename__ = "users"

    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    perms = db.Column("perms", db.SmallInteger, default=0)

    username = db.Column("username", db.String, unique=True, nullable=False)
    password = db.Column("password", db.String, nullable=False)
    email = db.Column("email", db.String, unique=True, nullable=False)
    public_email = db.Column("public_email", db.Boolean, default=False)

    name = db.Column("name", db.String, nullable=False)
    surname = db.Column("surname", db.String, nullable=False)
    bio = db.Column("bio", db.String, default="")

    written_posts = db.relationship("Post", foreign_keys='Post.author_id', backref='author')
    approved_posts = db.relationship("Post", foreign_keys='Post.approver_id', backref='approver')

    def save(self):
        """
        Save the user in the database
        """

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check(username, password):
        """
        Check if there is an user with the
        given username and if the password
        is right.

        If there are no registered users with
        that username, raises a ValueError (There
        are no registered users with that username);

        if the password is wrong, raises another ValueError
        (Wrong password);

        if it's all correct, return the user
        """

        password = hash_password(password)
        user = User.from_username(username)

        if not user or not user.password == password:
            return False

        return True

    @staticmethod
    def from_username(username):
        return User.query.filter_by(username=username).first()

    def json(self):
        """
        Return the user in json format
        """

        return {
                "id": self.id,
                "perms": self.perms,

                "username": self.username,
                "email": self.email,
                "isEmailPublic": self.public_email,

                "name": self.name,
                "surname": self.surname,
                "bio": self.bio
                }

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    datetime = db.Column("datetime", db.DateTime)
    tags = db.Column("tags", db.String)

    def __init__(self, author, title, content, tags=''):
        """
        Initialize a post
        """

        self.datetime = datetime.now().replace(microsecond=0)
        self.title = title
        self.content = content
        self.likes = {"count": 0, "list": []}
        self.dislikes = {"count": 0, "list": []}
        super().__init__(author=author, datetime=self.datetime, tags=tags)

    def save(self):
        """
        Save the post in the database
        """

        # save in the database
        db.session.add(self)
        db.session.commit()

        # prepare the file
        json_file = {}
        json_file["title"] = self.title
        json_file["content"] = self.content
        json_file["likes"] = self.likes
        json_file["dislikes"] = self.dislikes

        # write it
        with open(f"{app.config['DATABASE_PATH']}/posts/{self.id}.json", 'w') as f:
            json_dump(json_file, f)

    def json(self):
        """
        Return the post in json format
        """

        return {
                "id": self.id,
                "author": self.author.json,
                "approver": self.approver_id,
                "title": self.title,
                "content": self.content,
                "datetime": str(self.datetime),
                "tags": self.tags.split(';'),
                "likes": self.likes,
                "dislikes": self.dislikes
               }

class RevokedTokens(db.Model):
    __tablename__ = "revoked_tokens"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    jti = db.Column("jti", db.Integer, unique=True, nullable=False)
    exp = db.Column("exp", db.Integer, nullable=True)

    def save(self):
        """
        Save the token in the database
        """

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def clean():
        """
        Clean the blacklist
        """

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
