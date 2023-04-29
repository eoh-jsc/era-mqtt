import logging
import sys

from init_app import create_app

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
c = logging.StreamHandler(sys.stdout)
c.setFormatter(formatter)
logger.addHandler(c)

logger.info('Hello world!')  # TODO remove

app = create_app('.env', test=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
