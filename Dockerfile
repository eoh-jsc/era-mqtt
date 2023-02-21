FROM python:3.10

WORKDIR /app

COPY . .

RUN apt-get update -y && \
    apt-get install -y build-essential python3-dev supervisor wget

RUN wget https://www.emqx.com/en/downloads/broker/5.0.17/emqx-5.0.17-ubuntu20.04-amd64.deb && \
    apt-get install ./emqx-5.0.17-ubuntu20.04-amd64.deb

RUN pip install poetry psycopg2-binary

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .

EXPOSE 5000
EXPOSE 1883
EXPOSE 8083
EXPOSE 8084
EXPOSE 18083

CMD ["supervisord", "-c", "supervisor/supervisord.conf"]
#CMD ["poetry", "run", "python", "app.py"]
