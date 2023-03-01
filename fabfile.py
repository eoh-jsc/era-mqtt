from fabric2 import task


project_path = "/root/era-mqtt"


@task
def restart_all(c):
    c.run('docker-compose exec -T app supervisorctl status')
    c.run('docker-compose exec -T app supervisorctl reread')
    c.run('docker-compose exec -T app supervisorctl update')
    c.run('docker-compose exec -T app supervisorctl restart all')


@task
def deploy(c):
    print("Starting...")
    with c.cd(project_path):
        c.run("git pull")  # TODO
        restart_all(c)
    print("Success.")