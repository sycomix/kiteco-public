from typing import Dict

import argparse
import logging
import math
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s')

# TODO: Perhaps use fabric?


def run(cmd: str):
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError(f"running '{cmd}' returned non-zero status: {ret}")


def make_bundle(bundle: str, meta_info: str, kite_ml_path: str, env_vars: Dict[str, str]):
    run(f"rm -rf {bundle} && mkdir {bundle}")

    with open(f"{bundle}/env.sh", 'w') as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    run(
        f"go build -o {bundle}/graph_data_server github.com/kiteco/kiteco/kite-go/lang/python/cmds/graph-data-server"
    )
    run(f"cp -v {meta_info} {bundle}/metainfo.json")
    run(f"mkdir {bundle}/kite_ml")
    run(f"cp -v {kite_ml_path}/requirements.txt {bundle}/kite_ml")
    run(f"cp -rv {kite_ml_path}/kite {bundle}/kite_ml")
    run(f"cp -v datagen/get_data.py {bundle}")
    run(f"cp -v datagen/run.sh {bundle}")
    run(f"cp -v datagen/start.sh {bundle}")

    bundle_file = f"{bundle}.tar.gz"
    run(f"tar czvf {bundle_file} {bundle}")


def deploy_to_host(bundle: str, host: str, random_seed: int):
    run(f"scp {bundle}.tar.gz {host}:.")
    run(
        f"ssh {host} 'rm -rf {bundle} && tar xzf {bundle}.tar.gz && cd {bundle} && RANDOM_SEED={random_seed} ./start.sh'"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=str, help='bundle name')
    parser.add_argument('--steps', type=int, help='total number of training steps we expect to run')
    parser.add_argument('--batch', type=int, default=10, help='batch size')
    parser.add_argument('--meta_info', type=str, help='path to meta_info')
    parser.add_argument('--max_samples', type=int)
    parser.add_argument('--attr_base_proportion', type=float)
    parser.add_argument('--attr_proportion', type=float)
    parser.add_argument('--call_proportion', type=float)
    parser.add_argument('--arg_type_proportion', type=float)
    parser.add_argument('--kwarg_name_proportion', type=float)
    parser.add_argument('--arg_placeholder_proportion', type=float)
    parser.add_argument('--samples_per_file', type=int, default=500)
    parser.add_argument('--kite_ml_path', type=str, help='path to Kite ML')
    parser.add_argument('--out_dir', type=str, help='output directory that each instance will write to locally')
    parser.add_argument('--hosts', nargs='*', type=str, help='list of hosts to deploy to')
    args = parser.parse_args()

    assert len(args.hosts) > 0, "need to deploy to at least one host"

    logging.info(f"deploying to {len(args.hosts)} hosts:")
    for host in args.hosts:
        logging.info(f"* {host}")

    # continue to generate samples until we are killed to account for some
    # instances producing samples at different rates
    samples_per_host = args.steps
    env_vars = {
        'SAMPLES': samples_per_host,
        'OUT_DIR': args.out_dir,
        'BATCH': args.batch,
        'MAX_SAMPLES': args.max_samples,
        'ATTR_PROPORTION': args.attr_proportion,
        'ATTR_BASE_PROPORTION': args.attr_base_proportion,
        'CALL_PROPORTION': args.call_proportion,
        'ARG_TYPE_PROPORTION': args.arg_type_proportion,
        'KWARG_NAME_PROPORTION': args.kwarg_name_proportion,
        'ARG_PLACEHOLDER_PROPORTION': args.arg_placeholder_proportion,
        'SAMPLES_PER_FILE': args.samples_per_file,
        'KITE_AZUREUTIL_STORAGE_KEY': 'XXXXXXX',
        'KITE_AZUREUTIL_STORAGE_NAME': 'kites3mirror',
        'KITE_USE_AZURE_MIRROR': '1',
    }

    make_bundle(args.bundle, args.meta_info, args.kite_ml_path, env_vars)

    for i, host in enumerate(args.hosts):
        logging.info(f"deploying {args.bundle}.tar.gz to {host}")
        random_seed = i + 1
        deploy_to_host(args.bundle, host, random_seed)


if __name__ == "__main__":
    main()
