FROM python:3.10

USER root

WORKDIR /app

COPY . .

RUN apt-get update -y && \
    apt-get install -y build-essential python3-dev supervisor wget nginx nano curl ufw

RUN wget https://www.emqx.com/en/downloads/broker/5.0.17/emqx-5.0.17-ubuntu20.04-amd64.deb && \
    apt-get install ./emqx-5.0.17-ubuntu20.04-amd64.deb

RUN pip install poetry psycopg2-binary

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
RUN unlink /etc/nginx/sites-enabled/default
# chmod -R 777 /tmp/uwsgi.sock
# service nginx start
# TODO Son

EXPOSE 80
EXPOSE 443
EXPOSE 18083
EXPOSE 1883
EXPOSE 8883
EXPOSE 8083
EXPOSE 8084

CMD ["supervisord", "-c", "supervisor/supervisord.conf"]
