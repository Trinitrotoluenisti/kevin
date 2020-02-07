from . import app

from flask_sqlalchemy import SQLAlchemy


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
    email = db.Column("email", db.String, unique=True, nullable=False)
    password = db.Column("password", db.String, nullable=False)
    perms = db.Column("perms", db.Integer)

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
                "email": self.email,
                "password": self.password,
                "perms": self.perms
                }

# Create the database
db.create_all()
