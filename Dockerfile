FROM laughlamz/emqx-datadog

USER root

RUN apt-get update -y
RUN apt-get install -y python3.10 python3-pip python3-dev

RUN pip install -U pip poetry && \
    poetry config virtualenvs.create false

ADD poetry.lock pyproject.toml ./
RUN poetry install

WORKDIR /app
COPY . .

RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
RUN unlink /etc/nginx/sites-enabled/default

RUN touch /var/log/supervisor/supervisord.log && \
    mkdir /var/log/uwsgi

RUN chmod -R 777 /var/log/nginx/access.log && \
    chmod -R 777 /var/log/nginx/error.log && \
    chmod -R 777 /var/log/supervisor/supervisord.log

# docs 8001:5000
EXPOSE 80
EXPOSE 443
EXPOSE 18083
EXPOSE 18084
EXPOSE 1883
EXPOSE 8883
EXPOSE 8083
EXPOSE 8084
EXPOSE 5000

CMD ["/bin/bash", "entrypoint.sh"]
