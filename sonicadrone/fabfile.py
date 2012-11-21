from fabric.api import local, sudo
from fabric.decorators import task, hosts
from fabric.context_managers import lcd

@task
def build():
    local("go build sonicadrone.go")
    local("strip -s sonicadrone")

@task
def run():    
    local("go run sonicadrone.go")    

@task
def fake():    
    local("go run fakedrone.go")  

@task
def clean():
    local("rm -rf upload ready")
    local("rm sonicadrone")

@task
def deploy():
    build()
    DEST = '~/Documents/webframeworks/openshift/drone'
    local('rsync sonicadrone %s/diy/sonicadrone' % DEST)
    with lcd(DEST):
        local('pwd')
        local('git add .')
        local('git ci -m "new version"')
        local('git push')    
    clean()

@task
@hosts('rif@avocadosoft.ro:22011')
def logs():
    sudo("tail -f /var/log/supervisor/sonicadrone-stdout---supervisor-lUXEcG.log")
