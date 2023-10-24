from datetime import datetime

from fabric.api import run
from fabric.api import task
from fabric.contrib import files
from fabric.operations import get, put


@task
def backup():
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    run(f"tar -cvzf varkite-backup-{ts}.tar.gz /var/kite")
    get(remote_path=f"varkite-backup-{ts}.tar.gz", local_path="backup/")
    run("rm varkite-backup-*.tar.gz")
