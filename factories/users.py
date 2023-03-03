import factory

from init_app import Users
from init_app import db


class UsersFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Users
        sqlalchemy_session = db.session

    username = factory.Sequence(lambda n: f"user_{n}")
    password_hash = factory.Faker("password")
    salt = factory.Faker("word")
    is_superuser = False
    # time_created = factory.Faker("date_time_this_decade")
