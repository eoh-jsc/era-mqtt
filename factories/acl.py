import factory

from init_app import Acl
from init_app import Action
from init_app import Permission
from init_app import db


class AclFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Acl
        sqlalchemy_session = db.session

    username = factory.Faker('user_name')
    ipaddress = factory.Faker('ipv4_private')
    clientid = factory.Faker('uuid4')
    topic = factory.Faker('word')
    permission = factory.Iterator([Permission.allow, Permission.deny])
    action = factory.Iterator([Action.publish, Action.subscribe])
