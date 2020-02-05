from . import app

from flask_sqlalchemy import SQLAlchemy


# Initialize the databases
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, autoincrement=True, primary_key=True)
    username = db.Column("username", db.String, unique=True, nullable=False)
    email = db.Column("email", db.String, unique=True, nullable=False)
    password = db.Column("password", db.String, nullable=False)

    @staticmethod
    def list():
        """
        Return the list of users
        """

        return Controller.query.all()

    @property
    def json(self):
        """
        Return the user in json format
        """

        return {"id": self.id,
                "username": self.username,
                "email": self.email,
                "password": self.password
                }

# Create the database
db.create_all()
