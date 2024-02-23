FROM ubuntu:22.04

USER root

WORKDIR /app

COPY . .

RUN apt-get update -y && \
    apt-get install -y build-essential git python3.10 python3-pip python3-dev supervisor wget nginx nano curl zsh

RUN python3 --version

RUN chsh -s $(which zsh) && \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" && \
    echo "export PS1=\"(Docker)\$PS1\"" >> /root/.zshrc

RUN mkdir /usr/lib/emqx && mkdir /usr/lib/emqx/data
RUN chmod -R 777 /usr/lib/emqx/data

RUN wget https://www.emqx.com/en/downloads/broker/5.5.0/emqx-5.5.0-ubuntu22.04-amd64.deb && \
    apt-get install ./emqx-5.5.0-ubuntu22.04-amd64.deb

RUN pip install poetry psycopg2-binary
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    mkdir /var/log/uwsgi

RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
RUN unlink /etc/nginx/sites-enabled/default

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
