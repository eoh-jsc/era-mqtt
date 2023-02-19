FROM python:3.10-slim-buster

WORKDIR /app

COPY . .

RUN apt-get update -y && \
    apt-get install build-essential python3-dev -y

RUN pip install poetry psycopg2-binary

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .

EXPOSE 5000

#CMD ["poetry", "run", "python", "app.py"]
CMD ["poetry", "run", "uwsgi", "--ini", "./uwsgi/config.ini"]
