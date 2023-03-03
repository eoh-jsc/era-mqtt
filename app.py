from flask.cli import load_dotenv
from init_app import create_app

load_dotenv('.env')
app = create_app(db_path='postgresql://root:password@postgres/emqx', test=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
