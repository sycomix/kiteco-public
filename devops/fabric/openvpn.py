from datetime import datetime
from fabric.api import run
from fabric.api import task
from fabric.contrib import files
from fabric.operations import get, put
from fabric.state import env

# OpenVPN commands

_cmd_prefix = "sudo docker run -v /srv/openvpn:/etc/openvpn %s"
_azure_vpn_ip = "XXXXXXX"

@task
def initialize():
    host = "vpn-azure.kite.com" if env.host == _azure_vpn_ip else "vpn.kite.com"
    opts = f"--rm XXXXXXX/openvpn ovpn_genconfig -u udp://{host}:XXXXXXX"
    run(_cmd_prefix % opts)
    run(_cmd_prefix % "--rm -it XXXXXXX/openvpn ovpn_initpki")

@task
def start():
    run(_cmd_prefix % "-d -p XXXXXXX:XXXXXXX/udp --privileged XXXXXXX/openvpn")


def _get_id():
    return run("sudo docker ps | grep openvpn | awk '{print $1}'")

@task
def stop():
    container_id = _get_id()
    run(f"sudo docker stop {container_id}")

@task
def restart():
    container_id = _get_id()
    run(f"sudo docker restart {container_id}")

@task
def new_client(username):
    opts = f"--rm -it XXXXXXX/openvpn easyrsa build-client-full {username}"
    run(_cmd_prefix % opts)

@task
def revoke_client(username):
    opts = f"--rm -it XXXXXXX/openvpn easyrsa revoke {username}"
    run(_cmd_prefix % opts)

    opts = "--rm -it XXXXXXX/openvpn easyrsa gen-crl"
    run(_cmd_prefix % opts)

@task
def get_client_config(username):
    provider = "azure" if env.host == _azure_vpn_ip else "aws"
    opts = f"--rm XXXXXXX/openvpn ovpn_getclient {username} > {username}.ovpn"
    run(_cmd_prefix % opts)

    # Hack to make sure redirect-gateway line is gone.
    run(
        f"sed -n '/redirect-gateway/!p' {username}.ovpn > {username}-kite-vpn-{provider}.ovpn"
    )
    get(remote_path=f"{username}-kite-vpn-{provider}.ovpn")
    run("rm *.ovpn")

@task
def backup():
    provider = "azure" if env.host == _azure_vpn_ip else "aws"
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    run(f"sudo tar -cvzf openvpn-backup-{provider}-{ts}.tar.gz /srv/openvpn")
    get(remote_path=f"openvpn-backup-{provider}-{ts}.tar.gz", local_path="backup/")
    run("rm openvpn-backup-*.tar.gz")
