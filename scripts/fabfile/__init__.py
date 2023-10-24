import os
import time
import datetime

from fabric.api import env, task, local, hosts, settings
from fabric.operations import run, put, get
from fabric.context_managers import cd, shell_env

env.user = 'ubuntu'
# env.key_filename = '~/.ssh/kite-dev.pem'
env.use_ssh_config = True

GOPATH=os.path.join("/mnt", "godeploy")
KITECO=os.path.join(GOPATH, "src/github.com/kiteco/kiteco")

ARTIFACTS=os.path.join("/mnt/kite", "artifacts")
RELEASES="/var/kite/releases"
LOGDIR="/var/kite/log"

BUILD_TARGETS = {
    "user-node": "github.com/kiteco/kiteco/kite-go/cmds/user-node",
    "user-mux": "github.com/kiteco/kiteco/kite-go/cmds/user-mux",
}

DOCKER_IMAGES = {}

DEPLOY_TARGETS = [
    "user-node",
    "user-mux",
]

@task
def create_release():
    branch = f"release_{_date()}"
    local(f"git checkout -b {branch}")
    local(f"git push -u origin {branch}")

@task
def create_client_release(client):
    branch = f"release_{_date()}_client_{client}"
    local(f"git checkout -b {branch}")
    local(f"git push -u origin {branch}")


@task
@hosts('build.kite.com')
def build_release(branch):
    with shell_env(GOPATH=GOPATH, CGO_LDFLAGS_ALLOW='.*'):
        with cd(KITECO):
            # clear local changes if any
            run("git reset --hard")
            run("git checkout master")
            run("git pull")
            run(f"git checkout {branch}")
            run("git pull")

            run("make install-deps")

            artifacts_path = os.path.join(ARTIFACTS, branch)
            run(f"mkdir -p {artifacts_path}")

            for target, path in BUILD_TARGETS.items():
                run(f'go build -o {os.path.join(artifacts_path, target)} {path}')
                run(
                    f"s3cmd put {os.path.join(artifacts_path, target)} s3://kite-deploys/{branch}/{target}"
                )

            for tar, folder in DOCKER_IMAGES.items():
                with cd(folder):
                    run(f"make save OUTPUT={artifacts_path}/{tar}")
                    run(
                        f"s3cmd put {os.path.join(artifacts_path, tar)} s3://kite-deploys/{branch}/{tar}"
                    )

@task
@hosts('build.kite.com')
def pull_release(branch):
    local(f"mkdir -p {branch}")
    artifacts_path = os.path.join(ARTIFACTS, branch)
    for target in DEPLOY_TARGETS:
        get(remote_path=os.path.join(artifacts_path, target),
            local_path=branch)

@task
def push_release(branch):
    run(f"mkdir -p {os.path.join(RELEASES, branch)}")
    for target in DEPLOY_TARGETS:
        put(local_path=os.path.join(branch, target),
            remote_path=os.path.join(RELEASES, branch),
            mode=0o755)
    local(f"rm -rf {branch}")

@task
def deploy_release(branch):
    current_dir = os.path.join(RELEASES, "current")
    branch_dir = os.path.join(RELEASES, branch)

    run(f"rm -f {current_dir}")
    run(f"ln -s {branch_dir} {current_dir}")

    for target in DEPLOY_TARGETS:
        executable_file = os.path.join(branch_dir, target)
        log_file = os.path.join(LOGDIR, f"{target}.log")

        with settings(warn_only=True):
            run(f"killall {target}")
            time.sleep(5)
        run(f"nohup {executable_file} &> {log_file} &", pty=False)


# Release server tasks --------------------------------------------------

@task
def build_and_deploy_release_server():
    branch = create_release_release()
    build_release_server(branch)
    deploy_release_server(branch)

@task
def create_release_release():
    branch = f"release_server_{_date()}"
    local(f'git checkout -b {branch}')
    local(f'git push -u origin {branch}')
    return branch

@task
@hosts('build.kite.com')
def build_release_server(branch):
    with shell_env(GOPATH=GOPATH, CGO_LDFLAGS_ALLOW='.*'):
        with cd(KITECO):
            run("git fetch")
            run(f"git checkout {branch}")

            run("make install-deps")

            target = 'release'
            go_pkg_path = 'github.com/kiteco/kiteco/kite-go/cmds/release'

            artifacts_dir = os.path.join(ARTIFACTS, branch)
            artifacts_path = os.path.join(artifacts_dir, target)

            run(f"mkdir -p {artifacts_dir}")
            run(f'go build -o {artifacts_path} {go_pkg_path}')
            run(f"s3cmd put {artifacts_path} s3://kite-deploys/{branch}/{target}")

@task
def deploy_release_server(branch):
    current_dir = os.path.join(RELEASES, "current")
    branch_dir = os.path.join(RELEASES, branch)

    run(f'rm -rf {branch_dir}')
    run(f'mkdir {branch_dir}')
    run(f's3cmd get s3://kite-deploys/{branch}/release {branch_dir}')

    run(f'rm -f {current_dir}')
    run(f'ln -s {branch_dir} {current_dir}')

    target = 'release'
    executable_file = os.path.join(branch_dir, target)
    run(f'chmod 755 {executable_file}')
    log_file = os.path.join(LOGDIR, f"{target}.log")

    with settings(warn_only=True):
        run(f'killall {target}')
        time.sleep(5)
    run(f'nohup {executable_file} server &> {log_file} &', pty=False)

@task
def deploy_mock_release_server(branch):
    current_dir = os.path.join(RELEASES, "current")
    branch_dir = os.path.join(RELEASES, branch)

    run(f'rm -rf {branch_dir}')
    run(f'mkdir {branch_dir}')
    run(f's3cmd get s3://kite-deploys/{branch}/release {branch_dir}')

    run(f'rm -f {current_dir}')
    run(f'ln -s {branch_dir} {current_dir}')

    target = 'release'
    executable_file = os.path.join(branch_dir, target)
    run(f'chmod 755 {executable_file}')
    log_file = os.path.join(LOGDIR, f"{target}.log")

    with settings(warn_only=True):
        run(f'killall {target}')
        time.sleep(5)

    run(f'nohup {executable_file} mockserver &> {log_file} &', pty=False)

## --

def _date():
    return datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
