from fabric2 import task


@task
def deploy(c):
    print("Starting deploy...")
    with c.cd("/root/era-mqtt"):
        c.run("git pull")
        c.run('docker-compose exec -T app supervisorctl status')
        c.run('docker-compose exec -T app supervisorctl reread')
        c.run('docker-compose exec -T app supervisorctl update')
        c.run('docker-compose exec -T app supervisorctl restart uwsgi')
    print("Done.")
