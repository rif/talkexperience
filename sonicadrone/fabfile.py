from fabric.api import local, sudo, run
from fabric.decorators import task, hosts
from fabric.context_managers import lcd

@task
def build():
    local("go build sonicadrone.go")
    local("strip -s sonicadrone")

@task
def start():    
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
@hosts('dc9d2c9d2ffc45c38b7a4e8d320a6ce9@drone-talkexperience.rhcloud.com')
def log():
    run('tail -f diy-0.1/logs/sonicadrone.log')

