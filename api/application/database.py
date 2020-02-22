from . import app, logging

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Initialize the databases
db = SQLAlchemy(app)


def hash_password(password):
    """
    Returns an hashed version of the password
    """

    return password


class User(db.Model):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    username = db.Column("username", db.String, unique=True, nullable=False)
    name = db.Column("name", db.String, nullable=False)
    surname = db.Column("surname", db.String, nullable=False)
    email = db.Column("email", db.String, unique=True, nullable=False)
    password = db.Column("password", db.String, nullable=False)
    perms = db.Column("perms", db.Integer)

    def save(self):
        """
        Save the user in the database
        """

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def list():
        """
        Return the list of users
        """

        return User.query.all()

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

        user = User.query.filter_by(username=username).first()

        if not user:
            raise ValueError("There are no registered users with that username")

        if not user.password == password:
            raise ValueError("Wrong password")

        return user

    @property
    def json(self):
        """
        Return the user in json format
        """

        return {
                "id": self.id,
                "username": self.username,
                "name": self.name,
                "surname": self.surname,
                "email": self.email,
                "password": self.password,
                "perms": self.perms
                }

class RevokedTokens(db.Model):
    __tablename__ = "revoked_tokens"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True, unique=True)
    jti = db.Column("jti", db.Integer, unique=True, nullable=False)
    exp = db.Column("exp", db.Integer, nullable=False)

    def save(self):
        """
        Save the token in the database
        """

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def list():
        """
        Return the list of users
        """

        return list(map(repr, RevokedTokens.query.all()))

    @staticmethod
    def clean():
        """
        Clean the blacklist
        """

        # Fetch current informations
        number = len(RevokedTokens.query.all())
        now = datetime.now().timestamp()

        # Delete all the expired tokens
        RevokedTokens.query.filter(RevokedTokens.exp <= now).delete()
        db.session.commit()

        # Calculate how many have been deleted and log it
        number -= len(RevokedTokens.query.all())
        logging.debug(f"Cleaned tokens' blacklist ({number} tokens deleted)")


# Delete the revoked tokens' table if exists
try:
    RevokedTokens.__table__.drop(db.engine)
except:
    pass

# create the db if it doesn't exist
db.create_all()
