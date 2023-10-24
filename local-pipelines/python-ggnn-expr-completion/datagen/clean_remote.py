import argparse
import logging
import os


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')


def run(cmd: str):
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError(f"running '{cmd}' returned non-zero status: {ret}")


def clean(host: str, directory: str):
    os.system(f"ssh {host} 'killall graph_data_server'")
    run(f"ssh {host} 'rm -rf {directory}/*'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='directory to clean up on each remote machine')
    parser.add_argument('--hosts', nargs='*', type=str, help='list of hosts to deploy to')
    args = parser.parse_args()

    assert len(args.hosts) > 0, "need to clean at least one host"

    for host in args.hosts:
        logging.info(f"cleaning {args.dir} on {host}")
        clean(host, args.dir)


if __name__ == "__main__":
    main()
