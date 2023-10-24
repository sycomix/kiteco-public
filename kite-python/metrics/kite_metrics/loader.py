from jinja2 import Environment, PackageLoader, select_autoescape
import yaml
import json
import pkg_resources
import os


env = Environment(
    loader=PackageLoader('kite_metrics', 'schemas'),
)

cache = {}

def _schema_exists(filename):
    return pkg_resources.resource_exists('kite_metrics', f'schemas/{filename}')

def _schema_open(filename):
    return pkg_resources.resource_stream('kite_metrics', f'schemas/{filename}')


def load_context(key):
    filename = f'{key}.ctx.yaml'
    if filename not in cache:
        ctx = {}
        if _schema_exists(filename):
            ctx = yaml.load(_schema_open(filename), yaml.FullLoader)
        cache[filename] = ctx
    return cache[filename]


def load_schema(key):
    filename = f'{key}.yaml.tmpl'
    if filename not in cache:
        ctx = load_context(key)
        cache[filename] = yaml.load(env.get_template(filename).render(ctx), Loader=yaml.FullLoader)

    return cache[filename]


def load_json_schema(key, extra_ctx=None):
    filename = f'{key}.schema.json'
    if filename not in cache:
        if _schema_exists(filename):
            cache[filename] = json.load(_schema_open(filename))
        else:
            tmpl_filename = f'{key}.schema.json.tmpl'
            ctx = {'schema': load_schema(key)}
            if extra_ctx:
                ctx.update(extra_ctx)
            rendered = env.get_template(tmpl_filename).render(ctx)
            try:
                cache[filename] = json.loads(rendered)
            except json.decoder.JSONDecodeError:
                print(f"Error decoding schema JSON:\n{rendered}")

    return cache[filename]
