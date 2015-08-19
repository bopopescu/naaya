from fabric.api import *
from fabric.api import env
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo': 'https://github.com/eaudeweb/naaya.buildout.chm-eu.git',
    'bundle_repo':
        'https://github.com/eaudeweb/naaya.bundles.NaayaBundles-CHMEU.git',
}


env.hosts = ['zope@puma.eea.europa.eu']

app['repo'] = ppath('/var/local/chm/buildout')

app.update({
    'buildout_var': app['repo']/'src/buildout-chm-eu',
    'bundle_var': app['repo']/'src/NaayaBundles-CHMEU',
})


@task
def ssh():
    open_shell("cd '%(repo)s'" % app)


def _git_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.git'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("git clone '%s' buildout-chm-eu" % origin_url)

    elif update:
        with cd(repo_path):
            run("git pull")


@task
def _update_repos():
    _git_repo(app['buildout_var'], app['buildout_repo'], update=True)
    _git_repo(app['bundle_var'], app['bundle_repo'], update=True)


@task
def restart_puma():
    run("%(repo)s/bin/buildout -c %(repo)s/buildout.cfg" % app)
    run("%(repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-0 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 start" % app)


@task
def update_puma():
    execute('_update_repos')
    execute('restart_puma')


@task
def shutdown_puma():
    run("%(repo)s/bin/poundctl stop" % app)
    run("%(repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zeo-server stop" % app)


@task
def start_puma():
    run("%(repo)s/bin/zeo-server start" % app)
    run("%(repo)s/bin/zope-instance-0 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/poundctl start" % app)
