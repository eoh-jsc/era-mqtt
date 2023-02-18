from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@postgres/emqx'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.username


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/create_user")
def create_user():
    user = Users(username='john')
    db.session.add(user)
    db.session.commit()
    return "User created!"


@app.route("/list_user")
def list_user():
    users = Users.query.all()
    print('xxx', users)
    return str(users)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
