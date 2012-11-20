from fabric.api import local, sudo
from fabric.decorators import task, hosts

@task
def build():
    local("go build sonicadrone.go")
    local("strip -s sonicadrone")

@task
def run():    
    local("go run sonicadrone.go")    


@task
def clean():
    local("rm -rf upload ready")
    local("rm sonicadrone")

@task
@hosts('rif@avocadosoft.ro:22011')
def deploy():
    build()
    sudo('supervisorctl stop sonicadrone')
    local('scp sonicadrone avocado:')
    sudo('supervisorctl start sonicadrone')
    clean()

@task
@hosts('rif@avocadosoft.ro:22011')
def logs():
    sudo("tail -f /var/log/supervisor/sonicadrone-stdout---supervisor-lUXEcG.log")
