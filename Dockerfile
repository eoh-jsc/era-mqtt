FROM laughlamz/emqx-datadog

USER root

WORKDIR /app

COPY . .

RUN apt-get update -y
RUN apt-get install -y python3.10 python3-pip python3-dev

RUN pip install poetry

RUN poetry config virtualenvs.create false && \
    poetry install --without dev

RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
RUN unlink /etc/nginx/sites-enabled/default

RUN mkdir /var/log/supervisor/supervisord.log && \
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
